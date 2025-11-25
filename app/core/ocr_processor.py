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
    if url.startswith('file://'):
        file_path = url[7:]
        img = cv2.imread(file_path, cv2.IMREAD_COLOR)
        if img is None:
            raise ValueError(f"Failed to load image from {file_path}")
        return img
    else:
        response = httpx.get(url, timeout=30.0)
        response.raise_for_status()
        img_array = np.frombuffer(response.content, np.uint8)
        img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
        if img is None:
            raise ValueError(f"Failed to decode image from {url}")
        return img

def normalize_number(num_str: str) -> int:
    """Convert string number to int"""
    return int(num_str.replace('.', '').replace(',', '').replace(' ', ''))

def classify_app(text: str) -> str:
    """Rule-based app classification"""
    text_lower = text.lower()
    
    # Fitbit - paling spesifik
    if 'fitbit' in text_lower:
        return 'Fitbit'
    
    # Samsung Health - cek dulu sebelum Apple Health
    if 'samsung health' in text_lower or 'daily activity' in text_lower or 'aktivitas harian' in text_lower:
        return 'Samsung Health'
    
    # Google Fit - keyword unik
    if 'heart pts' in text_lower or 'move min' in text_lower or 'poin kardio' in text_lower or 'menit bergerak' in text_lower:
        return 'Google Fit'
    
    # Huawei Health - keyword unik
    if 'huawei' in text_lower or 'health+' in text_lower:
        return 'Huawei Health'
    
    # Cek "today's steps" atau "stress" + "wake" untuk Huawei
    if "today's steps" in text_lower or 'todays steps' in text_lower:
        if 'completed' in text_lower or 'activity rings' in text_lower or 'stress' in text_lower:
            return 'Huawei Health'
    
    # Cek "Stress" + "Wake" pattern (Huawei specific)
    if 'stress' in text_lower and 'wake' in text_lower:
        return 'Huawei Health'
    
    # Cek "Ingkh" keyword (Samsung specific)
    if 'ingkh' in text_lower:
        return 'Samsung Health'
    
    # Garmin Connect - keyword unik
    if 'garmin' in text_lower or ('% of goal' in text_lower and 'daily timeline' in text_lower):
        return 'Garmin Connect'
    
    # Apple Health - default
    return 'Apple Health'

