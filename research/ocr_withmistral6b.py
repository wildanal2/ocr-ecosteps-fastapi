import cv2
import re
import time
from transformers import AutoModelForCausalLM, AutoTokenizer

try:
    import easyocr
except ImportError:
    print("⚠️  Install: pip install easyocr")
    exit(1)

# === CONFIG ===
IMAGE_PATH = 'WhatsApp Image 2025-11-06 at 11.15.40.jpeg'
MODEL_NAME = "openai-community/gpt2"   # <1B parameter
USE_GPU = False

print("="*60)
print("⚡ OCR + LLM SMART PIPELINE")
print("="*60)

# --- STEP 1. EasyOCR ---
print("\n📦 Loading EasyOCR...")
reader = easyocr.Reader(['en'], gpu=USE_GPU)
img = cv2.imread(IMAGE_PATH)
img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
img_rgb = cv2.resize(img_rgb, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)

results = reader.readtext(img_rgb)
raw_text = ' '.join([res[1] for res in results])

print("\n📝 RAW OCR OUTPUT:")
print(raw_text)

# --- STEP 2. LLM Refinement ---
print("\n🧠 Refining text with LLM (DistilMistral)...")

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForCausalLM.from_pretrained(MODEL_NAME)

prompt = f"""
You are a data extraction assistant.
Extract the following information from the OCR text below, and return in JSON format:

OCR TEXT:
{raw_text}

FIELDS:
- date
- distance (in km)
- duration
- total_calories (in kcal)
- avg_pace (/km)
- avg_speed (km/h)
- avg_cadence (steps/min)
- avg_stride (cm)
- steps
- avg_heart_rate (bpm)
"""

inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=1024)
outputs = model.generate(**inputs, max_new_tokens=300)
result_text = tokenizer.decode(outputs[0], skip_special_tokens=True)

print("\n📋 LLM OUTPUT (Refined Extraction):")
print(result_text)
