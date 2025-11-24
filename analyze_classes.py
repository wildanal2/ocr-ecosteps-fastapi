import csv
import re
from collections import defaultdict

with open('datasets/ground_truth.csv', 'r') as f:
    data = list(csv.DictReader(f))

patterns = defaultdict(lambda: {'count': 0, 'samples': [], 'keywords': set()})

for row in data:
    cat = row['category']
    text = row['raw_ocr_sample'].lower()
    patterns[cat]['count'] += 1
    
    # Deteksi keyword unik
    if 'summary' in text or 'ringkasan' in text:
        patterns[cat]['keywords'].add('summary/ringkasan')
    if 'health data' in text or 'show all' in text:
        patterns[cat]['keywords'].add('health_data')
    if 'activity rings' in text or 'cincin aktivitas' in text:
        patterns[cat]['keywords'].add('activity_rings')
    if 'move' in text and 'kcal' in text:
        patterns[cat]['keywords'].add('move_kcal')
    if 'exercise' in text and 'stand' in text:
        patterns[cat]['keywords'].add('exercise_stand')
    if 'poin kardio' in text or 'heart pts' in text:
        patterns[cat]['keywords'].add('heart_points')
    if 'langkah' in text and 'poin' in text:
        patterns[cat]['keywords'].add('indo_langkah')
    if 'samsung health' in text:
        patterns[cat]['keywords'].add('samsung_brand')
    if 'fitbit' in text:
        patterns[cat]['keywords'].add('fitbit_brand')
    if 'steps' in text and 'mood' in text:
        patterns[cat]['keywords'].add('huawei_mood')
    if 'todays steps' in text or "today's steps" in text:
        patterns[cat]['keywords'].add('todays_steps')
    if 'daily activity' in text:
        patterns[cat]['keywords'].add('daily_activity')
    
    if len(patterns[cat]['samples']) < 2:
        patterns[cat]['samples'].append(text[:80])

print("="*80)
print("ANALISIS KATEGORI APLIKASI")
print("="*80)

for cat in sorted(patterns.keys()):
    p = patterns[cat]
    print(f"\n{cat} ({p['count']} data)")
    print(f"  Keywords: {', '.join(sorted(p['keywords']))}")
    print(f"  Sample: {p['samples'][0][:70]}...")

# Analisis similarity
print("\n" + "="*80)
print("REKOMENDASI PENGELOMPOKAN")
print("="*80)

apple_old = patterns['Apple Health Old']['keywords']
apple_new = patterns['Apple Health']['keywords']
overlap = apple_old & apple_new

print(f"\n1. Apple Health vs Apple Health Old")
print(f"   Overlap keywords: {len(overlap)}/{len(apple_old | apple_new)}")
print(f"   Unique to Old: {apple_old - apple_new}")
print(f"   Unique to New: {apple_new - apple_old}")

print(f"\n2. Distinctive Features:")
for cat in sorted(patterns.keys()):
    unique = patterns[cat]['keywords']
    for other_cat in patterns.keys():
        if other_cat != cat:
            unique = unique - patterns[other_cat]['keywords']
    if unique:
        print(f"   {cat}: {unique}")

print("\n" + "="*80)
print("KESIMPULAN")
print("="*80)
print(f"\nTotal kategori saat ini: 6")
print(f"Rekomendasi: ", end="")

if len(overlap) > len(apple_old - apple_new):
    print("GABUNG Apple Health + Apple Health Old = 5 CLASS")
    print("Alasan: Pola OCR sangat mirip, sulit dibedakan dengan regex")
else:
    print("TETAP 6 CLASS")
    print("Alasan: Setiap kategori memiliki pola unik yang dapat dibedakan")

print("\nKategori dengan pola paling jelas:")
for cat, p in sorted(patterns.items(), key=lambda x: len(x[1]['keywords']), reverse=True):
    print(f"  {cat}: {len(p['keywords'])} unique patterns")
