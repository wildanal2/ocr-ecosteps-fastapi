#!/usr/bin/env python3
import csv

# Load results
results = []
with open('ocr_evaluation_results.csv', 'r') as f:
    reader = csv.DictReader(f)
    results = list(reader)

total_files = len(results)
detected_steps = sum(1 for r in results if r['detected'] == 'True')
correct_steps = sum(1 for r in results if r['accurate'] == 'True')

step_detection_rate = (detected_steps / total_files) * 100
step_accuracy_rate = (correct_steps / total_files) * 100
conditional_accuracy = (correct_steps / detected_steps) * 100 if detected_steps > 0 else 0

print("=" * 70)
print("📊 HASIL EVALUASI AKURASI OCR ECOSTEPS")
print("=" * 70)
print(f"Total Gambar:           {total_files}")
print(f"Steps Terdeteksi:       {detected_steps}")
print(f"Steps Benar:            {correct_steps}")
print(f"")
print(f"📈 METRIK PERFORMA:")
print(f"Step Detection Rate:    {step_detection_rate:.1f}% ({detected_steps}/{total_files})")
print(f"Overall Accuracy:       {step_accuracy_rate:.1f}% ({correct_steps}/{total_files})")
print(f"Conditional Accuracy:   {conditional_accuracy:.1f}% ({correct_steps}/{detected_steps})")

# Per-category analysis
print(f"\n📱 ANALISIS PER KATEGORI:")
print("-" * 70)

categories = {}
for r in results:
    cat = r['category']
    if cat not in categories:
        categories[cat] = {'total': 0, 'detected': 0, 'correct': 0}
    categories[cat]['total'] += 1
    if r['detected'] == 'True':
        categories[cat]['detected'] += 1
    if r['accurate'] == 'True':
        categories[cat]['correct'] += 1

for category, stats in sorted(categories.items()):
    cat_total = stats['total']
    cat_detected = stats['detected']
    cat_correct = stats['correct']
    
    cat_detection_rate = (cat_detected / cat_total) * 100
    cat_accuracy_rate = (cat_correct / cat_total) * 100
    
    print(f"{category:20} | Detection: {cat_detection_rate:5.1f}% | Accuracy: {cat_accuracy_rate:5.1f}% | ({cat_detected}/{cat_total})")

# Show failed cases
print(f"\n❌ KASUS GAGAL:")
print("-" * 70)
failed = [r for r in results if r['detected'] == 'False']
if failed:
    for r in failed:
        print(f"  • {r['category']:20} | {r['filename']:50} | Expected: {r['expected_steps']}")
else:
    print("  Tidak ada kasus gagal!")

print("\n" + "=" * 70)
