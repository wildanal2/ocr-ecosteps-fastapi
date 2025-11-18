import asyncio
import httpx
from contextlib import asynccontextmanager
from decouple import config
from app.core.ocr_processor import process_ocr
from app.core.logger import setup_logger

logger = setup_logger(__name__)

task_queue = asyncio.Queue()
queue_list = []

def queue_task_check(data) -> bool:
    for item in queue_list:
        if str(item.report_id) == str(data.report_id):
            item.s3_url = data.s3_url
            logger.info(f"⚠ Report {data.report_id} already in queue, updated s3_url")
            return True
    return False

def queue_add(data):
    queue_list.append(data)
    logger.info(f"✓ Added report {data.report_id} to queue (total: {len(queue_list)})")

def queue_clear():
    global queue_list
    count = len(queue_list)
    queue_list.clear()
    logger.info(f"✓ Cleared {count} items from queue_list")
    return count

def get_queue_list():
    """Get current queue_list - ensures we get the actual global reference"""
    global queue_list
    return queue_list

def queue_done(data):
    global queue_list
    before_count = len(queue_list)
    
    # Debug: Show what we're trying to remove
    logger.info(f"Attempting to remove report_id: {data.report_id} (type: {type(data.report_id)})")
    logger.info(f"Current queue_list before removal: {[(str(item.report_id), type(item.report_id)) for item in queue_list]}")
    
    # Convert both to string for comparison to handle int/str mismatch
    queue_list = [item for item in queue_list if str(item.report_id) != str(data.report_id)]
    after_count = len(queue_list)
    
    logger.info(f"✓ Removed report {data.report_id} from queue ({before_count} ➜ {after_count})")
    logger.info(f"Queue_list after removal: {[str(item.report_id) for item in queue_list]}")
    
    # Debug log to verify removal
    if before_count == after_count:
        logger.error(f"✘ FAILED: Report {data.report_id} was not found in queue_list for removal!")
        logger.error(f"Data object: {data}")
        logger.error(f"Data type: {type(data)}")

async def ocr_worker():
    while True:
        data = await task_queue.get()
        try:
            logger.info(f"⚙ Processing report {data.report_id}")
            
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

            async with httpx.AsyncClient() as client:
                response = await client.post(api_url, json=payload, headers=headers)
                logger.info(f"✓ Result sent to Laravel: {response.status_code}")

            logger.info(f"✓ Completed OCR for report {data.report_id}")
        except Exception as e:
            logger.error(f"✘ Worker error: {e}")
        finally:
            logger.info(f"Worker finally block: calling queue_done for report {data.report_id}")
            queue_done(data)
            task_queue.task_done()
            logger.info(f"Worker finally block: completed for report {data.report_id}")

@asynccontextmanager
async def lifespan(app):
    global queue_list
    queue_list.clear()  # Clear any existing queue data on startup
    workers = []
    worker_count = config("WORKER_COUNT", cast=int, default=3)
    for _ in range(worker_count):
        workers.append(asyncio.create_task(ocr_worker()))
    logger.info(f"✓ Started {worker_count} OCR workers")
    yield
    for worker in workers:
        worker.cancel()
