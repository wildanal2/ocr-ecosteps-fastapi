import cv2
from pathlib import Path
import pandas as pd
import easyocr

DATASET_DIR = Path('../datasets')
OUTPUT_FILE = 'ocr_results.xlsx'

print("📦 Loading EasyOCR...")
reader = easyocr.Reader(['en'], gpu=True)
print("✓ EasyOCR loaded\n")

app_folders = ['Apple Health', 'Google Fit', 'Huawei Health', 'Samsung Health']
results_list = []

for app_name in app_folders:
    app_path = DATASET_DIR / app_name
    if not app_path.exists():
        continue
    
    print(f"📂 Processing: {app_name}")
    
    for img_file in app_path.glob('*'):
        if img_file.suffix.lower() not in ['.jpg', '.jpeg', '.png']:
            continue
        
        print(f"  🔍 {img_file.name}...", end=' ')
        
        try:
            img = cv2.imread(str(img_file))
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            img_rgb = cv2.resize(img_rgb, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
            
            ocr_results = reader.readtext(img_rgb)
            text = ' '.join([res[1] for res in ocr_results])
            
            results_list.append({
                'app': app_name,
                'filename': img_file.name,
                'raw_text': text
            })
            print("✓")
            
        except Exception as e:
            print(f"✗ Error: {e}")

print(f"\n💾 Saving to {OUTPUT_FILE}...")
df = pd.DataFrame(results_list)
df.to_excel(OUTPUT_FILE, index=False)
print(f"✓ Saved {len(results_list)} results")
print(f"\n📊 Summary:")
print(df.groupby('app').size())
