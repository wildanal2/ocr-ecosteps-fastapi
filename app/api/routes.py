from datetime import datetime
import asyncio
import psutil
import torch
from decouple import config
from fastapi import APIRouter, Request, Depends
from app.models.responses import HealthResponse, StatusResponse, AppStatusResponse
from app.models.requests import OCRRequest
from app.models.dev_requests import OCRDevRequest
from app.core.config import settings
from app.core.logger import setup_logger
from app.core.queue import task_queue, queue_task_check, lifespan, queue_add, queue_clear, get_queue_list
from app.core.ocr_processor import process_ocr, get_reader
from app.core.auth import verify_api_key

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
    logger.info("Status endpoint accessed")
    return StatusResponse(
        status="running",
        uptime=str(uptime).split('.')[0],
        version=settings.APP_VERSION
    )

@router.get("/app-status", response_model=AppStatusResponse)
async def app_status():
    """Comprehensive application status with OCR, queue, and worker information"""
    uptime = datetime.now() - start_time
    worker_count = config("WORKER_COUNT", cast=int, default=3)
    
    # OCR Engine Status
    try:
        gpu_available = torch.cuda.is_available()
        gpu_name = torch.cuda.get_device_name(0) if gpu_available else None
    except:
        gpu_available = False
        gpu_name = None
    
    ocr_engine = {
        "engine": "EasyOCR",
        "gpu_enabled": gpu_available,
        "gpu_device": gpu_name,
        "languages": ["en"],
        "status": "ready" if get_reader() else "loading"
    }
    
    # Queue Information - use getter to ensure correct reference
    current_queue_list = get_queue_list()
    waiting_count = task_queue.qsize()
    tracked_count = len(current_queue_list)
    processing_count = max(0, tracked_count - waiting_count)
    
    # Debug logging
    logger.info(f"Queue status - Waiting: {waiting_count}, Tracked: {tracked_count}, Processing: {processing_count}")
    logger.info(f"Queue list contents: {[f'ID:{item.report_id}' for item in current_queue_list]}")
    
    queue_info = {
        "waiting_in_queue": waiting_count,
        "total_reports_tracked": tracked_count,
        "currently_processing": processing_count,
        "queue_capacity": "unlimited",
        "reports_in_queue": [{
            "report_id": item.report_id,
            "user_id": item.user_id,
            "img_url": item.s3_url
        } for item in current_queue_list[:5]]  # Show first 5
    }
    
    # Worker Information
    busy_workers = min(worker_count, processing_count)
    idle_workers = max(0, worker_count - busy_workers)
    
    workers_info = {
        "total_workers": worker_count,
        "busy_workers": busy_workers,
        "idle_workers": idle_workers,
        "worker_type": "async",
        "processing_mode": "concurrent"
    }
    
    # Processing Statistics
    processing_info = {
        "supported_apps": ["Google Fit", "Samsung Health", "Huawei Health", "Apple Health", "Other"],
        "extraction_fields": ["steps", "distance", "duration", "calories", "heart_rate", "pace", "speed"],
        "image_preprocessing": "resize_2x + color_conversion",
        "avg_processing_time": "2-5 seconds"
    }
    
    # System Information
    system_info = {
        "cpu_usage": f"{psutil.cpu_percent()}%",
        "memory_usage": f"{psutil.virtual_memory().percent}%",
        "disk_usage": f"{psutil.disk_usage('/').percent}%",
        "python_version": f"{psutil.sys.version_info.major}.{psutil.sys.version_info.minor}"
    }
    
    logger.info("App status endpoint accessed")
    
    return AppStatusResponse(
        service=settings.APP_NAME,
        version=settings.APP_VERSION,
        uptime=str(uptime).split('.')[0],
        timestamp=datetime.now().isoformat(),
        ocr_engine=ocr_engine,
        queue=queue_info,
        workers=workers_info,
        processing=processing_info,
        system=system_info
    )

@router.post("/api/v1/ocr-ecosteps", dependencies=[Depends(verify_api_key)])
async def submit_ocr_queue(data: OCRRequest, request: Request):
    """Submit OCR document to processing queue"""
    async with lifespan(request.app):
        if queue_task_check(data):
            return {"message": "Laporan Anda telah diterima dan sedang dalam antrean verifikasi."}
        queue_add(data)
        await task_queue.put(data)
        return {"message": "Laporan Anda telah diterima dan dimasukkan ke dalam antrean verifikasi."}

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

@router.post("/admin/clear-queue", dependencies=[Depends(verify_api_key)])
async def clear_queue():
    """Clear all queue data (admin endpoint)"""
    cleared_count = queue_clear()
    logger.info(f"✓ Admin: Cleared {cleared_count} items from queue")
    return {"message": f"Queue cleared. Removed {cleared_count} items."}
