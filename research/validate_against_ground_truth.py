#!/usr/bin/env python3
"""
Validate OCR results against ground truth dataset
Usage: python validate_against_ground_truth.py [csv_file]
"""

import csv
import sys
from pathlib import Path

# Ground truth data (validated 2025-11-22)
GROUND_TRUTH = {
    # Apple Health
    "WhatsApp Image 2025-11-10 at 12.02.53.jpeg": 646,
    "appple_12333.jpeg": 10818,
    "PHOTO-2025-11-10-14-38-52.jpg": 1211,
    "6FD6E71B-25FB-4B85-9ACE-6700C51E31DF_1_102_o.jpeg": 736,
    "0B9728E2-0BDD-46A1-B30F-9DC87A3E9FC1_1_102_o.jpeg": 401,
    "2025-11-21_232346_apple.png": 14578,
    "WhatsApp Image 2025-11-10 at 12.04.38.jpeg": 640,
    # Apple Health Old
    "2025-11-22_074136_apple.png": 12515,
    # Fitbit
    "2025-11-22_072807_fitbit.jpg": 11820,
    "20.55.12_fitbit.jpeg": 4324,
    # Google Fit
    "461231351_8213834741985150_3244851168804879399_n.jpg": 5073,
    "G480QJzWEAAS-Wk.jpeg": 5548,
    "googlefit_20.55.11.jpeg": 827,
    "484822220_632215553109833_2297672382661628332_n.jpg": 7555,
    "google_fit_1122.jpeg": 16828,
    "Eu9JMj8VcAIaqB9.jpeg": 16669,
    "google_fit_11223.jpeg": 13924,
    "googlefit_123123panjang.jpeg": 2566,
    "494730497_9645386668876827_8603863592059978830_n.jpg": 16331,
    "gogle_fit_20.55.10.jpeg": 589,
    "509441112_3419385414870985_3021265621098066994_n.jpg": 18134,
    # Huawei Health
    "huawei_1122.jpeg": 498,
    "0F10CFFE-6730-4E44-97B8-DB622286EE24_1_102_o.jpeg": 395,
    "huawei_.jpeg": 8376,
    "huawei_12.jpeg": 376,
    # Samsung Health
    "499507250_24620207707567726_7253775697531596173_n.jpg": 7492,
    "487050330_122219410556233106_4344152826971809940_n.jpg": 3139,
    "2025-11-21_233701_samsung.jpg": 17029,
    "2025-11-21_234704_samsung.jpg": 6155,
    "518276064_1848906432355507_829745813346950310_n.jpg": 1035,
    "499260930_24620208160901014_235439803812869537_n.jpg": 7492,
}

def validate(csv_file):
    """Validate OCR results against ground truth"""
    print("="*80)
    print("🔍 VALIDATING AGAINST GROUND TRUTH")
    print("="*80)
    print(f"Ground truth entries: {len(GROUND_TRUTH)}")
    print(f"CSV file: {csv_file}")
    print("="*80)
    print()
    
    matches = 0
    mismatches = []
    missing = []
    
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            file_name = row['file_name']
            detected = row.get('steps', '')
            
            if file_name not in GROUND_TRUTH:
                missing.append(file_name)
                continue
            
            expected = GROUND_TRUTH[file_name]
            
            # Convert to int for comparison
            try:
                detected_int = int(detected) if detected else None
            except:
                detected_int = None
            
            if detected_int == expected:
                matches += 1
                print(f"✓ {file_name}: {detected} (correct)")
            else:
                mismatches.append({
                    'file': file_name,
                    'expected': expected,
                    'detected': detected_int,
                    'category': row.get('category', 'Unknown')
                })
                print(f"✗ {file_name}: expected {expected}, got {detected}")
    
    print()
    print("="*80)
    print("📊 VALIDATION SUMMARY")
    print("="*80)
    print(f"Total ground truth: {len(GROUND_TRUTH)}")
    print(f"✓ Matches:          {matches} ({matches/len(GROUND_TRUTH)*100:.1f}%)")
    print(f"✗ Mismatches:       {len(mismatches)}")
    print(f"⚠ Missing:          {len(missing)}")
    print("="*80)
    
    if mismatches:
        print()
        print("❌ MISMATCHES DETAILS:")
        print("-"*80)
        for m in mismatches:
            print(f"  {m['category']}/{m['file']}")
            print(f"    Expected: {m['expected']}")
            print(f"    Detected: {m['detected']}")
            print()
    
    if missing:
        print()
        print("⚠️  MISSING FROM GROUND TRUTH:")
        print("-"*80)
        for f in missing:
            print(f"  - {f}")
    
    print()
    if len(mismatches) == 0 and len(missing) == 0:
        print("✅ ALL VALIDATIONS PASSED!")
    else:
        print("⚠️  VALIDATION FAILED - Please review mismatches")
    print("="*80)
    
    return len(mismatches) == 0

if __name__ == "__main__":
    # Find latest CSV or use provided
    if len(sys.argv) > 1:
        csv_file = sys.argv[1]
    else:
        csv_files = sorted(Path('.').glob('ocr_validation_*.csv'), reverse=True)
        if csv_files:
            csv_file = csv_files[0]
            print(f"📁 Using latest CSV: {csv_file}\n")
        else:
            print("❌ No CSV files found")
            print("Usage: python validate_against_ground_truth.py [csv_file]")
            sys.exit(1)
    
    success = validate(csv_file)
    sys.exit(0 if success else 1)
