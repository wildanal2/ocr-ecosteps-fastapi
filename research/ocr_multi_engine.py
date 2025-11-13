import pytesseract
import cv2
import re
import time

try:
    import easyocr
    EASYOCR_AVAILABLE = True
except ImportError:
    EASYOCR_AVAILABLE = False
    print("⚠️  EasyOCR not installed. Install: pip install easyocr")

image_path = 'WhatsApp Image 2025-11-06 at 11.15.40.jpeg'

print("="*60)
print("🚀 MULTI-ENGINE OCR PROCESSING")
print("="*60)

# Preprocessing
print("\n📷 Loading image...")
t0 = time.time()
img = cv2.imread(image_path)
print(f"   ✓ Image loaded: {time.time()-t0:.0f}ms")

print("\n🔧 Preprocessing...")
t0 = time.time()
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
gray = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
_, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
print(f"   ✓ Preprocessing done: {(time.time()-t0)*1000:.0f}ms")

# OCR dengan Tesseract
print("\n🔍 Running Tesseract OCR...")
t0 = time.time()
text_tess = pytesseract.image_to_string(thresh, config=r'--oem 3 --psm 6')
print(f"   ✓ Tesseract completed: {(time.time()-t0)*1000:.0f}ms")

# OCR dengan EasyOCR
text_easy = ""
if EASYOCR_AVAILABLE:
    print("\n🔍 Running EasyOCR...")
    t0 = time.time()
    reader = easyocr.Reader(['en'], gpu=False, verbose=False)
    print(f"   ✓ Model loaded: {(time.time()-t0)*1000:.0f}ms")
    
    t0 = time.time()
    results = reader.readtext(thresh)
    text_easy = ' '.join([res[1] for res in results])
    print(f"   ✓ EasyOCR completed: {(time.time()-t0)*1000:.0f}ms")

# Gabungkan hasil (prioritas EasyOCR jika ada)
print("\n⚙️  Merging results...")
t0 = time.time()
text = text_easy if text_easy else text_tess
print(f"   ✓ Merge completed: {(time.time()-t0)*1000:.0f}ms")

def extract_field(pattern, text, group=1):
    match = re.search(pattern, text)
    return match.group(group) if match else None

print("\n📊 Extracting structured data...")
t0 = time.time()
data = {}

# Tanggal
date = extract_field(r'(\d{1,2}\s+\w+\s+\d{4}\s+at\s+\d{1,2}\.\d{2})', text)
if date:
    data['date'] = date

# Duration - coba dari kedua engine
dur_tess = re.search(r'(\d{2}):(\d{2,3}):(\d{2})', text_tess)
dur_easy = re.search(r'(\d{2}):(\d{2}):(\d{2})', text_easy) if text_easy else None

if dur_easy:
    data['duration'] = f"{dur_easy.group(1)}:{dur_easy.group(2)}:{dur_easy.group(3)}"
elif dur_tess:
    mins = dur_tess.group(2)
    if len(mins) == 3 and mins.startswith('1'):
        mins = mins[1:]
    data['duration'] = f"{dur_tess.group(1)}:{mins}:{dur_tess.group(3)}"

# Calories
cal = extract_field(r'(\d+)\s*(?:ca|kcal)', text)
if cal:
    data['total_calories'] = f"{cal} kcal"

# Pace
pace = re.search(r"(\d+)'(\d+)\"\s*/km", text)
if pace:
    data['avg_pace'] = f"{pace.group(1)}'{pace.group(2)}\" /km"

# Speed
speed = extract_field(r'(\d+[,\.]\d+)\s*km', text)
if speed:
    data['avg_speed'] = f"{speed} km/h"

# Cadence - coba dari kedua engine
cad_tess = re.search(r'(\d+)\s*steps?/min', text_tess)
cad_easy = re.search(r'(\d+)\s*steps?/min', text_easy) if text_easy else None

if cad_easy:
    data['avg_cadence'] = f"{cad_easy.group(1)} steps/min"
elif cad_tess:
    cad = cad_tess.group(1)
    if int(cad) < 100:
        cad = '1' + cad
    data['avg_cadence'] = f"{cad} steps/min"

# Stride
stride = extract_field(r'(\d+)\s*cm', text)
if stride:
    data['avg_stride'] = f"{stride} cm"

# Steps
steps = extract_field(r'(\d+[.,]\d+)\s*(?:steps?|seps)', text)
if steps:
    data['steps'] = f"{steps} steps"

# Heart rate
hr = extract_field(r'(\d+)\s*bpm', text)
if hr:
    data['avg_heart_rate'] = f"{hr} bpm"

print(f"   ✓ Extraction completed: {(time.time()-t0)*1000:.0f}ms")

print("\n" + "="*60)
print("📋 HASIL EKSTRAKSI DATA")
print("="*60)
print(f"Engine: {'Tesseract + EasyOCR' if EASYOCR_AVAILABLE else 'Tesseract only'}")
print("="*60)
for key, value in data.items():
    print(f"{key.replace('_', ' ').title():<20}: {value}")
print("="*60)
