#!/usr/bin/env python3
"""
Add new image to ground truth
Usage: python add_new_image.py <image_path> [category]

Example:
  python add_new_image.py datasets/Fitbit/new_image.jpg
  python add_new_image.py datasets/Fitbit/new_image.jpg "Fitbit"
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.ocr_processor_local import process_ocr_local

def add_new_image(image_path, category=None):
    """Process new image and prompt for ground truth update"""
    
    # Detect category from path if not provided
    if not category:
        path_parts = Path(image_path).parts
        if 'datasets' in path_parts:
            idx = path_parts.index('datasets')
            if idx + 1 < len(path_parts):
                category = path_parts[idx + 1]
    
    file_name = Path(image_path).name
    
    print("="*80)
    print("🔬 PROCESSING NEW IMAGE")
    print("="*80)
    print(f"File:     {file_name}")
    print(f"Category: {category}")
    print(f"Path:     {image_path}")
    print("="*80)
    print()
    
    # Process OCR
    print("⏳ Running OCR...")
    try:
        result = process_ocr_local(image_path, category)
        
        steps = result['extracted_data'].get('steps', 'NOT FOUND')
        app_class = result['app_class']
        raw_ocr = result['raw_ocr'][:150]
        
        print()
        print("="*80)
        print("📊 OCR RESULTS")
        print("="*80)
        print(f"App Class:  {app_class}")
        print(f"Steps:      {steps}")
        print(f"Raw OCR:    {raw_ocr}...")
        print("="*80)
        print()
        
        # Prompt for confirmation
        print("❓ KONFIRMASI:")
        print(f"   Apakah steps {steps} sudah benar?")
        print()
        print("   Jika benar, update ground truth dengan:")
        print()
        print("   1. Edit datasets/DATASET_GROUND_TRUTH.md:")
        print(f"      | {file_name} | {steps} | [notes] |")
        print()
        print("   2. Edit research/validate_against_ground_truth.py:")
        print(f'      "{file_name}": {steps},  # {category}')
        print()
        print("   3. Run validation:")
        print("      python research/validate_against_ground_truth.py")
        print()
        print("="*80)
        
        # Generate update snippets
        print()
        print("📋 COPY-PASTE SNIPPETS:")
        print("-"*80)
        print("For DATASET_GROUND_TRUTH.md:")
        print(f"| {file_name} | {steps} | Standard format |")
        print()
        print("For validate_against_ground_truth.py:")
        print(f'    "{file_name}": {steps},  # {category}')
        print("="*80)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python add_new_image.py <image_path> [category]")
        print()
        print("Examples:")
        print("  python add_new_image.py datasets/Fitbit/new_image.jpg")
        print("  python add_new_image.py datasets/Fitbit/new_image.jpg 'Fitbit'")
        sys.exit(1)
    
    image_path = sys.argv[1]
    category = sys.argv[2] if len(sys.argv) > 2 else None
    
    add_new_image(image_path, category)
