import cv2
import re
import time

try:
    from paddleocr import PaddleOCR
    PADDLE_AVAILABLE = True
except ImportError:
    PADDLE_AVAILABLE = False
    print("⚠️  Install: pip install paddlepaddle paddleocr")
    exit(1)

image_path = 'WhatsApp Image 2025-11-06 at 11.15.40.jpeg'

print("="*60)
print("🚀 PaddleOCR PROCESSING (Lightweight & Fast)")
print("="*60)

# Init PaddleOCR
print("\n📦 Loading PaddleOCR...")
t0 = time.time()
ocr = PaddleOCR(lang='en')
print(f"   ✓ Model loaded: {(time.time()-t0)*1000:.0f}ms")

# Preprocessing
print("\n🔧 Preprocessing...")
t0 = time.time()
img = cv2.imread(image_path)
img = cv2.resize(img, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
print(f"   ✓ Done: {(time.time()-t0)*1000:.0f}ms")

# OCR
print("\n🔍 Running PaddleOCR...")
t0 = time.time()
result = ocr.predict(img)
text = ' '.join([line[1][0] for line in result[0]])
print(f"   ✓ Completed: {(time.time()-t0)*1000:.0f}ms")

# Ekstraksi data
print("\n📊 Extracting data...")
t0 = time.time()
data = {}

m = re.search(r'(\d{1,2}\s+\w+\s+\d{4})\s+at\s+(\d{1,2}\.\d{2})', text)
if m: data['date'] = f"{m.group(1)} at {m.group(2)}"

m = re.search(r'(\d{2}):(\d{2}):(\d{2})', text)
if m: data['duration'] = f"{m.group(1)}:{m.group(2)}:{m.group(3)}"

m = re.search(r'(\d+)\s*(?:ca|kcal)', text, re.I)
if m: data['total_calories'] = f"{m.group(1)} kcal"

m = re.search(r"(\d+)'(\d+)\"\s*/km", text)
if m: data['avg_pace'] = f"{m.group(1)}'{m.group(2)}\" /km"

m = re.search(r'(\d+[,\.]\d+)\s*km', text)
if m: data['avg_speed'] = f"{m.group(1)} km/h"

m = re.search(r'(\d+)\s*steps?/min', text)
if m: data['avg_cadence'] = f"{m.group(1)} steps/min"

m = re.search(r'(\d+)\s*cm', text)
if m: data['avg_stride'] = f"{m.group(1)} cm"

m = re.search(r'(\d+)[.,](\d+)\s*(?:steps?|seps)', text, re.I)
if m: data['steps'] = f"{m.group(1)}.{m.group(2)} steps"

m = re.search(r'(\d+)\s*bpm', text)
if m: data['avg_heart_rate'] = f"{m.group(1)} bpm"

print(f"   ✓ Done: {(time.time()-t0)*1000:.0f}ms")

print("\n" + "="*60)
print("📋 HASIL EKSTRAKSI (PaddleOCR)")
print("="*60)
for key, value in data.items():
    print(f"{key.replace('_', ' ').title():<20}: {value}")
print("="*60)
print(f"\n📝 Raw OCR: {text[:200]}...")
