import cv2
import time
import json

try:
    import easyocr
    from transformers import AutoModelForCausalLM, AutoTokenizer
    import torch
except ImportError:
    print("⚠️  Install: pip install easyocr transformers torch")
    exit(1)

image_path = 'WhatsApp Image 2025-11-06 at 11.15.40.jpeg'

print("="*60)
print("🤖 OCR + TinyLLM (1.1B)")
print("="*60)

# Load EasyOCR
print("\n📦 Loading EasyOCR...")
t0 = time.time()
reader = easyocr.Reader(['en'], gpu=False)
print(f"   ✓ Done: {(time.time()-t0)*1000:.0f}ms")

# Load TinyLlama 1.1B
print("\n📦 Loading TinyLlama 1.1B...")
t0 = time.time()
model_name = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype=torch.float32,
    device_map="cpu",
    low_cpu_mem_usage=True
)
print(f"   ✓ Done: {(time.time()-t0)*1000:.0f}ms")

# OCR
print("\n🔍 Running OCR...")
t0 = time.time()
img = cv2.imread(image_path)
img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
img_rgb = cv2.resize(img_rgb, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
results = reader.readtext(img_rgb)
text = ' '.join([res[1] for res in results])
print(f"   ✓ Done: {(time.time()-t0)*1000:.0f}ms")

# LLM Extraction
print("\n🧠 Running LLM extraction...")
t0 = time.time()

prompt = f"""<|system|>
Extract fitness data from OCR text. Return valid JSON only.</s>
<|user|>
OCR: {text}

Extract: date, distance, duration, total_calories, avg_pace, avg_speed, avg_cadence, avg_stride, steps, avg_heart_rate</s>
<|assistant|>
"""

inputs = tokenizer(prompt, return_tensors="pt", return_attention_mask=True)
outputs = model.generate(
    **inputs,
    max_new_tokens=250,
    temperature=0.1,
    do_sample=False,
    pad_token_id=tokenizer.eos_token_id
)
response = tokenizer.decode(outputs[0], skip_special_tokens=True)
print(f"   ✓ Done: {(time.time()-t0)*1000:.0f}ms")

# Parse LLM response
try:
    json_start = response.find('{')
    json_end = response.rfind('}') + 1
    if json_start != -1 and json_end > json_start:
        json_str = response[json_start:json_end]
        data = json.loads(json_str)
    else:
        data = {}
except:
    data = {}

print("\n" + "="*60)
print("📝 RAW OCR OUTPUT")
print("="*60)
print(text)
print("\n" + "="*60)
print("🤖 LLM RESPONSE")
print("="*60)
print(response[len(prompt):])
print("\n" + "="*60)
print("📋 HASIL EKSTRAKSI (LLM)")
print("="*60)
for key, value in data.items():
    print(f"{key.replace('_', ' ').title():<20}: {value}")
print("="*60)
