#!/usr/bin/env python3
"""
Analyze OCR validation results from CSV
Calculate accuracy, success rate, and per-category statistics
"""

import csv
import sys
from pathlib import Path
from collections import defaultdict

def analyze_csv(csv_file):
    """Analyze validation results"""
    print("="*80)
    print("📊 OCR RESULTS ANALYSIS")
    print("="*80)
    print(f"📁 File: {csv_file}")
    print("="*80)
    print()
    
    # Read CSV
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    
    if not rows:
        print("❌ No data found in CSV")
        return
    
    total = len(rows)
    success = sum(1 for r in rows if r['status'] == 'SUCCESS')
    errors = total - success
    
    # Per category stats
    category_stats = defaultdict(lambda: {'total': 0, 'success': 0, 'steps_found': 0})
    
    for row in rows:
        cat = row['category']
        category_stats[cat]['total'] += 1
        if row['status'] == 'SUCCESS':
            category_stats[cat]['success'] += 1
        if row.get('steps'):
            category_stats[cat]['steps_found'] += 1
    
    # Overall stats
    print("📈 OVERALL STATISTICS")
    print("-"*80)
    print(f"Total images:        {total}")
    print(f"✓ Success:           {success} ({success/total*100:.1f}%)")
    print(f"✗ Errors:            {errors} ({errors/total*100:.1f}%)")
    print()
    
    steps_found = sum(1 for r in rows if r.get('steps'))
    print(f"Steps extracted:     {steps_found} ({steps_found/total*100:.1f}%)")
    print()
    
    # Processing time stats
    times = [int(r['processing_time_ms']) for r in rows if r.get('processing_time_ms')]
    if times:
        avg_time = sum(times) / len(times)
        min_time = min(times)
        max_time = max(times)
        print(f"Avg processing time: {avg_time:.0f}ms")
        print(f"Min/Max time:        {min_time}ms / {max_time}ms")
    print()
    
    # Per category breakdown
    print("="*80)
    print("📊 PER CATEGORY BREAKDOWN")
    print("="*80)
    print(f"{'Category':<25} {'Total':<8} {'Success':<10} {'Steps Found':<12} {'Success %'}")
    print("-"*80)
    
    for cat in sorted(category_stats.keys()):
        stats = category_stats[cat]
        success_rate = stats['success'] / stats['total'] * 100 if stats['total'] > 0 else 0
        print(f"{cat:<25} {stats['total']:<8} {stats['success']:<10} {stats['steps_found']:<12} {success_rate:.1f}%")
    
    print("="*80)
    print()
    
    # App classification accuracy
    print("📱 APP CLASSIFICATION")
    print("-"*80)
    app_counts = defaultdict(int)
    for row in rows:
        if row.get('app_class'):
            app_counts[row['app_class']] += 1
    
    for app, count in sorted(app_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"{app:<25}: {count} images")
    print()
    
    # Errors breakdown
    if errors > 0:
        print("="*80)
        print("❌ ERRORS BREAKDOWN")
        print("="*80)
        error_rows = [r for r in rows if r['status'] == 'ERROR']
        for row in error_rows:
            print(f"• {row['category']}/{row['file_name']}")
            print(f"  Error: {row.get('error_message', 'Unknown')}")
            print()
    
    # Missing steps
    missing_steps = [r for r in rows if r['status'] == 'SUCCESS' and not r.get('steps')]
    if missing_steps:
        print("="*80)
        print("⚠️  SUCCESS BUT NO STEPS EXTRACTED")
        print("="*80)
        for row in missing_steps:
            print(f"• {row['category']}/{row['file_name']}")
            print(f"  App: {row.get('app_class', 'Unknown')}")
            if row.get('raw_ocr'):
                print(f"  OCR: {row['raw_ocr'][:100]}...")
            print()
    
    print("="*80)
    print("✅ Analysis completed!")
    print()
    print("💡 Tips:")
    print("  - Review errors and missing steps")
    print("  - Check if app classification is correct")
    print("  - Update regex patterns if needed")
    print("  - Re-run batch processing after improvements")
    print("="*80)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        # Find latest CSV
        csv_files = sorted(Path('.').glob('ocr_validation_*.csv'), reverse=True)
        if csv_files:
            csv_file = csv_files[0]
            print(f"📁 Using latest CSV: {csv_file}")
            print()
        else:
            print("Usage: python analyze_results.py <csv_file>")
            print("   or: python analyze_results.py  (uses latest CSV)")
            sys.exit(1)
    else:
        csv_file = sys.argv[1]
    
    try:
        analyze_csv(csv_file)
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
