#!/usr/bin/env python3
from app.core.ocr_processor import process_ocr

test_cases = [
    ('Garmin Connect', '2025-11-25_093624_gw.jpg', 9920),
    ('Garmin Connect', '2025-11-25_093638_gw.png', 10514),
    ('Garmin Connect', '2025-11-25_093648_gw.jpg', 11998),
    ('Garmin Connect', '2025-11-25_093702_gw.jpg', 10300),
    ('Garmin Connect', '2025-11-25_093729_gw.png', 10514),
    ('Garmin Connect', '2025-11-25_093803_gw.png', 5432),
    ('Garmin Connect', '2025-11-25_093822_gw.png', 6336),
]

print('Testing Garmin Connect...\n')
correct = 0
for cat, fname, expected in test_cases:
    url = f'file://datasets/{cat}/{fname}'
    result = process_ocr(url)
    actual = result['extracted_data'].get('steps')
    app = result['app_class']
    status = '✓' if actual == expected else '✗'
    if actual == expected:
        correct += 1
    print(f'{status} {fname:40s} App: {app:20s} Expected: {expected:5d}, Got: {actual}')

print(f'\n{correct}/{len(test_cases)} correct ({correct/len(test_cases)*100:.1f}%)')
