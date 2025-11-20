import asyncio
import httpx
import threading
from contextlib import asynccontextmanager
from decouple import config
from app.core.ocr_processor import process_ocr
from app.core.logger import setup_logger

logger = setup_logger(__name__)

# Queue with max size to prevent memory overflow
MAX_QUEUE_SIZE = config("MAX_QUEUE_SIZE", cast=int, default=1000)
task_queue = asyncio.Queue(maxsize=MAX_QUEUE_SIZE)
queue_list = []
queue_list_lock = threading.Lock()

# Metrics
processed_count = 0
failed_count = 0
metrics_lock = threading.Lock()

async def queue_task_check(data) -> bool:
    with queue_list_lock:
        for item in queue_list:
            if str(item.report_id) == str(data.report_id):
                item.s3_url = data.s3_url
                logger.info(f"⚠ Report id:{data.report_id} already in queue, updated s3_url")
                return True
        return False

async def queue_add(data):
    # Check if queue is full
    if task_queue.qsize() >= MAX_QUEUE_SIZE:
        logger.error(f"❌ Queue full! Rejecting report {data.report_id}")
        raise Exception("Queue is full. Please try again later.")
    
    with queue_list_lock:
        queue_list.append(data)
        waiting = task_queue.qsize()
        logger.info(f"✓ Added report id:{data.report_id} | Queue: {len(queue_list)} tracked, {waiting} waiting")

async def queue_clear():
    global queue_list
    with queue_list_lock:
        count = len(queue_list)
        queue_list.clear()
        logger.info(f"✓ Cleared {count} items from queue_list")
        return count

def get_queue_list():
    """Get current queue_list - thread-safe copy"""
    with queue_list_lock:
        return list(queue_list)

async def queue_done(data, success: bool = True):
    global queue_list, processed_count, failed_count
    with queue_list_lock:
        before_count = len(queue_list)
        queue_list = [item for item in queue_list if str(item.report_id) != str(data.report_id)]
        after_count = len(queue_list)
        waiting = task_queue.qsize()
        logger.info(f"✓ [Queue] Removed report {data.report_id} | Remaining: {after_count} tracked, {waiting} waiting")
    
    with metrics_lock:
        if success:
            processed_count += 1
        else:
            failed_count += 1

async def ocr_worker(worker_id: int):
    while True:
        data = await task_queue.get()
        try:
            logger.info(f"⚙ [Worker-{worker_id}] Processing report {data.report_id}")
            
            result = await asyncio.to_thread(process_ocr, data.s3_url)
            
            # Determine environment and get appropriate URL/key
            env = getattr(data, 'environment', 'staging').lower()
            if env == 'production':
                api_url = config("LARAVEL_API_URL_PRODUCTION", default=config("LARAVEL_API_URL", default="http://localhost:8003"))
                api_key = config("LARAVEL_API_KEY_PRODUCTION", default=config("LARAVEL_API_KEY", default=""))
            else:
                api_url = config("LARAVEL_API_URL_STAGING", default=config("LARAVEL_API_URL", default="http://localhost:8003"))
                api_key = config("LARAVEL_API_KEY_STAGING", default=config("LARAVEL_API_KEY", default=""))
            
            api_url = api_url + "/api/ocr/result"
            
            payload = {
                "report_id": data.report_id,
                "user_id": data.user_id,
                "img_url": data.s3_url,
                "raw_ocr": result["raw_ocr"],
                "extracted_data": result["extracted_data"],
                'app_class': result["app_class"],
                "processing_time_ms": result["processing_time_ms"]
            }
            
            headers = {
                "x-api-key": api_key
            }

            logger.info(f"📤 [Worker-{worker_id}] Sending to {env.upper()} webhook: {api_url}")
            logger.info(f"📦 [Worker-{worker_id}] Payload: report_id={data.report_id}, user_id={data.user_id}, app_class={result['app_class']}")
            
            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.post(api_url, json=payload, headers=headers)
                    logger.info(f"✅ Webhook response: {response.status_code} - {response.text[:200]}")
                    
                    if response.status_code == 200:
                        logger.info(f"✓ [Worker-{worker_id}] Successfully sent OCR result for report {data.report_id}")
                    else:
                        logger.warning(f"⚠ [Worker-{worker_id}] Webhook returned non-200 status: {response.status_code}")
                        
            except (httpx.ConnectError, httpx.TimeoutException) as e:
                logger.error(f"🔌 [Worker-{worker_id}] Webhook failed: {e}")
                # Don't raise - continue processing
            except Exception as e:
                logger.error(f"❌ [Worker-{worker_id}] Unexpected webhook error: {e}")
                # Don't raise - continue processing

            logger.info(f"✓ [Worker-{worker_id}] Completed OCR for report {data.report_id}")
            await queue_done(data, success=True)
        except Exception as e:
            logger.error(f"✘ [Worker-{worker_id}] Error: {e}")
            await queue_done(data, success=False)
        finally:
            task_queue.task_done()

@asynccontextmanager
async def lifespan(app):
    global queue_list
    queue_list.clear()
    workers = []
    worker_count = config("WORKER_COUNT", cast=int, default=3)
    logger.info(f"🚀 Starting {worker_count} OCR workers...")
    for i in range(worker_count):
        workers.append(asyncio.create_task(ocr_worker(i+1)))
    yield
    for worker in workers:
        worker.cancel()
