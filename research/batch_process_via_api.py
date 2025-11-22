#!/usr/bin/env python3
"""
Batch OCR Processing via API Endpoint
Hit /api/v1/ocr-ecosteps/local endpoint for each image
"""

import os
import csv
import time
import httpx
from pathlib import Path
from datetime import datetime

# Configuration
API_BASE_URL = "http://localhost:8000"
API_ENDPOINT = "/api/v1/ocr-ecosteps/local"
DATASETS_DIR = "/home/miew/Documents/Project/ocr-ecosteps/datasets"
OUTPUT_CSV = f"/home/miew/Documents/Project/ocr-ecosteps/research/ocr_validation_api_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

# Get API key from environment
API_KEY = os.getenv("API_KEY", "your-secret-api-key-here")

# Image extensions
IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp'}

def get_all_images():
    """Scan datasets directory and return all image files with categories"""
    images = []
    
    for category_dir in Path(DATASETS_DIR).iterdir():
        if not category_dir.is_dir():
            continue
            
        category = category_dir.name
        print(f"📁 Scanning category: {category}")
        
        for img_file in category_dir.iterdir():
            if img_file.suffix.lower() in IMAGE_EXTENSIONS:
                images.append({
                    'category': category,
                    'file_path': str(img_file),
                    'file_name': img_file.name
                })
        
        print(f"   Found {len([i for i in images if i['category'] == category])} images")
    
    return images

def process_via_api():
    """Process all images via API and save to CSV"""
    print("="*80)
    print("🔬 OCR BATCH PROCESSING VIA API - RESEARCH & VALIDATION")
    print("="*80)
    print(f"🌐 API URL: {API_BASE_URL}{API_ENDPOINT}")
    print(f"📂 Dataset directory: {DATASETS_DIR}")
    print(f"💾 Output CSV: {OUTPUT_CSV}")
    print()
    
    # Get all images
    images = get_all_images()
    total = len(images)
    
    if total == 0:
        print("❌ No images found!")
        return
    
    print(f"\n✓ Total images to process: {total}")
    print("="*80)
    print()
    
    # Prepare CSV
    csv_headers = [
        'no',
        'category',
        'file_name',
        'file_path',
        'app_class',
        'steps',
        'date',
        'distance',
        'duration',
        'total_calories',
        'avg_pace',
        'avg_speed',
        'avg_cadence',
        'avg_stride',
        'avg_heart_rate',
        'processing_time_ms',
        'raw_ocr',
        'status',
        'error_message'
    ]
    
    results = []
    success_count = 0
    error_count = 0
    start_time = time.time()
    
    # HTTP client
    client = httpx.Client(timeout=60.0)
    
    # Process each image
    for idx, img_info in enumerate(images, 1):
        category = img_info['category']
        file_path = img_info['file_path']
        file_name = img_info['file_name']
        
        print(f"[{idx}/{total}] Processing: {category}/{file_name}")
        
        try:
            # Call API
            response = client.post(
                f"{API_BASE_URL}{API_ENDPOINT}",
                json={
                    "img_path": file_path,
                    "category": category
                },
                headers={"X-API-Key": API_KEY}
            )
            response.raise_for_status()
            result = response.json()
            
            # Extract data
            extracted = result.get('extracted_data', {})
            
            row = {
                'no': idx,
                'category': category,
                'file_name': file_name,
                'file_path': file_path,
                'app_class': result.get('app_class', ''),
                'steps': extracted.get('steps', ''),
                'date': extracted.get('date', ''),
                'distance': extracted.get('distance', ''),
                'duration': extracted.get('duration', ''),
                'total_calories': extracted.get('total_calories', ''),
                'avg_pace': extracted.get('avg_pace', ''),
                'avg_speed': extracted.get('avg_speed', ''),
                'avg_cadence': extracted.get('avg_cadence', ''),
                'avg_stride': extracted.get('avg_stride', ''),
                'avg_heart_rate': extracted.get('avg_heart_rate', ''),
                'processing_time_ms': result.get('processing_time_ms', ''),
                'raw_ocr': result.get('raw_ocr', ''),
                'status': 'SUCCESS',
                'error_message': ''
            }
            
            results.append(row)
            success_count += 1
            print(f"   ✓ Success - App: {row['app_class']}, Steps: {row['steps']}, Time: {row['processing_time_ms']}ms")
            
        except Exception as e:
            error_count += 1
            row = {
                'no': idx,
                'category': category,
                'file_name': file_name,
                'file_path': file_path,
                'app_class': '',
                'steps': '',
                'date': '',
                'distance': '',
                'duration': '',
                'total_calories': '',
                'avg_pace': '',
                'avg_speed': '',
                'avg_cadence': '',
                'avg_stride': '',
                'avg_heart_rate': '',
                'processing_time_ms': '',
                'raw_ocr': '',
                'status': 'ERROR',
                'error_message': str(e)
            }
            results.append(row)
            print(f"   ✗ Error: {e}")
        
        print()
    
    client.close()
    
    # Save to CSV
    print("="*80)
    print("💾 Saving results to CSV...")
    
    with open(OUTPUT_CSV, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=csv_headers)
        writer.writeheader()
        writer.writerows(results)
    
    total_time = time.time() - start_time
    
    # Summary
    print("="*80)
    print("📊 PROCESSING SUMMARY")
    print("="*80)
    print(f"Total images:     {total}")
    print(f"✓ Success:        {success_count}")
    print(f"✗ Errors:         {error_count}")
    print(f"⏱ Total time:     {total_time:.2f}s")
    print(f"⚡ Avg time/img:   {(total_time/total):.2f}s")
    print(f"\n💾 Results saved to: {OUTPUT_CSV}")
    print("="*80)
    print("\n✅ Batch processing completed!")
    print("📋 Please validate the results manually in the CSV file.")

if __name__ == "__main__":
    try:
        process_via_api()
    except KeyboardInterrupt:
        print("\n\n⚠️  Processing interrupted by user")
        exit(1)
    except Exception as e:
        print(f"\n\n❌ Fatal error: {e}")
        exit(1)
