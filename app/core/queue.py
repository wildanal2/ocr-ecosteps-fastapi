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
        if item.report_id == data.report_id:
            item.s3_url = data.s3_url
            logger.info(f"⚠ Report {data.report_id} already in queue, updated s3_url")
            return True
    logger.info(f"✓ Adding report {data.report_id} to queue")
    queue_list.append(data)
    return False

def queue_done(data):
    global queue_list
    before_count = len(queue_list)
    queue_list = [item for item in queue_list if item.report_id != data.report_id]
    after_count = len(queue_list)
    logger.info(f"✓ Removed report {data.report_id} from queue ({before_count} ➜ {after_count})")

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
                "raw_ocr": result["raw_ocr"],
                "extracted_data": result["extracted_data"],
                'app_class': result["app_class"]
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
            queue_done(data)
            task_queue.task_done()

@asynccontextmanager
async def lifespan(app):
    workers = []
    worker_count = config("WORKER_COUNT", cast=int, default=3)
    for _ in range(worker_count):
        workers.append(asyncio.create_task(ocr_worker()))
    logger.info(f"✓ Started {worker_count} OCR workers")
    yield
    for worker in workers:
        worker.cancel()
