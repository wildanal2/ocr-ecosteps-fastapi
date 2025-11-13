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
print("🤖 OCR + Mini LLM Processing")
print("="*60)

# Load EasyOCR
print("\n📦 Loading EasyOCR...")
t0 = time.time()
reader = easyocr.Reader(['en'], gpu=False)
print(f"   ✓ Done: {(time.time()-t0)*1000:.0f}ms")

# Load Mini LLM (Phi-2 atau TinyLlama)
print("\n📦 Loading Mini LLM (Phi-2)...")
t0 = time.time()
model_name = "microsoft/phi-2"
tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype=torch.float32,
    device_map="cpu",
    trust_remote_code=True
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

prompt = f"""Extract structured data from this fitness tracker OCR text.

OCR Text: {text}

Extract and return ONLY a JSON object with these fields:
- date (format: "DD Month YYYY at HH.MM")
- distance (format: "X.XX km")
- duration (format: "HH:MM:SS")
- total_calories (format: "XXX kcal")
- avg_pace (format: "M'SS\\" /km")
- avg_speed (format: "X.XX km/h")
- avg_cadence (format: "XXX steps/min")
- avg_stride (format: "XX cm")
- steps (format: "X.XXX steps")
- avg_heart_rate (format: "XXX bpm")

JSON:"""

inputs = tokenizer(prompt, return_tensors="pt")
outputs = model.generate(
    inputs.input_ids,
    max_new_tokens=300,
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
