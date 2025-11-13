import re
import zipfile
import xml.etree.ElementTree as ET

# Akurasi Model:
# App Classification: 75.0% (12/16 benar)

# Step Extraction: 56.2% (9/16 benar)

def normalize_number(num_str):
    """Convert string number to int"""
    return int(num_str.replace('.', '').replace(',', ''))

def classify_app(text):
    """Rule-based app classification"""
    text_lower = text.lower()
    
    if 'heart pts' in text_lower or 'move min' in text_lower or 'poin kardio' in text_lower:
        return 'Google Fit'
    elif 'huawei' in text_lower or 'health+' in text_lower:
        return 'Huawei Health'
    elif 'samsung health' in text_lower or 'together' in text_lower or 'kebugaran' in text_lower or 'aktivitas harian' in text_lower or 'ingkh' in text_lower:
        return 'Samsung Health'
    else:
        return 'Apple Health'

def extract_step_by_pattern(text, app):
    """Extract step number using app-specific patterns"""
    
    if app == 'Apple Health':
        # Pattern 1: "646 langkah" or "640 langkah"
        m = re.search(r'(\d+)\s*langkah', text, re.I)
        if m: return int(m.group(1))
        
        # Pattern 2: "Today Today 1.211" with dot separator
        m = re.search(r'Today\s+Today\s+(\d\.\d{3})', text, re.I)
        if m: return normalize_number(m.group(1))
        
        # Pattern 3: "Today 736" or "Today Today 736"
        m = re.search(r'Today\s+(?:Today\s+)?(\d{3,5})', text, re.I)
        if m: return int(m.group(1))
        
        # Pattern 4: "Hari Ini 640" (Indonesian)
        m = re.search(r'Hari Ini\s+(\d{3,5})', text, re.I)
        if m: return int(m.group(1))
        
        # Pattern 5: "401steps"
        m = re.search(r'(\d{3,5})steps', text, re.I)
        if m: return int(m.group(1))
        
    elif app == 'Google Fit':
        # Pattern 1: "7,555 Heart Pts" or "16,669 Heart Pts"
        m = re.search(r'(\d{1,2}[\.,]\d{3})\s*Heart Pts', text, re.I)
        if m: return normalize_number(m.group(1))
        
        # Pattern 2: "5.073 Poin Kardio" or "5.548 Poin Kardio"
        m = re.search(r'(\d[\.,]\d{3})\s*Poin Kardio', text, re.I)
        if m: return normalize_number(m.group(1))
        
    elif app == 'Huawei Health':
        # Pattern: "395 /10.000 steps"
        m = re.search(r'(\d+)\s*/\s*\d+[\.,]?\d*\s*steps', text, re.I)
        if m: return int(m.group(1))
        
    elif app == 'Samsung Health':
        # Pattern 1: "7.492 Ingkh"
        m = re.search(r'(\d[\.,]\d{3})\s*Ingkh', text, re.I)
        if m: return normalize_number(m.group(1))
        
        # Pattern 2: "1.083 18%" (percentage context) - find number before %
        m = re.search(r'(\d[\.,]\d{3})\s*\d{1,3}%', text, re.I)
        if m: return normalize_number(m.group(1))
        
        # Pattern 3: "3,139 steps" or "1.035 langkah"
        m = re.search(r'(\d[\.,]\d{3})\s*(?:steps|langkah)', text, re.I)
        if m: return normalize_number(m.group(1))
        
        # Pattern 4: "aktivitas 7.492"
        m = re.search(r'aktivitas\s+(\d[\.,]\d{3})', text, re.I)
        if m: return normalize_number(m.group(1))
    
    return None

# Load data
print("📂 Loading data...")
xlsx_file = 'ocr_results.xlsx'

with zipfile.ZipFile(xlsx_file, 'r') as z:
    with z.open('xl/sharedStrings.xml') as f:
        tree = ET.parse(f)
        root = tree.getroot()
        strings = [elem.text if elem.text else '' for elem in root.findall('.//{http://schemas.openxmlformats.org/spreadsheetml/2006/main}t')]
    
    with z.open('xl/worksheets/sheet1.xml') as f:
        tree = ET.parse(f)
        root = tree.getroot()
        rows = root.findall('.//{http://schemas.openxmlformats.org/spreadsheetml/2006/main}row')
        
        data = []
        for row in rows[1:]:
            cells = row.findall('.//{http://schemas.openxmlformats.org/spreadsheetml/2006/main}c')
            row_data = []
            for cell in cells:
                v = cell.find('.//{http://schemas.openxmlformats.org/spreadsheetml/2006/main}v')
                if v is not None:
                    t = cell.get('t')
                    if t == 's':
                        row_data.append(strings[int(v.text)])
                    else:
                        row_data.append(v.text)
            if len(row_data) >= 4:
                data.append(row_data)

true_apps = [d[0] for d in data]
texts = [d[2] for d in data]
true_steps = [int(float(d[3])) for d in data]

print(f"✓ Loaded {len(data)} samples\n")

# Classify and extract
print("🔍 Extracting steps with hybrid approach...")
predicted_apps = []
predicted_steps = []

for text in texts:
    pred_app = classify_app(text)
    predicted_apps.append(pred_app)
    
    step = extract_step_by_pattern(text, pred_app)
    predicted_steps.append(step if step else 0)

# Calculate accuracies
app_correct = sum(1 for pred, true in zip(predicted_apps, true_apps) if pred == true)
app_accuracy = app_correct / len(true_apps) * 100

step_correct = sum(1 for pred, true in zip(predicted_steps, true_steps) if pred == true)
step_accuracy = step_correct / len(true_steps) * 100

print("="*80)
print("📊 VALIDATION RESULTS")
print("="*80)
print(f"App Classification Accuracy: {app_accuracy:.1f}% ({app_correct}/{len(true_apps)})")
print(f"Step Extraction Accuracy: {step_accuracy:.1f}% ({step_correct}/{len(true_steps)})")
print()

# Detailed results
print("="*80)
print("DETAILED PREDICTIONS")
print("="*80)
for i, (true_app, pred_app, text, true_step, pred_step) in enumerate(zip(true_apps, predicted_apps, texts, true_steps, predicted_steps), 1):
    app_status = "✓" if true_app == pred_app else "✗"
    step_status = "✓" if true_step == pred_step else "✗"
    
    print(f"[{i}] {app_status} App: {true_app} → {pred_app}")
    print(f"    {step_status} Step: {true_step} → {pred_step}")
    
    if true_step != pred_step:
        print(f"    Text: {text[:120]}...")
    print()

# Error analysis
errors = [(i, true_apps[i], true_steps[i], predicted_steps[i]) for i in range(len(true_steps)) if true_steps[i] != predicted_steps[i]]
if errors:
    print("="*80)
    print(f"❌ ERRORS ({len(errors)} samples)")
    print("="*80)
    for idx, app, true, pred in errors:
        print(f"[{idx+1}] {app}: True={true}, Pred={pred}")
        print(f"Text: {texts[idx][:200]}...")
        print()
else:
    print("="*80)
    print("🎉 PERFECT! All predictions are correct!")
    print("="*80)
