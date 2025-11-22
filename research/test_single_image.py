#!/usr/bin/env python3
"""
Quick test single image OCR
Usage: python test_single_image.py <image_path> [category]
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.ocr_processor_local import process_ocr_local

def test_single_image(image_path: str, category: str = None):
    """Test OCR on single image"""
    print("="*80)
    print("🔬 SINGLE IMAGE OCR TEST")
    print("="*80)
    print(f"📁 Image: {image_path}")
    print(f"📂 Category: {category or 'Auto-detect'}")
    print("="*80)
    print()
    
    try:
        result = process_ocr_local(image_path, category)
        
        print("✅ OCR COMPLETED")
        print("="*80)
        print(f"📱 App Class: {result['app_class']}")
        print(f"⏱  Processing Time: {result['processing_time_ms']}ms")
        print()
        
        print("📊 EXTRACTED DATA:")
        print("-"*80)
        extracted = result['extracted_data']
        if extracted:
            for key, value in extracted.items():
                print(f"  {key.replace('_', ' ').title():<20}: {value}")
        else:
            print("  No data extracted")
        print()
        
        print("📝 RAW OCR TEXT:")
        print("-"*80)
        print(result['raw_ocr'])
        print("="*80)
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_single_image.py <image_path> [category]")
        print()
        print("Examples:")
        print("  python test_single_image.py /path/to/image.jpg")
        print("  python test_single_image.py /path/to/image.jpg 'Google Fit'")
        sys.exit(1)
    
    img_path = sys.argv[1]
    category = sys.argv[2] if len(sys.argv) > 2 else None
    
    test_single_image(img_path, category)
