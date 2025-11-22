# 📝 How to Add New Data - Quick Guide

## 🚀 Simple Workflow

### Step 1: Add Image to Dataset

```bash
# Copy image ke folder kategori yang sesuai
cp new_image.jpg datasets/Fitbit/
```

### Step 2: Run OCR Check

```bash
python research/add_new_image.py datasets/Fitbit/new_image.jpg
```

**Output akan menampilkan:**

- ✅ Detected steps
- ✅ App classification
- ✅ Raw OCR text
- ✅ Copy-paste snippets untuk update

### Step 3: Verify & Update

**Jika hasil benar:**

1. **Update DATASET_GROUND_TRUTH.md:**

   ```markdown
   | new_image.jpg | 12345 | Standard format |
   ```
2. **Update validate_against_ground_truth.py:**

   ```python
   "new_image.jpg": 12345,  # Fitbit
   ```
3. **Validate:**

   ```bash
   python research/validate_against_ground_truth.py
   ```

---

## 💬 Atau Chat dengan AI



Bilang versi lengkap

```
Saya sudah tambah gambar baru:
File: [nama_file.jpg]
Kategori: [Apple Health/Google Fit/Samsung Health/Huawei Health/Fitbit]
Lokasi: datasets/[Kategori]/[nama_file.jpg]

Tolong check OCR nya dan update ground truth jika benar.
```


Cukup bilang:

```
Check OCR untuk: datasets/Fitbit/new_image.jpg
```

Atau:

```
Saya tambah gambar baru di datasets/Google Fit/test_2025.jpg
Tolong check dan update ground truth
```

AI akan:

1. ✅ Test OCR
2. ✅ Tampilkan hasil
3. ✅ Tanya konfirmasi
4. ✅ Update ground truth jika benar
5. ✅ Run validation

---

## 📋 Template Pesan untuk AI

### Format 1 (Simple):

```
Check OCR: datasets/[Category]/[filename]
```

### Format 2 (Detailed):

```
Tambah data baru:
- File: [filename]
- Kategori: [Category]
- Lokasi: datasets/[Category]/[filename]

Check OCR dan update ground truth jika benar.
```

### Format 3 (Batch):

```
Check OCR untuk gambar-gambar ini:
1. datasets/Fitbit/image1.jpg
2. datasets/Fitbit/image2.jpg
3. datasets/Google Fit/image3.jpg

Update ground truth untuk yang benar.
```

---

## 🔧 Manual Update (Jika Perlu)

### 1. Edit DATASET_GROUND_TRUTH.md

Tambahkan di section kategori yang sesuai:

```markdown
### Fitbit (3 images)  ← Update count

| File Name | Expected Steps | Notes |
|-----------|----------------|-------|
| existing_image.jpg | 11820 | Today format |
| new_image.jpg | 12345 | Standard format |  ← Add this
```

### 2. Edit validate_against_ground_truth.py

Tambahkan di dictionary GROUND_TRUTH:

```python
GROUND_TRUTH = {
    # ... existing entries ...
    "new_image.jpg": 12345,  # Fitbit  ← Add this
}
```

### 3. Validate

```bash
cd research
python validate_against_ground_truth.py
```

Expected output:

```
✓ Matches: 32 (100.0%)  ← Updated count
✗ Mismatches: 0
✅ ALL VALIDATIONS PASSED!
```

---

## ⚡ Quick Commands

```bash
# Test single image
python research/add_new_image.py datasets/Fitbit/new.jpg

# Validate all
python research/validate_against_ground_truth.py

# Batch process all (if many new images)
python research/batch_process_datasets.py
```

---

## 🎯 Example Workflow

```bash
# 1. Add image
cp ~/Downloads/fitbit_screenshot.jpg datasets/Fitbit/

# 2. Check OCR
python research/add_new_image.py datasets/Fitbit/fitbit_screenshot.jpg

# Output:
# Steps: 15234
# App Class: Fitbit

# 3. Update ground truth (copy-paste dari output)
# Edit datasets/DATASET_GROUND_TRUTH.md
# Edit research/validate_against_ground_truth.py

# 4. Validate
python research/validate_against_ground_truth.py

# Output:
# ✅ ALL VALIDATIONS PASSED!
```

---

## 📊 What AI Will Do

When you say: **"Check OCR: datasets/Fitbit/new.jpg"**

AI will automatically:

1. ✅ **Run OCR** on the image
2. ✅ **Show results:**
   - Detected steps
   - App classification
   - Raw OCR text
3. ✅ **Ask confirmation:** "Is this correct?"
4. ✅ **If confirmed, update:**
   - `datasets/DATASET_GROUND_TRUTH.md`
   - `research/validate_against_ground_truth.py`
5. ✅ **Run validation** to verify
6. ✅ **Show summary:** "Ground truth updated! 32/32 validated ✅"

---

## 🎓 Tips

- ✅ Always verify OCR results manually
- ✅ Add notes for special patterns
- ✅ Run validation after updates
- ✅ Keep ground truth in sync with actual data
- ✅ Use descriptive file names

---

## 🆘 Troubleshooting

### OCR Result Wrong?

```bash
# Check raw OCR text
python research/test_single_image.py datasets/Fitbit/image.jpg

# Review raw_ocr output
# Update patterns in app/core/ocr_processor_local.py if needed
```

### Validation Failed?

```bash
# Check which images failed
python research/validate_against_ground_truth.py

# Review mismatches
# Update ground truth or fix OCR patterns
```

---

**🎉 That's it! Simple workflow untuk add new data!**
