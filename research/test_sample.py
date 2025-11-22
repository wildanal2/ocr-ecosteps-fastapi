#!/usr/bin/env python3
"""Quick test with 3 sample images"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.ocr_processor_local import process_ocr_local

# Test 3 samples from different categories
samples = [
    ("datasets/Google Fit/google_fit_1122.jpeg", "Google Fit"),
    ("datasets/Apple Health/appple_12333.jpeg", "Apple Health"),
    ("datasets/Samsung Health/2025-11-21_233701_samsung.jpg", "Samsung Health"),
]

print("="*80)
print("🔬 TESTING 3 SAMPLE IMAGES")
print("="*80)

for img_path, category in samples:
    full_path = f"/home/miew/Documents/Project/ocr-ecosteps/{img_path}"
    print(f"\n📁 {category}/{Path(img_path).name}")
    print("-"*80)
    
    try:
        result = process_ocr_local(full_path, category)
        print(f"✓ App: {result['app_class']}")
        print(f"✓ Steps: {result['extracted_data'].get('steps', 'NOT FOUND')}")
        print(f"✓ Time: {result['processing_time_ms']}ms")
        print(f"✓ Raw OCR (first 150 chars): {result['raw_ocr'][:150]}...")
    except Exception as e:
        print(f"✗ Error: {e}")

print("\n" + "="*80)
