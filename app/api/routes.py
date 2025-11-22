from datetime import datetime
import asyncio
from fastapi import APIRouter, Depends
from app.models.responses import HealthResponse, StatusResponse, AppStatusResponse
from app.models.requests import OCRRequest
from app.models.dev_requests import OCRDevRequest
from app.models.local_requests import OCRLocalRequest
from app.core.config import settings
from app.core.logger import setup_logger
from app.core.queue import task_queue, queue_add, queue_clear, queue_task_check
from app.core.ocr_processor import process_ocr
from app.core.ocr_processor_local import process_ocr_local
from app.core.auth import verify_api_key
from app.api.status import get_app_status

logger = setup_logger(__name__)
router = APIRouter()
start_time = datetime.now()

@router.get("/", response_model=dict)
async def root():
    logger.info("Root endpoint accessed")
    return {
        "message": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs"
    }

@router.get("/health", response_model=HealthResponse)
async def health_check():
    logger.info("Health check endpoint accessed")
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        service="ocr-ecosteps"
    )

@router.get("/status", response_model=StatusResponse)
async def status():
    uptime = datetime.now() - start_time
    return StatusResponse(
        status="running",
        uptime=str(uptime).split('.')[0],
        version=settings.APP_VERSION
    )

@router.get("/app-status", response_model=AppStatusResponse)
async def app_status():
    """Comprehensive application status with OCR, queue, and worker information"""
    return get_app_status(start_time)

@router.post("/api/v1/ocr-ecosteps", dependencies=[Depends(verify_api_key)])
async def submit_ocr_queue(data: OCRRequest):
    """Submit OCR document to processing queue"""
    try:
        if await queue_task_check(data):
            return {"message": "Laporan Anda telah diterima dan sedang dalam antrean verifikasi."}
        await queue_add(data)
        await task_queue.put(data)
        return {"message": "Laporan Anda telah diterima dan dimasukkan ke dalam antrean verifikasi."}
    except Exception as e:
        logger.error(f"✘ Failed to add to queue: {e}")
        return {"error": "Queue is full", "message": "Sistem sedang sibuk. Silakan coba lagi dalam beberapa saat."}, 503

@router.post("/api/v1/ocr-ecosteps/dev", dependencies=[Depends(verify_api_key)])
async def process_ocr_dev(data: OCRDevRequest):
    """Direct OCR processing for testing/development (no queue)"""
    logger.info(f"⚙ Dev mode: Processing OCR for {data.img_url}")
    try:
        result = await asyncio.to_thread(process_ocr, data.img_url)
        logger.info(f"✓ Dev mode: OCR completed")
        return result
    except Exception as e:
        logger.error(f"✘ Dev mode error: {e}")
        raise

@router.post("/api/v1/ocr-ecosteps/local", dependencies=[Depends(verify_api_key)])
async def process_ocr_local_endpoint(data: OCRLocalRequest):
    """Local file OCR processing for research/validation (no queue)"""
    logger.info(f"🔬 Research mode: Processing local file {data.img_path}")
    try:
        result = await asyncio.to_thread(process_ocr_local, data.img_path, data.category)
        logger.info(f"✓ Research mode: OCR completed")
        return result
    except Exception as e:
        logger.error(f"✘ Research mode error: {e}")
        raise

@router.post("/admin/clear-queue", dependencies=[Depends(verify_api_key)])
async def clear_queue():
    """Clear all queue data (admin endpoint)"""
    cleared_count = await queue_clear()
    logger.info(f"✓ Admin: Cleared {cleared_count} items from queue")
    return {"message": f"Queue cleared. Removed {cleared_count} items."}
