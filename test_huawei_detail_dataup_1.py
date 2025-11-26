#!/usr/bin/env python3
from app.core.ocr_processor import process_ocr
# update dataset ke 1 huawei health detail 
test_cases = [
    ('Huawei Health', 'detail_2025-11-23_230929.jpg', 9708),
    ('Huawei Health', 'detail_2025-11-23_231355_detail.png', 5684),
    ('Huawei Health', 'detail_2025-11-24_112009_detail.jpg', 873), 
    ('Huawei Health', 'detail_2025-11-24_145628_detail.png', 2637),
    ('Huawei Health', 'detail_2025-11-24_213801_detail.jpg', 9708),
    ('Huawei Health', 'detail_2025-11-24_222506_detail.jpg', 5498),
    ('Huawei Health', 'detail_2025-11-25_082925_detail.jpg', 12477),
    ('Huawei Health', 'detail_2025-11-25_085124.jpg', 2858),
    ('Huawei Health', 'detail_2025-11-25_201622.png', 3253),
    ('Huawei Health', 'detail_2025-11-25_201713.png', 4097),
    ('Huawei Health', 'detail_2025-11-25_201816.png', 951),
]


print('Testing Huawei Health...\n')
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
