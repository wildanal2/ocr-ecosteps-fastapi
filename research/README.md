# 🔬 Research Folder

Folder ini berisi tools dan scripts untuk research, validasi, dan improvement OCR engine.

## 📁 Files

### 🚀 Executable Scripts

| File | Description | Usage |
|------|-------------|-------|
| `batch_process_datasets.py` | Batch process semua dataset | `python batch_process_datasets.py` |
| `batch_process_via_api.py` | Batch process via API endpoint | `python batch_process_via_api.py` |
| `test_single_image.py` | Test single image | `python test_single_image.py <path>` |
| `run_research.sh` | Interactive menu | `./run_research.sh` |

### 📚 Documentation

| File | Description |
|------|-------------|
| `QUICK_START.md` | Quick reference - start here! |
| `RESEARCH_GUIDE.md` | Comprehensive guide |
| `RESEARCH_SUMMARY.md` | Implementation summary |
| `README.md` | This file |

### 📊 Templates & Results

| File | Description |
|------|-------------|
| `validation_template.csv` | CSV template with validation columns |
| `ocr_validation_*.csv` | Generated results (timestamped) |

### 🧪 Legacy Research Files

| File | Description |
|------|-------------|
| `ocr_best.py` | Original EasyOCR implementation |
| `ocr_*.py` | Various OCR experiments |
| `step_extractor_*.py` | Step extraction experiments |
| `ocr_results.xlsx` | Previous results |

## 🎯 Quick Commands

### Most Common: Batch Process All
```bash
python batch_process_datasets.py
```

### Test One Image
```bash
python test_single_image.py ../datasets/Google\ Fit/google_fit_1122.jpeg
```

### Interactive Menu
```bash
./run_research.sh
```

## 📊 Workflow

```
1. Run batch_process_datasets.py
   ↓
2. Get CSV file (ocr_validation_*.csv)
   ↓
3. Open in Excel/Sheets
   ↓
4. Add validation columns
   ↓
5. Manual validation
   ↓
6. Calculate accuracy
   ↓
7. Identify improvements
   ↓
8. Update code
   ↓
9. Re-test
```

## 🎓 What's New

Compared to legacy research files, new implementation adds:

- ✅ **Batch processing** automation
- ✅ **CSV export** for validation
- ✅ **API endpoint** for local files
- ✅ **Fitbit support**
- ✅ **Better error handling**
- ✅ **Progress tracking**
- ✅ **Interactive tools**

## 📈 Expected Output

After running batch processing:

```
research/
└── ocr_validation_20250106_120530.csv  (example)
```

CSV contains:
- 31 rows (one per image)
- 19 columns (data + metadata)
- Ready for manual validation

## 🔧 Customization

To add new app support or improve extraction:

1. Edit `../app/core/ocr_processor_local.py`
2. Update `classify_app()` function
3. Update `extract_steps()` function
4. Re-run batch processing
5. Compare results

## 📝 Notes

- Processing time: ~2-5s per image
- Total time: ~1-3 minutes for 31 images
- Requires EasyOCR model (~2-4 GB RAM)
- GPU auto-detected if available

## 🆘 Need Help?

1. **Quick start:** Read `QUICK_START.md`
2. **Detailed guide:** Read `RESEARCH_GUIDE.md`
3. **Implementation details:** Read `RESEARCH_SUMMARY.md`
4. **Main project:** Read `../README.md`

## 🎯 Next Steps

1. ✅ Read QUICK_START.md
2. ✅ Run batch_process_datasets.py
3. ✅ Validate results
4. ✅ Calculate accuracy
5. ✅ Improve if needed

---

**Happy Research! 🚀**
