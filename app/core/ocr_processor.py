import cv2
import re
import easyocr
import numpy as np
import httpx
import time
import threading
from app.core.logger import setup_logger

logger = setup_logger(__name__)
reader = None
reader_lock = threading.Lock()

def get_reader():
    global reader
    if reader is None:
        with reader_lock:
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

def normalize_number(num_str: str) -> int:
    """Convert string number to int"""
    return int(num_str.replace('.', '').replace(',', '').replace(' ', ''))

def classify_app(text: str) -> str:
    """Rule-based app classification"""
    text_lower = text.lower()
    
    if 'fitbit' in text_lower:
        return 'Fitbit'
    elif 'heart pts' in text_lower or 'move min' in text_lower or 'poin kardio' in text_lower:
        return 'Google Fit'
    elif 'huawei' in text_lower or 'health+' in text_lower or 'kesehatan bergerak' in text_lower or "today's steps" in text_lower or 'todays steps' in text_lower:
        return 'Huawei Health'
    elif 'samsung health' in text_lower or 'daily activity' in text_lower or 'aktivitas harian' in text_lower:
        return 'Samsung Health'
    else:
        return 'Apple Health'

def extract_steps(text: str, app: str) -> int:
    """Extract step number using app-specific patterns"""
    
    if app == 'Apple Health':
        m = re.search(r'Hari Ini\s+Hari Ini\s+(\d{1,2}[\., ]\d{3})', text, re.I)
        if m: return normalize_number(m.group(1))
        
        m = re.search(r'Langkah\s+Jarak\s+(\d{1,2}[\., ]\d{3})', text, re.I)
        if m: return normalize_number(m.group(1))
        
        m = re.search(r'Steps\s+Distance\s+(\d{1,2}[\., ]\d{3})', text, re.I)
        if m: return normalize_number(m.group(1))
        
        m = re.search(r'(?:Langkah|Steps)\s+\d{2}\.\d{2}\s+(\d{1,2}[\., ]\d{3})', text, re.I)
        if m: return normalize_number(m.group(1))
        
        m = re.search(r'Steps\s+Distance\s+(\d{1,2})[\., ](\d{3})', text, re.I)
        if m: return int(m.group(1) + m.group(2))
        
        m = re.search(r'(?:TOTAL|Total)\s+\d+\s*(?:KCAL|KKAL)\s+(?:Langkah|Steps).*?(\d{1,2}[\., ]\d{3})', text, re.I | re.DOTALL)
        if m: return normalize_number(m.group(1))
        
        m = re.search(r'TOTAL\s+(\d{1,2}[\., ]\d{3})\s+\d{2}\s+\w+\s+\d{4}', text, re.I)
        if m: return normalize_number(m.group(1))
        
    elif app == 'Google Fit':
        m = re.search(r'(\d{1,2}[\., ]\d{3})\s*Heart', text, re.I)
        if m: return normalize_number(m.group(1))
        
        m = re.search(r'(\d{1,2}[\.,]?\d{0,3})\s*(?:CHeart Pts|GHeart Pts|Heart Pts|Poin Kardio)', text, re.I)
        if m: return normalize_number(m.group(1))
        
        m = re.search(r'Steps\s+(\d{1,2}[\., ]\d{3})', text, re.I)
        if m: return normalize_number(m.group(1))
        
    elif app == 'Huawei Health':
        m = re.search(r'Langkah hari ini\s+(\d{1,2}[\., ]?\d{3})\s*/\s*\d', text, re.I)
        if m: return normalize_number(m.group(1))
        
        m = re.search(r'Today\'?s steps\s+(\d{1,2}[\., ]?\d{3})\s*/\s*\d', text, re.I)
        if m: return normalize_number(m.group(1))
        
        m = re.search(r'Todays steps\s+(\d{1,2}[\., ]?\d{3})\s*/\s*\d', text, re.I)
        if m: return normalize_number(m.group(1))
        
        m = re.search(r'Stress\s+\d+\s+(\d{1,2}[\., ]?\d{3})\s+Wake', text, re.I)
        if m: return normalize_number(m.group(1))
        
    elif app == 'Samsung Health':
        m = re.search(r'Samsung Health\s+(\d{1,2}[\., ]?\d{2,3})\s*langkah', text, re.I)
        if m: return normalize_number(m.group(1))
        
        m = re.search(r'Edit home\s+(\d{1,2}[\., ]\d{3})\s*steps', text, re.I)
        if m: return normalize_number(m.group(1))
        
        m = re.search(r'(?:Langkah|Steps)\s+(?:Waktu aktif|Active time).*?(\d{1,2}[\., ]\d{3})\s+\d+', text, re.I | re.DOTALL)
        if m: return normalize_number(m.group(1))
        
        m = re.search(r'(?:Kalori aktivitas|Activity calories)\s+(\d{1,2}[\., ]\d{3})', text, re.I)
        if m: return normalize_number(m.group(1))
        
        m = re.search(r'(\d{1,2}[\., ]\d{3})\s+\d+%\s*/\s*\d', text, re.I)
        if m: return normalize_number(m.group(1))
    
    elif app == 'Fitbit':
        m = re.search(r'(\d{1,2}[\., ]\d{3})\s*Langkah', text, re.I)
        if m: return normalize_number(m.group(1))
        
        m = re.search(r'fitbit.*?(\d{1,2}[\., ]\d{3})', text, re.I | re.DOTALL)
        if m: return normalize_number(m.group(1))
        
        m = re.search(r'Today\s+(\d{1,2}[\., ]\d{3})\s*Steps', text, re.I)
        if m: return normalize_number(m.group(1))
    
    # Fallback
    m = re.search(r'(\d{1,2}[\., ]\d{3})\s*(?:steps|langkah)', text, re.I)
    if m: return normalize_number(m.group(1))
    
    m = re.search(r'\b(\d{2,3})\s*(?:steps|langkah)', text, re.I)
    if m: return int(m.group(1))
    
    return None

