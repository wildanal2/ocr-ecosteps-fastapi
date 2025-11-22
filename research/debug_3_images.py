#!/usr/bin/env python3
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.ocr_processor_local import process_ocr_local

images = [
    ("datasets/Fitbit/2025-11-22_072807_fitbit.jpg", "Fitbit", 11820),
    ("datasets/Samsung Health/487050330_122219410556233106_4344152826971809940_n.jpg", "Samsung Health", 3139),
    ("datasets/Huawei Health/0F10CFFE-6730-4E44-97B8-DB622286EE24_1_102_o.jpeg", "Huawei Health", 395),
]

for img_path, category, expected in images:
    full_path = f"/home/miew/Documents/Project/ocr-ecosteps/{img_path}"
    print("="*80)
    print(f"📁 {Path(img_path).name}")
    print(f"Expected: {expected}")
    print("-"*80)
    
    result = process_ocr_local(full_path, category)
    print(f"Detected: {result['extracted_data'].get('steps', 'NOT FOUND')}")
    print(f"App: {result['app_class']}")
    print(f"\nRaw OCR:\n{result['raw_ocr']}")
    print("="*80)
    print()
