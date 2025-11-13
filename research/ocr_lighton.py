import cv2
import time
import json
import re
from PIL import Image
import base64
import io

try:
    from llama_cpp import Llama
except ImportError:
    print("⚠️  Install: pip install llama-cpp-python")
    exit(1)

image_path = 'WhatsApp Image 2025-11-06 at 11.15.40.jpeg'

print("="*60)
print("🤖 LightOnOCR-1B (Vision OCR Model)")
print("="*60)

# Load LightOnOCR model
print("\n📦 Loading LightOnOCR-1B...")
t0 = time.time()
llm = Llama.from_pretrained(
    repo_id="noctrex/LightOnOCR-1B-1025-i1-GGUF",
    filename="LightOnOCR-1B-1025-i1-BF16.gguf",
    n_ctx=2048,
    n_threads=4,
    verbose=False
)
print(f"   ✓ Done: {(time.time()-t0)*1000:.0f}ms")

# Load image
print("\n📷 Loading image...")
t0 = time.time()
img = cv2.imread(image_path)
img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
pil_img = Image.fromarray(img_rgb)
print(f"   ✓ Done: {(time.time()-t0)*1000:.0f}ms")

# OCR with LightOnOCR
print("\n🔍 Running LightOnOCR...")
t0 = time.time()

# Convert image to base64
buffered = io.BytesIO()
pil_img.save(buffered, format="PNG")
img_base64 = base64.b64encode(buffered.getvalue()).decode()

prompt = f"""Extract all text from this fitness tracker image.
Return the text exactly as shown in the image."""

response = llm.create_chat_completion(
    messages=[
        {
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img_base64}"}}
            ]
        }
    ],
    max_tokens=500,
    temperature=0.1
)

text = response['choices'][0]['message']['content']
print(f"   ✓ Done: {(time.time()-t0)*1000:.0f}ms")

# Extract data with regex
print("\n📊 Extracting data...")
t0 = time.time()
data = {}

m = re.search(r'(\d{1,2})\s+(\w+)\s+(\d{4})\s+at\s+(\d{1,2}\.\d{2})', text)
if m: data['date'] = f"{m.group(1)} {m.group(2)} {m.group(3)} at {m.group(4)}"

m = re.search(r'(\d+[,\.]\d+)\s*km', text)
if m: data['distance'] = f"{m.group(1)} km"

m = re.search(r'(\d{2}):(\d{2}):(\d{2})', text)
if m: data['duration'] = f"{m.group(1)}:{m.group(2)}:{m.group(3)}"

m = re.search(r'(\d+)\s*(?:ca|kcal)', text, re.I)
if m: data['total_calories'] = f"{m.group(1)} kcal"

m = re.search(r"(\d+)'(\d+)\"", text)
if m: data['avg_pace'] = f"{m.group(1)}'{m.group(2)}\" /km"

speeds = re.findall(r'(\d+[,\.]\d+)\s*km', text)
if len(speeds) > 1: data['avg_speed'] = f"{speeds[1]} km/h"

m = re.search(r'(\d{2,3})\s*steps/min', text, re.I)
if m: data['avg_cadence'] = f"{m.group(1)} steps/min"

m = re.search(r'(\d+)\s*cm', text)
if m: data['avg_stride'] = f"{m.group(1)} cm"

m = re.search(r'(\d+)[.,](\d+)\s*steps', text, re.I)
if m: data['steps'] = f"{m.group(1)}.{m.group(2)} steps"

m = re.search(r'(\d{2,3})\s*bpm', text, re.I)
if m: data['avg_heart_rate'] = f"{m.group(1)} bpm"

print(f"   ✓ Done: {(time.time()-t0)*1000:.0f}ms")

print("\n" + "="*60)
print("📝 RAW OCR OUTPUT")
print("="*60)
print(text)
print("\n" + "="*60)
print("📋 HASIL EKSTRAKSI")
print("="*60)
for key, value in data.items():
    print(f"{key.replace('_', ' ').title():<20}: {value}")
print("="*60)