def extract_steps_from_layout(results: list, app: str) -> int:
    """Extract steps using layout/position matching"""
    if app == 'Google Fit':
        # Find "Heart Pts" keyword position (handle GHeart, CHeart, etc)
        heart_idx = -1
        for i, (bbox, text, conf) in enumerate(results):
            text_lower = text.lower()
            if 'heart' in text_lower and ('pts' in text_lower or 'poin' in text_lower):
                heart_idx = i
                break
        
        if heart_idx > 0:
            # First, look for numbers WITH separators (more reliable for large numbers)
            candidates_with_sep = []
            for j in range(max(0, heart_idx-5), heart_idx):
                text = results[j][1]
                if ',' in text or ('.' in text and text.count('.') == 1 and len(text) > 3):
                    num_text = text.replace(',', '').replace('.', '').replace(' ', '')
                    if num_text.isdigit() and 3 <= len(num_text) <= 5:
                        candidates_with_sep.append((j, int(num_text)))
            
            # If found numbers with separators, return the closest one to Heart Pts
            if candidates_with_sep:
                # Sort by distance to heart_idx (closest first)
                candidates_with_sep.sort(key=lambda x: heart_idx - x[0])
                return candidates_with_sep[0][1]
            
            # Fallback: look for number immediately before "Heart Pts" (within 2 items)
            for j in range(max(0, heart_idx-2), heart_idx):
                text = results[j][1]
                num_text = text.replace(',', '').replace('.', '').replace(' ', '')
                if num_text.isdigit() and 3 <= len(num_text) <= 5:
                    return int(num_text)
    
    elif app == 'Huawei Health':
        # Check if "steps XXX /X.XXX steps" in single item
        for i, (bbox, text, conf) in enumerate(results):
            if 'steps' in text.lower() and '/' in text:
                # Extract number before /
                import re
                m = re.search(r'steps\s+(\d{3,5})\s*/', text, re.I)
                if m:
                    return int(m.group(1))
        
        # Find "Stress" then "Wake", number is between them
        stress_idx = wake_idx = -1
        for i, (bbox, text, conf) in enumerate(results):
            if 'stress' in text.lower():
                stress_idx = i
            if 'wake' in text.lower():
                wake_idx = i
                if stress_idx >= 0:
                    break
        
        if stress_idx >= 0 and wake_idx > stress_idx:
            for j in range(stress_idx+1, wake_idx):
                num_text = results[j][1].replace(',', '').replace('.', '').replace(' ', '')
                if num_text.isdigit() and 3 <= len(num_text) <= 5:
                    return int(num_text)
    
    elif app == 'Apple Health':
        # Find "Today" keyword appearing twice
        today_indices = []
        for i, (bbox, text, conf) in enumerate(results):
            if 'today' in text.lower():
                today_indices.append(i)
        
        if len(today_indices) >= 2:
            # Look for number after second "Today"
            start_idx = today_indices[1]
            for j in range(start_idx+1, min(len(results), start_idx+4)):
                text = results[j][1]
                # Check for number with separator
                if ',' in text or '.' in text:
                    num_text = text.replace(',', '').replace('.', '').replace(' ', '')
                    if num_text.isdigit() and 3 <= len(num_text) <= 5:
                        return int(num_text)
    
    elif app == 'Samsung Health':
        # Check if "X.XXX Ingkh" in single item
        for i, (bbox, text, conf) in enumerate(results):
            if 'ingkh' in text.lower():
                # Extract number before Ingkh
                import re
                m = re.search(r'(\d[\., ]\d{3})\s*ingkh', text, re.I)
                if m:
                    num_text = m.group(1).replace(',', '').replace('.', '').replace(' ', '')
                    return int(num_text)
    
    elif app == 'Garmin Connect':
        # Find "% of Goal" keyword
        goal_idx = -1
        for i, (bbox, text, conf) in enumerate(results):
            if '% of goal' in text.lower() or 'of goal' in text.lower():
                goal_idx = i
                break
        
        if goal_idx > 0:
            # Look for TWO numbers before "% of Goal"
            # First number = steps, Second number = goal
            candidates = []
            for j in range(max(0, goal_idx-5), goal_idx):
                text = results[j][1]
                # Check for number with separator (comma or dot)
                if ',' in text or ('.' in text and text.count('.') == 1 and len(text) > 3):
                    num_text = text.replace(',', '').replace('.', '').replace(' ', '')
                    if num_text.isdigit() and 4 <= len(num_text) <= 5:
                        candidates.append((j, int(num_text)))
            
            # Return the FIRST number (furthest from "% of Goal") = steps
            if len(candidates) >= 2:
                candidates.sort(key=lambda x: x[0])  # Sort by index ascending
                return candidates[0][1]  # Return first (steps)
            elif len(candidates) == 1:
                return candidates[0][1]
    
    return None

