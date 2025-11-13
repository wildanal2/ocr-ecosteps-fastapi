import re
import zipfile
import xml.etree.ElementTree as ET
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import numpy as np

# Pattern extractors per app
PATTERNS = {
    'Apple Health': [
        r'(\d+[\.,]?\d*)\s*langkah',
        r'Step Count.*?(\d+[\.,]?\d*)',
        r'(\d{3,5})\s*steps?',
    ],
    'Google Fit': [
        r'(\d[\.,]\d{3})\s*Poin Kardio Langkah',
        r'Langkah\s*(\d+[\.,]?\d*)',
        r'(\d{4,5})\s*Poin',
    ],
    'Huawei Health': [
        r'(\d+)\s*/\s*\d+[\.,]?\d*\s*steps',
        r'steps\s*(\d+)',
    ],
    'Samsung Health': [
        r'(\d+[\.,]?\d*)\s*(?:langkah|steps)',
        r'(\d[\.,]\d{3})\s*steps',
    ]
}

def normalize_number(num_str):
    """Convert string number to int"""
    return int(num_str.replace('.', '').replace(',', ''))

def extract_features(text):
    """Extract features from OCR text"""
    features = {
        'has_langkah': 1 if 'langkah' in text.lower() else 0,
        'has_steps': 1 if 'steps' in text.lower() else 0,
        'has_poin_kardio': 1 if 'poin kardio' in text.lower() else 0,
        'has_step_count': 1 if 'step count' in text.lower() else 0,
        'num_count': len(re.findall(r'\d{3,5}', text)),
        'text_length': len(text),
    }
    return list(features.values())

def extract_step_by_pattern(text, app):
    """Extract step number using app-specific patterns"""
    patterns = PATTERNS.get(app, [])
    
    for pattern in patterns:
        matches = re.findall(pattern, text, re.I)
        if matches:
            try:
                return normalize_number(matches[0])
            except:
                continue
    
    # Fallback: find 3-5 digit numbers
    numbers = re.findall(r'\b(\d{3,5})\b', text)
    if numbers:
        return int(numbers[0])
    
    return None

# Load data from Excel
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

apps = [d[0] for d in data]
texts = [d[2] for d in data]
true_steps = [int(float(d[3])) for d in data]

print(f"✓ Loaded {len(data)} samples\n")

# Train app classifier
print("🤖 Training app classifier...")
X_text = texts
y_app = apps

vectorizer = TfidfVectorizer(max_features=50)
X_tfidf = vectorizer.fit_transform(X_text)

X_features = np.array([extract_features(t) for t in texts])
X_combined = np.hstack([X_tfidf.toarray(), X_features])

X_train, X_test, y_train, y_test = train_test_split(X_combined, y_app, test_size=0.3, random_state=42)

clf = RandomForestClassifier(n_estimators=50, random_state=42)
clf.fit(X_train, y_train)

y_pred = clf.predict(X_test)
app_accuracy = accuracy_score(y_test, y_pred)

print(f"✓ App classifier accuracy: {app_accuracy*100:.1f}%\n")

# Extract steps using hybrid approach
print("🔍 Extracting steps with hybrid approach...")
predicted_steps = []

for i, text in enumerate(texts):
    # Predict app
    X_single = np.hstack([vectorizer.transform([text]).toarray(), [extract_features(text)]])
    predicted_app = clf.predict(X_single)[0]
    
    # Extract step using pattern
    step = extract_step_by_pattern(text, predicted_app)
    predicted_steps.append(step if step else 0)

# Calculate accuracy
correct = sum(1 for pred, true in zip(predicted_steps, true_steps) if pred == true)
accuracy = correct / len(true_steps) * 100

print("="*80)
print("📊 VALIDATION RESULTS")
print("="*80)
print(f"Total samples: {len(true_steps)}")
print(f"Correct predictions: {correct}/{len(true_steps)}")
print(f"Accuracy: {accuracy:.1f}%\n")

# Detailed results
print("="*80)
print("DETAILED PREDICTIONS")
print("="*80)
for i, (app, text, true, pred) in enumerate(zip(apps, texts, true_steps, predicted_steps), 1):
    status = "✓" if true == pred else "✗"
    print(f"{status} [{i}] {app}")
    print(f"   True: {true} | Predicted: {pred}")
    if true != pred:
        print(f"   Text: {text[:100]}...")
    print()

# Error analysis
errors = [(i, apps[i], true_steps[i], predicted_steps[i]) for i in range(len(true_steps)) if true_steps[i] != predicted_steps[i]]
if errors:
    print("="*80)
    print(f"❌ ERRORS ({len(errors)} samples)")
    print("="*80)
    for idx, app, true, pred in errors:
        print(f"[{idx+1}] {app}: True={true}, Pred={pred}")
        print(f"Text: {texts[idx][:150]}...")
        print()
