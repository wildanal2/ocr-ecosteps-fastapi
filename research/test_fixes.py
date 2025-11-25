#!/usr/bin/env python3
from app.core.ocr_processor import process_ocr

test_cases = [
    ('Google Fit', 'gogle_fit_20.55.10.jpeg', 589),
    ('Google Fit', '484822220_632215553109833_2297672382661628332_n.jpg', 7555),
    ('Google Fit', '494730497_9645386668876827_8603863592059978830_n.jpg', 16331),
    ('Google Fit', 'Eu9JMj8VcAIaqB9.jpeg', 16669),
    ('Google Fit', '509441112_3419385414870985_3021265621098066994_n.jpg', 18134),
    ('Huawei Health', '0F10CFFE-6730-4E44-97B8-DB622286EE24_1_102_o.jpeg', 395),
    ('Huawei Health', '2025-11-24_143136_huawei.png', 735),
    ('Apple Health', 'PHOTO-2025-11-10-14-38-52.jpg', 1211),
    ('Samsung Health', '499507250_24620207707567726_7253775697531596173_n.jpg', 7492),
]

print('Testing fixes...\n')
correct = 0
for cat, fname, expected in test_cases:
    url = f'file://datasets/{cat}/{fname}'
    result = process_ocr(url)
    actual = result['extracted_data'].get('steps')
    app = result['app_class']
    status = '✓' if actual == expected else '✗'
    if actual == expected:
        correct += 1
    print(f'{status} {fname[:45]:45s} App: {app:15s} Expected: {expected:5d}, Got: {actual}')

print(f'\n{correct}/{len(test_cases)} correct ({correct/len(test_cases)*100:.1f}%)')
