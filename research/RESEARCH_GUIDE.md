# OCR Research & Validation Guide

## 📋 Overview

Panduan ini untuk melakukan research dan validasi ulang OCR dengan dataset baru yang ada di folder lokal.

## 📁 Dataset Structure

```
datasets/
├── Apple Health/          # 7 images
├── Apple Health Old/      # 1 image
├── Fitbit/               # 2 images
├── Google Fit/           # 11 images
├── Huawei Health/        # 4 images
└── Samsung Health/       # 6 images

Total: 31 images across 6 categories
```

## 🚀 Quick Start

### Option 1: Direct Processing (Recommended)

Langsung process semua dataset tanpa perlu API server:

```bash
cd /home/miew/Documents/Project/ocr-ecosteps
python research/batch_process_datasets.py
```

**Keuntungan:**
- ✅ Tidak perlu jalankan API server
- ✅ Lebih cepat
- ✅ Langsung import module

### Option 2: Via API Endpoint

Process melalui API endpoint (perlu server running):

```bash
# Terminal 1: Start API server
python main.py

# Terminal 2: Run batch processing
python research/batch_process_via_api.py
```

**Keuntungan:**
- ✅ Test API endpoint sekaligus
- ✅ Simulasi production environment
- ✅ Bisa monitor via logs

## 📊 Output

Hasil akan disimpan dalam file CSV dengan format:

```
ocr_validation_YYYYMMDD_HHMMSS.csv
```

### CSV Columns:

| Column | Description |
|--------|-------------|
| no | Nomor urut |
| category | Kategori app (folder name) |
| file_name | Nama file gambar |
| file_path | Path lengkap file |
| app_class | Hasil klasifikasi app |
| steps | Jumlah langkah yang terdeteksi |
| date | Tanggal aktivitas |
| distance | Jarak tempuh |
| duration | Durasi aktivitas |
| total_calories | Total kalori |
| avg_pace | Kecepatan rata-rata |
| avg_speed | Kecepatan |
| avg_cadence | Cadence |
| avg_stride | Stride length |
| avg_heart_rate | Heart rate |
| processing_time_ms | Waktu processing (ms) |
| raw_ocr | Raw text dari OCR |
| status | SUCCESS/ERROR |
| error_message | Pesan error jika ada |

## 🔍 Manual Validation

Setelah CSV dibuat, lakukan validasi manual:

1. **Buka CSV file** dengan Excel/LibreOffice/Google Sheets
2. **Tambahkan kolom baru:**
   - `validation_status` (CORRECT/WRONG/PARTIAL)
   - `expected_steps` (nilai steps yang benar)
   - `notes` (catatan tambahan)

3. **Validasi setiap baris:**
   - Buka gambar asli dari `file_path`
   - Bandingkan dengan hasil OCR
   - Tandai status validasi
   - Catat nilai yang benar jika salah

4. **Hitung akurasi:**
   ```
   Accuracy = (CORRECT / Total) × 100%
   ```

## 🧪 Testing Single Image

### Via API:

```bash
curl -X POST "http://localhost:8000/api/v1/ocr-ecosteps/local" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-secret-api-key-here" \
  -d '{
    "img_path": "/home/miew/Documents/Project/ocr-ecosteps/datasets/Google Fit/google_fit_1122.jpeg",
    "category": "Google Fit"
  }'
```

### Via Python:

```python
from app.core.ocr_processor_local import process_ocr_local

result = process_ocr_local(
    "/home/miew/Documents/Project/ocr-ecosteps/datasets/Google Fit/google_fit_1122.jpeg",
    "Google Fit"
)
print(result)
```

## 📈 Analysis & Improvement

Setelah validasi, analisis hasil:

1. **Per Category Accuracy:**
   - Hitung akurasi per kategori app
   - Identifikasi kategori dengan akurasi rendah

2. **Common Errors:**
   - Pattern error yang sering muncul
   - Jenis data yang sering salah ekstraksi

3. **Improvement Areas:**
   - Update regex patterns di `ocr_processor_local.py`
   - Tambah preprocessing untuk kategori tertentu
   - Fine-tune classification rules

## 🔧 Customization

### Menambah Kategori Baru:

Edit `app/core/ocr_processor_local.py`:

```python
def classify_app(text: str, category: str = None) -> str:
    # ... existing code ...
    elif 'new_app_keyword' in text_lower:
        return 'New App Name'
```

### Menambah Pattern Ekstraksi:

```python
def extract_steps(text: str, app: str) -> int:
    # ... existing code ...
    elif app == 'New App Name':
        m = re.search(r'your_pattern_here', text, re.I)
        if m: return int(m.group(1))
```

## 📝 Notes

- **Processing Time:** ~2-5 detik per gambar (tergantung GPU/CPU)
- **Total Time:** ~1-3 menit untuk 31 gambar
- **Memory:** ~2-4 GB RAM (EasyOCR model)
- **GPU:** Otomatis terdeteksi jika tersedia

## 🐛 Troubleshooting

### Error: "Cannot load image"
- Pastikan path file benar
- Check file permissions
- Pastikan format gambar supported

### Error: "Module not found"
- Install dependencies: `pip install -r requirements.txt`
- Check virtual environment aktif

### API Error: "Unauthorized"
- Set API_KEY di environment atau script
- Check header X-API-Key

### Slow Processing
- Enable GPU jika tersedia
- Reduce image resolution di preprocessing
- Process in smaller batches

## 📚 References

- [EasyOCR Documentation](https://github.com/JaidedAI/EasyOCR)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- Project README: `/home/miew/Documents/Project/ocr-ecosteps/README.md`

## ✅ Checklist

- [ ] Dataset lengkap di folder `datasets/`
- [ ] Dependencies terinstall
- [ ] Run batch processing script
- [ ] CSV hasil generated
- [ ] Manual validation completed
- [ ] Accuracy calculated
- [ ] Improvement identified
- [ ] Code updated (if needed)
- [ ] Re-test dengan dataset baru

---

**Happy Research! 🔬**
