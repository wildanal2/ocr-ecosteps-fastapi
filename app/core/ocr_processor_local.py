import cv2
import re
import easyocr
import numpy as np
import time
import threading
from pathlib import Path
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

def load_local_image(file_path: str) -> np.ndarray:
    """Load image from local filesystem"""
    img = cv2.imread(file_path)
    if img is None:
        raise ValueError(f"Cannot load image: {file_path}")
    return img

def normalize_number(num_str: str) -> int:
    """Convert string number to int"""
    return int(num_str.replace('.', '').replace(',', ''))

def classify_app(text: str, category: str = None) -> str:
    """Rule-based app classification with category hint"""
    if category:
        return category
    
    text_lower = text.lower()
    
    if 'heart pts' in text_lower or 'move min' in text_lower or 'poin kardio' in text_lower:
        return 'Google Fit'
    elif 'huawei' in text_lower or 'health+' in text_lower:
        return 'Huawei Health'
    elif 'samsung health' in text_lower or 'together' in text_lower or 'kebugaran' in text_lower or 'aktivitas harian' in text_lower or 'ingkh' in text_lower:
        return 'Samsung Health'
    elif 'fitbit' in text_lower or 'today' in text_lower and 'steps' in text_lower:
        return 'Fitbit'
    elif 'activity' in text_lower or 'summary' in text_lower or 'fitness' in text_lower or 'workout' in text_lower:
        return 'Apple Health'
    else:
        return 'Other'

def extract_steps(text: str, app: str) -> int:
    """Extract step number using app-specific patterns"""
    
    if app == 'Apple Health' or app == 'Apple Health Old':
        # Pattern: "Today Today 10.818" or "Today 10,818"
        m = re.search(r'Today\s+(?:Today\s+)?(\d{1,2}[\.,]\d{3})', text, re.I)
        if m: return normalize_number(m.group(1))
        
        # Pattern: "TOTAL 12.515 steps" or "12,515 steps"
        m = re.search(r'(?:TOTAL|Total)\s+(\d{1,2}[\.,]\d{3})\s*steps', text, re.I)
        if m: return normalize_number(m.group(1))
        
        # Pattern: "401steps" (no space)
        m = re.search(r'(\d{3,5})steps', text, re.I)
        if m: return int(m.group(1))
        
        m = re.search(r'(\d+)\s*langkah', text, re.I)
        if m: return int(m.group(1))
        
        m = re.search(r'Step Count.*?Today\s+Today\s+(\d{3,5})', text, re.I | re.DOTALL)
        if m: return int(m.group(1))
        
        m = re.search(r'Hari Ini\s+(\d{3,5})', text, re.I)
        if m: return int(m.group(1))
        
    elif app == 'Google Fit':
        # Pattern: "16.828 Poin Kardio" or "827 CHeart Pts" (OCR typo) - prioritize Heart Pts
        m = re.search(r'(\d{1,2}[\.,]?\d{0,3})\s*(?:CHeart Pts|GHeart Pts|Heart Pts|Poin Kardio|Kcart Pis)', text, re.I)
        if m: 
            num_str = m.group(1)
            if '.' in num_str or ',' in num_str:
                return normalize_number(num_str)
            else:
                return int(num_str)
        
        # Pattern: "Langkah 16,828" or "ASteps 1,602"
        m = re.search(r'(?:Langkah|ASteps)\s+(\d{1,2}[\.,]\d{3})', text, re.I)
        if m: return normalize_number(m.group(1))
        
    elif app == 'Huawei Health':
        # Pattern: "395 /10.000 steps" - get number BEFORE slash
        m = re.search(r'(\d{1,5})\s*/\s*\d+[\.,]?\d*\s*steps', text, re.I)
        if m: return int(m.group(1))
        
        # Pattern: "Steps ... 8,376" - prioritize after "Steps" keyword
        m = re.search(r'Steps.*?(\d{1,2}[\.,]\d{3})', text, re.I | re.DOTALL)
        if m: return normalize_number(m.group(1))
        
        # Pattern: "8,376 steps" or "8.376 steps"
        m = re.search(r'(\d{1,2}[\.,]\d{3})\s*steps', text, re.I)
        if m: return normalize_number(m.group(1))
        
    elif app == 'Samsung Health':
        # Pattern: "3,139 steps" - NOT after slash (avoid target)
        m = re.search(r'(?<!/)(\d{1,2}[\.,]\d{3})\s*steps', text, re.I)
        if m: return normalize_number(m.group(1))
        
        # Pattern: "1.035 langkah" or "1,035 langkah"
        m = re.search(r'(\d{1,2}[\.,]\d{3})\s*langkah', text, re.I)
        if m: return normalize_number(m.group(1))
        
        # Pattern: "Steps ... 17,029" - get first number after Steps keyword
        m = re.search(r'Steps.*?(\d{1,2}[\.,]\d{3})', text, re.I | re.DOTALL)
        if m: return normalize_number(m.group(1))
        
        m = re.search(r'(\d[\.,]\d{3})\s*Ingkh', text, re.I)
        if m: return normalize_number(m.group(1))
        
        m = re.search(r'aktivitas\s+(\d[\.,]\d{3})', text, re.I)
        if m: return normalize_number(m.group(1))
    
    elif app == 'Fitbit':
        # Pattern: "Today 11,820 Steps" - prioritize after "Today"
        m = re.search(r'Today\s+(\d{1,2}[\.,]\d{3})\s*Steps', text, re.I)
        if m: return normalize_number(m.group(1))
        
        m = re.search(r'(\d{1,2}[\.,]\d{3})\s*steps', text, re.I)
        if m: return normalize_number(m.group(1))
        
        m = re.search(r'(\d{3,5})\s*steps', text, re.I)
        if m: return int(m.group(1))
    
    return None

def process_ocr_local(file_path: str, category: str = None) -> dict:
    """Process OCR from local file"""
    start_time = time.time()
    logger.info(f"🔍 Processing local OCR: {file_path}")
    
    # Load & preprocess
    img = load_local_image(file_path)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img_rgb = cv2.resize(img_rgb, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    
    # OCR
    ocr_reader = get_reader()
    results = ocr_reader.readtext(img_rgb)
    raw_text = ' '.join([res[1] for res in results])
    
    # Classify app
    app_class = classify_app(raw_text, category)
    
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
    
    m = re.search(r'(\d{2}):(\d{2})[:\.?](\d{2})', raw_text)
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
    
    return {
        "file_path": file_path,
        "file_name": Path(file_path).name,
        "raw_ocr": raw_text,
        "extracted_data": data,
        "app_class": app_class,
        "processing_time_ms": processing_time_ms
    }
