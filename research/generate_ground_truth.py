#!/usr/bin/env python3
"""Generate ground truth from validated CSV"""
import csv
import sys

csv_file = sys.argv[1] if len(sys.argv) > 1 else "ocr_validation_20251122_124557.csv"

print("# Ground truth generated from:", csv_file)
print("GROUND_TRUTH = {")

with open(csv_file, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        file_name = row['file_name']
        steps = row['steps']
        category = row['category']
        print(f'    "{file_name}": {steps},  # {category}')

print("}")
