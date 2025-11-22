# 📁 Datasets Folder

## 📋 Overview

Folder ini berisi dataset gambar untuk testing dan validasi OCR system.

**Total Images:** 31
**Categories:** 6
**Last Updated:** 2025-11-22

---

## 📂 Structure

```
datasets/
├── Apple Health/          7 images
├── Apple Health Old/      1 image
├── Fitbit/               2 images
├── Google Fit/          11 images
├── Huawei Health/        4 images
├── Samsung Health/       6 images
├── DATASET_GROUND_TRUTH.md  ← Ground truth reference
├── ground_truth.csv         ← CSV format
└── README.md                ← This file
```

---

## 🎯 Ground Truth

**File:** `DATASET_GROUND_TRUTH.md`

Berisi expected values (ground truth) untuk semua gambar.
Gunakan sebagai acuan untuk:
- ✅ Validasi hasil OCR
- ✅ Testing setelah perubahan code
- ✅ Benchmark accuracy
- ✅ Debugging

---

## 🚀 Quick Usage

### Validate OCR Results
```bash
cd research
python validate_against_ground_truth.py
```

### Test Single Image
```bash
python research/test_single_image.py datasets/Fitbit/2025-11-22_072807_fitbit.jpg "Fitbit"
```

### Batch Process All
```bash
python research/batch_process_datasets.py
```

---

## ➕ Adding New Images

1. **Add image to appropriate category folder**
2. **Test OCR:**
   ```bash
   python research/test_single_image.py datasets/Category/new_image.jpg "Category"
   ```
3. **Verify result manually**
4. **Update ground truth:**
   - Edit `DATASET_GROUND_TRUTH.md`
   - Add entry with expected value
   - Update `research/validate_against_ground_truth.py`
5. **Run validation:**
   ```bash
   python research/validate_against_ground_truth.py
   ```

---

## 📊 Current Statistics

| Category | Images | Accuracy |
|----------|--------|----------|
| Apple Health | 7 | 100% ✅ |
| Apple Health Old | 1 | 100% ✅ |
| Fitbit | 2 | 100% ✅ |
| Google Fit | 11 | 100% ✅ |
| Huawei Health | 4 | 100% ✅ |
| Samsung Health | 6 | 100% ✅ |
| **TOTAL** | **31** | **100%** ✅ |

---

## 📝 Files

- **DATASET_GROUND_TRUTH.md** - Detailed ground truth documentation
- **ground_truth.csv** - CSV format for automation
- **README.md** - This file

---

## 🔍 Validation

```bash
# Validate current OCR results
cd research
python validate_against_ground_truth.py

# Expected output:
# ✓ 31/31 matches (100.0%)
# ✗ 0 mismatches
# ✅ ALL VALIDATIONS PASSED!
```

---

**Last Validation:** 2025-11-22
**Status:** ✅ All 31 images validated