def process_ocr(image_url: str) -> dict:
    start_time = time.time()
    logger.info(f"🔍 Processing OCR for: {image_url}")
    
    # Download & preprocess
    img = download_image(image_url)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img_rgb = cv2.resize(img_rgb, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    
    # OCR
    ocr_reader = get_reader()
    results = ocr_reader.readtext(img_rgb)
    raw_text = ' '.join([res[1] for res in results])
    
    # Classify app
    app_class = classify_app(raw_text)
    
    # Extract steps
    steps = extract_steps(raw_text, app_class)
    
    # Extract other data
    data = {}
    if steps:
        data['steps'] = steps
    
    m = re.search(r'(\d{1,2})\s+(\w+)\s+(\d{4})\s+at\s+(\d{1,2}\.\d{2})', raw_text)
    if m: data['date'] = f"{m.group(1)} {m.group(2)} {m.group(3)} at {m.group(4)}"
    
    m = re.search(r'(\d+[,\.]\d+)\s*km', raw_text)
    if m: data['distance'] = f"{m.group(1)} km"
    
    m = re.search(r'(\d{2}):(\d{2})[:\.]?(\d{2})', raw_text)
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
    
    m = re.search(r'(\d{2,3})\s*bpm', raw_text, re.I)
    if m: data['avg_heart_rate'] = f"{m.group(1)} bpm"
    
    processing_time_ms = int((time.time() - start_time) * 1000)
    
    logger.info(f"✓ OCR completed: {app_class}, extracted {len(data)} fields, time: {processing_time_ms}ms")
    logger.info(f"Raw OCR: {raw_text}")
    logger.info(f"Extracted data: {data}")
    
    return {
        "raw_ocr": raw_text,
        "extracted_data": data,
        "app_class": app_class,
        "processing_time_ms": processing_time_ms
    }
