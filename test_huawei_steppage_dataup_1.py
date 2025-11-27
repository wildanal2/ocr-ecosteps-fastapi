#!/usr/bin/env python3
from app.core.ocr_processor import process_ocr
# update dataset ke 1 huawei health detail 
test_cases = [
    ('Huawei Health','steppage_2025-11-26_061318_huawei.jpg', 9703),
    ('Huawei Health','steppage_2025-11-26_193650_huawei.jpg', 11328),
    ('Huawei Health','steppage_2025-11-26_193809_huawei.png', 3011),
    ('Huawei Health','steppage_2025-11-26_220319_huawei.png', 9936),
    ('Huawei Health','steppage_2025-11-26_225148_huawei.png', 16452),
    ('Huawei Health','steppage_2025-11-27_065659_huawei.jpg', 10386),
    ('Huawei Health','steppage_2025-11-27_084327_huawei.jpg', 4141),
    ('Huawei Health','steppage_2025-11-27_123147_huawei.jpg', 8039),
    ('Huawei Health','steppage_2025-11-27_123222_huawei.jpg', 6170),
    ('Huawei Health','steppage_2025-11-27_132728_huawei.png', 8265),
    ('Huawei Health','steppage_2025-11-27_133223_huawei.png', 5655),
    ('Huawei Health','steppage_2025-11-27_133716_huawei.jpg', 2627),
    ('Huawei Health','steppage_2025-11-27_161357_huawei.png', 3354),
    ('Huawei Health','steppage_2025-11-27_161413_huawei.png', 3026),
]





print('Testing Huawei Health Step Page...\n')
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
