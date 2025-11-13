import cv2
import re
import time

try:
    import easyocr
    EASYOCR_AVAILABLE = True
except ImportError:
    EASYOCR_AVAILABLE = False
    print("⚠️  Install: pip install easyocr")
    exit(1)

image_path = 'WhatsApp Image 2025-11-06 at 11.15.40.jpeg'

print("="*60)
print("🚀 EasyOCR PROCESSING")
print("="*60)

# Init EasyOCR
print("\n📦 Loading EasyOCR...")
t0 = time.time()
reader = easyocr.Reader(['en'], gpu=False)
print(f"   ✓ Model loaded: {(time.time()-t0)*1000:.0f}ms")

# Preprocessing (RGB)
print("\n🔧 Preprocessing...")
t0 = time.time()
img = cv2.imread(image_path)
img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
img_rgb = cv2.resize(img_rgb, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
print(f"   ✓ Done: {(time.time()-t0)*1000:.0f}ms")

# OCR
print("\n🔍 Running EasyOCR...")
t0 = time.time()
results = reader.readtext(img_rgb)
text = ' '.join([res[1] for res in results])
print(f"   ✓ Completed: {(time.time()-t0)*1000:.0f}ms")

# Ekstraksi data
print("\n📊 Extracting data...")
t0 = time.time()
data = {}

# Date
m = re.search(r'(\d{1,2}\s+\w+\s+\d{4})\s+at\s+(\d{1,2}\.\d{2})', text)
if m: data['date'] = f"{m.group(1)} at {m.group(2)}"

# Distance (text terbesar setelah tanggal, format: X,XX km)
dist_matches = re.findall(r'(\d+[,\.]\d+)\s*km', text)
if dist_matches:
    # Ambil yang pertama (biasanya distance utama)
    data['distance'] = f"{dist_matches[0]} km"

# Duration
m = re.search(r'(\d{2}):(\d{2}):(\d{2})', text)
if m: data['duration'] = f"{m.group(1)}:{m.group(2)}:{m.group(3)}"

# Calories
m = re.search(r'(\d+)\s*(?:ca|kcal)', text, re.I)
if m: data['total_calories'] = f"{m.group(1)} kcal"

# Pace
m = re.search(r"(\d+)'(\d+)\"\s*/km", text)
if m: data['avg_pace'] = f"{m.group(1)}'{m.group(2)}\" /km"

# Speed
m = re.search(r'(\d+[,\.]\d+)\s*km[/\\]?[mh]', text)
if m: data['avg_speed'] = f"{m.group(1)} km/h"

# Cadence
m = re.search(r'(\d+)\s*steps?/min', text)
if m: data['avg_cadence'] = f"{m.group(1)} steps/min"

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
print("📝 RAW OCR OUTPUT")
print("="*60)
print(text)
print("\n" + "="*60)
print("📋 HASIL EKSTRAKSI (EasyOCR)")
print("="*60)
for key, value in data.items():
    print(f"{key.replace('_', ' ').title():<20}: {value}")
print("="*60)