def extract_steps(text: str, app: str) -> int:
    """Extract step number using app-specific patterns"""
    
    if app == 'Apple Health':
        # Pattern: "TOTAL 12.515 steps" atau "TOTAL 15.226 steps"
        m = re.search(r'TOTAL\s+(\d{1,2}[\., ]\d{3})\s+steps', text, re.I)
        if m: return normalize_number(m.group(1))
        
        # Pattern: "Hari Ini Hari Ini 1.045 0,67KM"
        m = re.search(r'Hari Ini\s+Hari Ini\s+(\d{1,2}[\., ]\d{3})', text, re.I)
        if m: return normalize_number(m.group(1))
        
        # Pattern: "Langkah Jarak 2.802 1,83KM"
        m = re.search(r'Langkah\s+Jarak\s+(\d{1,2}[\., ]\d{3})', text, re.I)
        if m: return normalize_number(m.group(1))
        
        # Pattern: "Steps Distance 17.102 12,83KM"
        m = re.search(r'Steps\s+Distance\s+(\d{1,2}[\., ]\d{3})', text, re.I)
        if m: return normalize_number(m.group(1))
        
        # Pattern: "Langkah 16.56 1.836langkah" atau "Steps 13.30 1.990 steps"
        m = re.search(r'(?:Langkah|Steps)\s+\d{2}\.\d{2}\s+(\d{1,2}[\., ]\d{3})', text, re.I)
        if m: return normalize_number(m.group(1))
        
        # Pattern: "640 0,47kM" di awal (untuk gambar dengan format berbeda)
        m = re.search(r'\b(\d{3})\s+0[\.,]\d+\s*k[Mm]', text)
        if m: return int(m.group(1))
        
        # Pattern: "646 langkah" atau "736 0,46km"
        m = re.search(r'\b(\d{3})\s+(?:langkah|0[\.,]\d+\s*km)', text, re.I)
        if m: return int(m.group(1))
        
        # Pattern: "Today Today 10.818 7,42km" (untuk appple_12333.jpeg)
        m = re.search(r'Today\s+Today\s+(\d{1,2}[\., ]\d{3})\s+\d', text, re.I)
        if m: return normalize_number(m.group(1))
        
        # Pattern: "Today 14.578 9,99kM" (untuk 2025-11-21_232346_apple.png)
        m = re.search(r'Today\s+(\d{1,2}[\., ]\d{3})\s+\d', text, re.I)
        if m: return normalize_number(m.group(1))
        
        # Pattern: "Steps Distance 17.102 12,83KM" (untuk 2025-11-24_192531_apple.jpg)
        m = re.search(r'Steps\s+Distance\s+(\d{2}[\., ]\d{3})\s+\d', text, re.I)
        if m: return normalize_number(m.group(1))
        
        # Pattern: "TOTAL 15.226 steps" (untuk 2025-11-24_220330_apple.png)
        m = re.search(r'TOTAL\s+(\d{2}[\., ]\d{3})\s+steps', text, re.I)
        if m: return normalize_number(m.group(1))
        
        # Pattern: "Today Today 1.211 0,94kM" (untuk PHOTO-2025-11-10-14-38-52.jpg)
        m = re.search(r'Today\s+Today\s+(\d[\., ]\d{3})\s+0[\.,]\d+', text, re.I)
        if m: return normalize_number(m.group(1))
        
        # Pattern: "Steps Distance 17.102 12,83KM" (5 digit)
        m = re.search(r'Steps\s+Distance\s+(\d{2}[\., ]\d{3})\s+\d{2}[\.,]\d+', text, re.I)
        if m: return normalize_number(m.group(1))
        
    elif app == 'Google Fit':
        # Pattern: "589 Heart Pts" (3 digit tanpa separator) - cek dulu sebelum yang lain
        m = re.search(r'^.*?(\d{3})\s+Heart\s+Pts', text, re.I)
        if m: return int(m.group(1))
        
        # Pattern: "16,331 Heart Pts" atau "7,555 Heart Pts" (5 digit)
        m = re.search(r'(\d{2}[\., ,]\d{3})\s+Heart\s+Pts', text, re.I)
        if m: return normalize_number(m.group(1))
        
        # Pattern: "2,566 Heart Pts" atau "2,566 Poin Kardio" (4 digit)
        m = re.search(r'(\d{1,2}[\., ]\d{3})\s*(?:Heart|Hcart|Poin Kardio)', text, re.I)
        if m: return normalize_number(m.group(1))
        
        # Pattern: "Steps 1,571" atau "Stops 1.,602"
        m = re.search(r'(?:Steps|Stops|Langkah)\s+(\d{1,2}[\.,]\d{3})', text, re.I)
        if m: return normalize_number(m.group(1))
        
    elif app == 'Huawei Health':
        # Pattern: "Today's steps 395 /10.000 steps" (tanpa separator ribuan) - cek dulu
        m = re.search(r'Today\'?s steps\s+(\d{3,5})\s+/', text, re.I)
        if m: return int(m.group(1))
        
        # Pattern: "Today's steps 8,376/4,000 steps" - ambil angka pertama sebelum /
        m = re.search(r'Today\'?s steps\s+(\d{1,2}[\., ]\d{3})\s*/\s*\d', text, re.I)
        if m: return normalize_number(m.group(1))
        
        # Pattern: "Langkah hari ini 5.117/10.000 langkah"
        m = re.search(r'Langkah hari ini\s+(\d{1,2}[\., ]\d{3})\s*/\s*\d', text, re.I)
        if m: return normalize_number(m.group(1))
        
        # Pattern: "Langkah hari ini 824/7.000 langkah" (tanpa separator ribuan)
        m = re.search(r'Langkah hari ini\s+(\d{3,5})\s*/\s*\d', text, re.I)
        if m: return int(m.group(1))
        
        # Pattern: "Todays steps 5,498/10,000 steps"
        m = re.search(r'Todays steps\s+(\d{1,2}[\., ]\d{3})\s*/\s*\d', text, re.I)
        if m: return normalize_number(m.group(1))
        
        # Pattern: "Steps Mood 05.06 Stress 50 735 Wake" - ambil angka sebelum Wake
        m = re.search(r'Stress\s+\d+\s+(\d{3,5})\s+Wake', text, re.I)
        if m: return int(m.group(1))
        
        # Pattern: "Today's steps" tanpa angka setelahnya, cari di tempat lain
        if "today's steps" in text.lower() or 'todays steps' in text.lower():
            # Cari angka 3-5 digit yang mungkin steps
            m = re.search(r'\b(\d{3,5})\s+Wake', text, re.I)
            if m: return int(m.group(1))
        
        # Pattern: "Add record 8,376 steps Normal" (untuk huawei_.jpeg)
        m = re.search(r'Add record\s+(\d{1,2}[\., ]\d{3})', text, re.I)
        if m: return normalize_number(m.group(1))
        
    elif app == 'Samsung Health':
        # Pattern: "Steps Active time Activity calories 7.492 63 299"
        m = re.search(r'(?:Langkah|Steps)\s+(?:Waktu aktif|Active time)\s+(?:Kalori aktivitas|Activity calories)\s+(\d{1,2}[\., ]\d{3})\s+\d+\s+\d+', text, re.I)
        if m: return normalize_number(m.group(1))
        
        # Pattern: "Samsung Health 77 langkah"
        m = re.search(r'Samsung Health\s+(\d{1,5})\s*langkah', text, re.I)
        if m: return int(m.group(1))
        
        # Pattern: "Edit home 2,680 steps"
        m = re.search(r'Edit home\s+(\d{1,2}[\., ]\d{3})\s*steps', text, re.I)
        if m: return normalize_number(m.group(1))
        
        # Pattern: "Steps Active time Activity calories 725 8 28"
        m = re.search(r'(?:Langkah|Steps)\s+(?:Waktu aktif|Active time)\s+(?:Kalori aktivitas|Activity calories)\s+(\d{3,5})\s+\d+\s+\d+', text, re.I)
        if m: return int(m.group(1))
        
        # Pattern: "1,862 37% /5,000 steps"
        m = re.search(r'(\d{1,2}[\., ]\d{3})\s+\d+%\s*/\s*\d', text, re.I)
        if m: return normalize_number(m.group(1))
        
        # Pattern: "7.492 Ingkh Target: 10.000" (untuk 499507250_24620207707567726_7253775697531596173_n.jpg)
        m = re.search(r'(\d{1,2}[\., ]\d{3})\s+(?:Ingkh|langkah)\s+Target', text, re.I)
        if m: return normalize_number(m.group(1))
        
        # Pattern: "Active time Activity calories 13,130 98 941" (untuk 2025-11-24_174611_samsung.jpg)
        m = re.search(r'Active time\s+Activity calories\s+(\d{1,2}[\., ]\d{3})\s+\d+\s+\d+', text, re.I)
        if m: return normalize_number(m.group(1))
        
        # Pattern: "7.492 Ingkh" atau "Langkah < ... 7.492 Ingkh"
        m = re.search(r'(\d[\., ]\d{3})\s+Ingkh', text, re.I)
        if m: return normalize_number(m.group(1))
    
    elif app == 'Fitbit':
        m = re.search(r'(\d{1,2}[\., ]\d{3})\s*Langkah', text, re.I)
        if m: return normalize_number(m.group(1))
        
        m = re.search(r'fitbit.*?(\d{1,2}[\., ]\d{3})', text, re.I | re.DOTALL)
        if m: return normalize_number(m.group(1))
        
        m = re.search(r'Today\s+(\d{1,2}[\., ]\d{3})\s*Steps', text, re.I)
        if m: return normalize_number(m.group(1))
    
    elif app == 'Garmin Connect':
        # Pattern: "9,920 5,000 198% of Goal" or "10.514 6.180 170% of Goal"
        m = re.search(r'(\d{1,2}[\., ]\d{3})\s+\d[\., ]\d{3}\s+\d+%\s+of\s+Goal', text, re.I)
        if m: return normalize_number(m.group(1))
        
        # Pattern: "November 9,920 5,000"
        m = re.search(r'November\s+(\d{1,2}[\., ]\d{3})\s+\d', text, re.I)
        if m: return normalize_number(m.group(1))
    
    # Fallback patterns
    m = re.search(r'(\d{1,2}[\., ]\d{3})\s*(?:steps|langkah)', text, re.I)
    if m: return normalize_number(m.group(1))
    
    m = re.search(r'\b(\d{2,5})\s*(?:steps|langkah)', text, re.I)
    if m: return int(m.group(1))
    
    return None

def process_ocr(image_url: str, show_progress: bool = False) -> dict:
    start_time = time.time()
    if show_progress:
        print(f"🔍 Processing: {image_url.split('/')[-1]}...", end='', flush=True)
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
    
    # Extract steps using layout matching first
    steps = extract_steps_from_layout(results, app_class)
    
    # Fallback to regex if layout matching fails
    if steps is None:
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
    
    if show_progress:
        status = "✓" if steps else "✗"
        print(f" {status} {app_class} - {steps if steps else 'FAILED'} steps ({processing_time_ms}ms)")
    
    logger.info(f"✓ OCR completed: {app_class}, extracted {len(data)} fields, time: {processing_time_ms}ms")
    logger.info(f"Raw OCR: {raw_text}")
    logger.info(f"Extracted data: {data}")
    
    return {
        "raw_ocr": raw_text,
        "extracted_data": data,
        "app_class": app_class,
        "processing_time_ms": processing_time_ms
    }
