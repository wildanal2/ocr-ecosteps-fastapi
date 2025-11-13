import pytesseract
import cv2
import re
import time

image_path = 'WhatsApp Image 2025-11-06 at 11.15.40.jpeg'

print("="*60)
print("⚡ OPTIMIZED OCR PROCESSING")
print("="*60)

# Load & Preprocessing
print("\n🔧 Preprocessing...")
t0 = time.time()
img = cv2.imread(image_path)
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# Adaptive preprocessing untuk area berbeda
h, w = gray.shape
clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
gray = clahe.apply(gray)
gray = cv2.resize(gray, None, fx=2.5, fy=2.5, interpolation=cv2.INTER_CUBIC)
gray = cv2.bilateralFilter(gray, 5, 75, 75)
_, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
print(f"   ✓ Done: {(time.time()-t0)*1000:.0f}ms")

# Tesseract dengan config optimal
print("\n🔍 Running Tesseract (optimized)...")
t0 = time.time()
custom_config = r'--oem 3 --psm 6'
text = pytesseract.image_to_string(thresh, config=custom_config)
print(f"   ✓ Completed: {(time.time()-t0)*1000:.0f}ms")

# Ekstraksi dengan smart correction
print("\n📊 Extracting data...")
t0 = time.time()
data = {}

# Date
m = re.search(r'(\d{1,2}\s+\w+\s+\d{4})\s+at\s+(\d{1,2}\.\d{2})', text)
if m: data['date'] = f"{m.group(1)} at {m.group(2)}"

# Duration - smart fix
m = re.search(r'(\d{2}):(\d{2,3}):(\d{2})', text)
if m:
    h, mins, s = m.group(1), m.group(2), m.group(3)
    # Fix OCR error: 119 -> 19
    if len(mins) == 3 and mins[0] == '1' and int(mins) > 59:
        mins = mins[1:]
    data['duration'] = f"{h}:{mins}:{s}"

# Calories
m = re.search(r'(\d+)\s*(?:ca|kcal)', text, re.I)
if m: data['total_calories'] = f"{m.group(1)} kcal"

# Pace
m = re.search(r"(\d+)'(\d+)\"\s*/km", text)
if m: data['avg_pace'] = f"{m.group(1)}'{m.group(2)}\" /km"

# Speed
m = re.search(r'(\d+[,\.]\d+)\s*km', text)
if m: data['avg_speed'] = f"{m.group(1)} km/h"

# Cadence - smart fix
m = re.search(r'(\d+)\s*steps?/min', text)
if m:
    cad = m.group(1)
    # Fix missing leading 1 (37 -> 137)
    if int(cad) < 100 and int(cad) > 20:
        cad = '1' + cad
    data['avg_cadence'] = f"{cad} steps/min"

# Stride
m = re.search(r'(\d+)\s*cm', text)
if m: data['avg_stride'] = f"{m.group(1)} cm"

# Steps
m = re.search(r'(\d+)[.,](\d+)\s*(?:steps?|seps)', text, re.I)
if m: data['steps'] = f"{m.group(1)}.{m.group(2)} steps"

# Heart rate
m = re.search(r'(\d+)\s*bpm', text)
if m: data['avg_heart_rate'] = f"{m.group(1)} bpm"

print(f"   ✓ Done: {(time.time()-t0)*1000:.0f}ms")

print("\n" + "="*60)
print("📋 HASIL EKSTRAKSI")
print("="*60)
for key, value in data.items():
    print(f"{key.replace('_', ' ').title():<20}: {value}")
print("="*60)
