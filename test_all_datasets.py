#!/usr/bin/env python3
import csv
from app.core.ocr_processor import process_ocr
from collections import defaultdict

# Read ground truth
test_cases = []
with open('datasets/ground_truth.csv', 'r', encoding='utf-8') as f:
    reader = csv.reader(f)
    for row in reader:
        if len(row) >= 3 and row[0] and row[1] and row[2]:
            try:
                test_cases.append((row[0], row[1], int(row[2])))
            except ValueError:
                continue

print(f'Testing {len(test_cases)} images from ground_truth.csv\n')
print('=' * 110)

correct = 0
total_time = 0
results_by_app = defaultdict(lambda: {'correct': 0, 'total': 0, 'failed': []})

for i, (category, fname, expected) in enumerate(test_cases, 1):
    url = f'file://datasets/{category}/{fname}'
    try:
        result = process_ocr(url)
        actual = result['extracted_data'].get('steps')
        app = result['app_class']
        time_ms = result['processing_time_ms']
        
        status = '✓' if actual == expected else '✗'
        if actual == expected:
            correct += 1
            results_by_app[app]['correct'] += 1
        else:
            results_by_app[app]['failed'].append((fname, expected, actual))
        
        results_by_app[app]['total'] += 1
        total_time += time_ms
        
        print(f'{i:3d}. {status} {fname:50s} App: {app:20s} Expected: {expected:6d}, Got: {actual}')
    except Exception as e:
        print(f'{i:3d}. ✗ {fname:50s} ERROR: {str(e)[:50]}')
        results_by_app[category]['total'] += 1
        results_by_app[category]['failed'].append((fname, expected, 'ERROR'))

print('=' * 110)
print(f'\nOVERALL RESULTS:')
print(f'Total: {correct}/{len(test_cases)} correct')
print(f'Accuracy: {correct/len(test_cases)*100:.1f}%')
print(f'Avg Time: {total_time/len(test_cases):.0f}ms')
print(f'Total Time: {total_time/1000:.1f}s')

print(f'\n\nRESULTS BY APP:')
print('-' * 110)
for app in sorted(results_by_app.keys()):
    stats = results_by_app[app]
    acc = stats['correct']/stats['total']*100 if stats['total'] > 0 else 0
    print(f'{app:20s}: {stats["correct"]:3d}/{stats["total"]:3d} ({acc:5.1f}%)')
    if stats['failed']:
        for fname, exp, act in stats['failed'][:3]:
            print(f'  ✗ {fname:45s} Expected: {exp:6}, Got: {act}')
        if len(stats['failed']) > 3:
            print(f'  ... and {len(stats["failed"])-3} more failures')

print('\n' + '=' * 110)
