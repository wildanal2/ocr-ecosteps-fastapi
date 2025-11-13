from datetime import datetime
import asyncio
from fastapi import APIRouter, Request, Depends
from app.models.responses import HealthResponse, StatusResponse
from app.models.requests import OCRRequest
from app.models.dev_requests import OCRDevRequest
from app.core.config import settings
from app.core.logger import setup_logger
from app.core.queue import task_queue, queue_task_check, lifespan
from app.core.ocr_processor import process_ocr
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

@router.post("/api/v1/ocr-ecosteps", dependencies=[Depends(verify_api_key)])
async def submit_ocr_queue(data: OCRRequest, request: Request):
    """Submit OCR document to processing queue"""
    async with lifespan(request.app):
        if queue_task_check(data):
            return {"message": "Laporan Anda telah diterima dan sedang dalam antrean verifikasi."}
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
