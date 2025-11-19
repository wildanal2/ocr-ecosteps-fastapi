import asyncio
import httpx
from contextlib import asynccontextmanager
from decouple import config
from app.core.ocr_processor import process_ocr
from app.core.logger import setup_logger

logger = setup_logger(__name__)

task_queue = asyncio.Queue()
queue_list = []
queue_lock = asyncio.Lock()

async def queue_task_check(data) -> bool:
    async with queue_lock:
        for item in queue_list:
            if str(item.report_id) == str(data.report_id):
                item.s3_url = data.s3_url
                logger.info(f"⚠ Report id:{data.report_id} already in queue, updated s3_url")
                return True
        return False

async def queue_add(data):
    async with queue_lock:
        queue_list.append(data)
        waiting = task_queue.qsize()
        logger.info(f"✓ Added report id:{data.report_id} | Queue: {len(queue_list)} tracked, {waiting} waiting")

async def queue_clear():
    global queue_list
    async with queue_lock:
        count = len(queue_list)
        queue_list.clear()
        logger.info(f"✓ Cleared {count} items from queue_list")
        return count

def get_queue_list():
    """Get current queue_list - ensures we get the actual global reference"""
    global queue_list
    return queue_list

async def queue_done(data):
    global queue_list
    async with queue_lock:
        before_count = len(queue_list)
        queue_list = [item for item in queue_list if str(item.report_id) != str(data.report_id)]
        after_count = len(queue_list)
        waiting = task_queue.qsize()
        logger.info(f"✓ [Queue] Removed report {data.report_id} | Remaining: {after_count} tracked, {waiting} waiting")

async def ocr_worker(worker_id: int):
    while True:
        data = await task_queue.get()
        try:
            logger.info(f"⚙ [Worker-{worker_id}] Processing report {data.report_id}")
            
            result = await asyncio.to_thread(process_ocr, data.s3_url)
            
            api_url = config("LARAVEL_API_URL", default="http://localhost:8003") + "/api/ocr/result"
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
                "x-api-key": config("LARAVEL_API_KEY", default="")
            }

            logger.info(f"📤 [Worker-{worker_id}] Sending OCR result to webhook: {api_url}")
            logger.info(f"📦 [Worker-{worker_id}] Payload: report_id={data.report_id}, user_id={data.user_id}, app_class={result['app_class']}")
            
            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.post(api_url, json=payload, headers=headers)
                    logger.info(f"✅ Webhook response: {response.status_code} - {response.text[:200]}")
                    
                    if response.status_code == 200:
                        logger.info(f"✓ [Worker-{worker_id}] Successfully sent OCR result for report {data.report_id}")
                    else:
                        logger.warning(f"⚠ [Worker-{worker_id}] Webhook returned non-200 status: {response.status_code}")
                        
            except httpx.ConnectError as e:
                logger.error(f"🔌 Connection failed to {api_url}: {e}")
                raise
            except httpx.TimeoutException as e:
                logger.error(f"⏰ Timeout sending to webhook: {e}")
                raise
            except Exception as e:
                logger.error(f"❌ Unexpected error sending to webhook: {e}")
                raise

            logger.info(f"✓ [Worker-{worker_id}] Completed OCR for report {data.report_id}")
        except Exception as e:
            logger.error(f"✘ [Worker-{worker_id}] Error: {e}")
        finally:
            await queue_done(data)
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
