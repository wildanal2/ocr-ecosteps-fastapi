# 🚀 OCR Research Cheatsheet

## ⚡ Quick Commands

### Most Used: Batch Process All
```bash
python research/batch_process_datasets.py
```

### Analyze Latest Results
```bash
python research/analyze_results.py
```

### Interactive Menu
```bash
./research/run_research.sh
```

### Test Single Image
```bash
python research/test_single_image.py datasets/Google\ Fit/google_fit_1122.jpeg
```

---

## 📊 Dataset Info

| Category | Count |
|----------|-------|
| Apple Health | 7 |
| Apple Health Old | 1 |
| Fitbit | 2 |
| Google Fit | 11 |
| Huawei Health | 4 |
| Samsung Health | 6 |
| **Total** | **31** |

---

## 🔌 API Endpoint

### Local File Processing
```bash
curl -X POST "http://localhost:8000/api/v1/ocr-ecosteps/local" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-secret-api-key-here" \
  -d '{
    "img_path": "/full/path/to/image.jpg",
    "category": "Google Fit"
  }'
```

### Dev Mode (URL)
```bash
curl -X POST "http://localhost:8000/api/v1/ocr-ecosteps/dev" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-secret-api-key-here" \
  -d '{
    "img_url": "https://example.com/image.jpg"
  }'
```

---

## 📁 File Locations

```
research/
├── batch_process_datasets.py    # Main batch script
├── batch_process_via_api.py     # API variant
├── test_single_image.py         # Single test
├── run_research.sh              # Interactive menu
├── analyze_results.py           # Results analyzer
├── ocr_validation_*.csv         # Generated results
└── *.md                         # Documentation
```

---

## 🔧 Common Tasks

### Count Images
```bash
find datasets -type f \( -iname "*.jpg" -o -iname "*.jpeg" -o -iname "*.png" \) | wc -l
```

### Find Latest CSV
```bash
ls -t research/ocr_validation_*.csv | head -1
```

### View CSV Headers
```bash
head -1 research/ocr_validation_*.csv | tr ',' '\n'
```

### Open Latest CSV
```bash
libreoffice $(ls -t research/ocr_validation_*.csv | head -1)
```

---

## 🐍 Python Quick Test

```python
from app.core.ocr_processor_local import process_ocr_local

result = process_ocr_local(
    "/home/miew/Documents/Project/ocr-ecosteps/datasets/Google Fit/google_fit_1122.jpeg",
    "Google Fit"
)

print(f"App: {result['app_class']}")
print(f"Steps: {result['extracted_data'].get('steps')}")
print(f"Time: {result['processing_time_ms']}ms")
```

---

## 📊 CSV Columns

1. no
2. category
3. file_name
4. file_path
5. app_class
6. steps
7. date
8. distance
9. duration
10. total_calories
11. avg_pace
12. avg_speed
13. avg_cadence
14. avg_stride
15. avg_heart_rate
16. processing_time_ms
17. raw_ocr
18. status
19. error_message

---

## ✅ Validation Workflow

```
1. Run:     python research/batch_process_datasets.py
2. Analyze: python research/analyze_results.py
3. Open:    CSV file in Excel/Sheets
4. Add:     validation_status, expected_steps, notes columns
5. Validate: Each row manually
6. Calculate: Accuracy = (CORRECT / Total) × 100%
```

---

## 🎯 Success Criteria

- ✅ Success Rate: >90%
- ✅ Steps Extraction: >85%
- ✅ Processing Time: <5s per image
- ✅ Classification Accuracy: >95%

---

## 🔍 Debugging

### Check OCR Output
```python
result = process_ocr_local("path/to/image.jpg")
print(result['raw_ocr'])  # See what OCR detected
```

### Test Regex Pattern
```python
import re
text = "12,345 steps"
m = re.search(r'(\d[\.,]\d{3})\s*steps', text, re.I)
if m: print(m.group(1))  # Test extraction
```

### Check Classification
```python
from app.core.ocr_processor_local import classify_app
text = "Heart Pts 12,345"
app = classify_app(text)
print(app)  # Should be "Google Fit"
```

---

## 📚 Documentation

- **Quick Start:** `research/QUICK_START.md`
- **Full Guide:** `research/RESEARCH_GUIDE.md`
- **Summary:** `research/RESEARCH_SUMMARY.md`
- **This File:** `research/CHEATSHEET.md`
- **Main Docs:** `RESEARCH_IMPLEMENTATION.md`

---

## 🆘 Help

### Error: Module not found
```bash
pip install -r requirements.txt
```

### Error: Cannot load image
```bash
# Check file exists
ls -lh path/to/image.jpg

# Check permissions
chmod 644 path/to/image.jpg
```

### Error: API unauthorized
```bash
# Set API key
export API_KEY="your-secret-api-key-here"
```

---

**Print this for quick reference! 📄**
