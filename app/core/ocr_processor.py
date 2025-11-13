import cv2
import re
import easyocr
import numpy as np
import httpx
from app.core.logger import setup_logger

logger = setup_logger(__name__)
reader = None

def get_reader():
    global reader
    if reader is None:
        try:
            import torch
            gpu_available = torch.cuda.is_available()
            logger.info(f"📦 Loading EasyOCR (GPU: {gpu_available})...")
            reader = easyocr.Reader(['en'], gpu=gpu_available)
            logger.info(f"✓ EasyOCR loaded with {'GPU' if gpu_available else 'CPU'}")
        except ImportError:
            logger.warning("⚠ PyTorch not found, using CPU")
            reader = easyocr.Reader(['en'], gpu=False)
    return reader

def download_image(url: str) -> np.ndarray:
    response = httpx.get(url)
    response.raise_for_status()
    img_array = np.frombuffer(response.content, np.uint8)
    return cv2.imdecode(img_array, cv2.IMREAD_COLOR)

def process_ocr(image_url: str) -> dict:
    logger.info(f"🔍 Processing OCR for: {image_url}")
    
    # Download & preprocess
    img = download_image(image_url)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img_rgb = cv2.resize(img_rgb, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    
    # OCR
    ocr_reader = get_reader()
    results = ocr_reader.readtext(img_rgb)
    raw_text = ' '.join([res[1] for res in results])
    
    # Extract data
    data = {}
    
    m = re.search(r'(\d{1,2})\s+(\w+)\s+(\d{4})\s+at\s+(\d{1,2}\.\d{2})', raw_text)
    if m: data['date'] = f"{m.group(1)} {m.group(2)} {m.group(3)} at {m.group(4)}"
    
    m = re.search(r'(\d+[,\.]\d+)\s*km', raw_text)
    if m: data['distance'] = f"{m.group(1)} km"
    
    m = re.search(r'(\d{2}):(\d{2})[:\.](\\d{2})', raw_text)
    if m: data['duration'] = f"{m.group(1)}:{m.group(2)}:{m.group(3)}"
    
    m = re.search(r'(\d+)\s*(?:ca|kcal)', raw_text, re.I)
    if m: data['total_calories'] = f"{m.group(1)} kcal"
    
    m = re.search(r"(\d+)'(\d+)\"", raw_text)
    if m: data['avg_pace'] = f"{m.group(1)}'{m.group(2)}\" /km"
    
    speeds = re.findall(r'(\d+[,\.]\d+)\s*km', raw_text)
    if len(speeds) > 1: data['avg_speed'] = f"{speeds[1]} km/h"
    
    m = re.search(r'(\d{2,3})\s*(?:deeps|steps)/min', raw_text, re.I)
    if m: data['avg_cadence'] = f"{m.group(1)} steps/min"
    
    m = re.search(r'(\d+)\s*cm', raw_text)
    if m: data['avg_stride'] = f"{m.group(1)} cm"
    
    m = re.search(r'(\d+)[.,](\d+)\s*steps', raw_text, re.I)
    if m: data['steps'] = int(f"{m.group(1)}{m.group(2)}")
    
    m = re.search(r'(\d{2,3})\s*bpm', raw_text, re.I)
    if m: data['avg_heart_rate'] = f"{m.group(1)} bpm"
    
    logger.info(f"✓ OCR completed, extracted {len(data)} fields")
    
    return {
        "raw_ocr": raw_text,
        "extracted_data": data
    }
