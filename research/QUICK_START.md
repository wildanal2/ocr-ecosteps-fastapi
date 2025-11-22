# 🚀 Quick Start - OCR Research

## Cara Tercepat

### 1️⃣ Batch Process Semua Dataset

```bash
cd /home/miew/Documents/Project/ocr-ecosteps
python research/batch_process_datasets.py
```

**Output:** `research/ocr_validation_YYYYMMDD_HHMMSS.csv`

---

### 2️⃣ Test Single Image

```bash
python research/test_single_image.py datasets/Google\ Fit/google_fit_1122.jpeg
```

atau dengan kategori:

```bash
python research/test_single_image.py datasets/Google\ Fit/google_fit_1122.jpeg "Google Fit"
```

---

### 3️⃣ Interactive Menu

```bash
./research/run_research.sh
```

Pilih dari menu interaktif.

---

## Via API (Alternative)

### Start Server:
```bash
python main.py
```

### Run Batch:
```bash
python research/batch_process_via_api.py
```

### Test Single via API:
```bash
curl -X POST "http://localhost:8000/api/v1/ocr-ecosteps/local" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-secret-api-key-here" \
  -d '{
    "img_path": "/home/miew/Documents/Project/ocr-ecosteps/datasets/Google Fit/google_fit_1122.jpeg",
    "category": "Google Fit"
  }'
```

---

## Dataset Info

```
📁 datasets/
├── Apple Health/       7 images
├── Apple Health Old/   1 image
├── Fitbit/            2 images
├── Google Fit/        11 images
├── Huawei Health/     4 images
└── Samsung Health/    6 images

Total: 31 images
```

---

## Output CSV Columns

- `category` - Kategori app
- `file_name` - Nama file
- `app_class` - Hasil klasifikasi
- `steps` - Langkah terdeteksi
- `raw_ocr` - Text mentah OCR
- `status` - SUCCESS/ERROR

---

## Next Steps

1. ✅ Run batch processing
2. ✅ Open CSV file
3. ✅ Validate manually
4. ✅ Calculate accuracy
5. ✅ Improve patterns if needed

---

**Need help?** Read `RESEARCH_GUIDE.md`
