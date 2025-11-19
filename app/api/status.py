from datetime import datetime
import torch
import psutil
from decouple import config
from app.models.responses import AppStatusResponse
from app.core.config import settings
from app.core.queue import task_queue, get_queue_list
from app.core.ocr_processor import get_reader

def get_app_status(start_time: datetime) -> AppStatusResponse:
    """Get comprehensive application status"""
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
    
    # Queue Information
    current_queue_list = get_queue_list()
    waiting_count = task_queue.qsize()
    tracked_count = len(current_queue_list)
    processing_count = max(0, tracked_count - waiting_count)
    
    queue_info = {
        "waiting_in_queue": waiting_count,
        "total_reports_tracked": tracked_count,
        "currently_processing": processing_count,
        "queue_capacity": "unlimited",
        "reports_in_queue": [{
            "report_id": item.report_id,
            "user_id": item.user_id,
            "img_url": item.s3_url
        } for item in current_queue_list[:5]]
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
    }
    
    # System Information
    system_info = {
        "cpu_usage": f"{psutil.cpu_percent()}%",
        "memory_usage": f"{psutil.virtual_memory().percent}%",
        "disk_usage": f"{psutil.disk_usage('/').percent}%",
        "python_version": f"{psutil.sys.version_info.major}.{psutil.sys.version_info.minor}"
    }
    
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
