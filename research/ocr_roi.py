import pytesseract
import cv2
import re

image_path = 'WhatsApp Image 2025-11-06 at 11.15.40.jpeg'

img = cv2.imread(image_path)
h, w = img.shape[:2]

def extract_roi(img, y_start, y_end, x_start=0, x_end=None):
    """Crop ROI dan lakukan OCR dengan preprocessing optimal"""
    if x_end is None:
        x_end = img.shape[1]
    
    roi = img[y_start:y_end, x_start:x_end]
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    gray = cv2.resize(gray, None, fx=3, fy=3, interpolation=cv2.INTER_CUBIC)
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    # Denoise
    thresh = cv2.medianBlur(thresh, 3)
    
    text = pytesseract.image_to_string(thresh, config='--oem 3 --psm 7 -c tessedit_char_whitelist=0123456789:.,/\'" ')
    return text.strip()

# Definisi ROI berdasarkan layout (perkiraan proporsi)
# Format: (y_start_ratio, y_end_ratio, x_start_ratio, x_end_ratio)
rois = {
    'date': (0.08, 0.12, 0.1, 0.9),
    'duration': (0.15, 0.20, 0.05, 0.45),
    'calories': (0.15, 0.20, 0.55, 0.95),
    'pace': (0.23, 0.28, 0.05, 0.45),
    'speed': (0.23, 0.28, 0.55, 0.95),
    'cadence': (0.31, 0.36, 0.05, 0.45),
    'stride': (0.31, 0.36, 0.55, 0.95),
    'steps': (0.39, 0.44, 0.05, 0.45),
    'heart_rate': (0.39, 0.44, 0.55, 0.95),
}

data = {}

for key, (y1, y2, x1, x2) in rois.items():
    roi_text = extract_roi(img, int(h*y1), int(h*y2), int(w*x1), int(w*x2))
    
    # Parse berdasarkan field
    if key == 'date':
        match = re.search(r'(\d+.*\d{4}.*\d+\.\d+)', roi_text)
        data['date'] = match.group(1) if match else roi_text
    elif key == 'duration':
        match = re.search(r'(\d{2}):(\d{2}):(\d{2})', roi_text)
        if match:
            data['duration'] = f"{match.group(1)}:{match.group(2)}:{match.group(3)}"
    elif key == 'calories':
        match = re.search(r'(\d+)', roi_text)
        data['total_calories'] = f"{match.group(1)} kcal" if match else roi_text
    elif key == 'pace':
        match = re.search(r"(\d+)'(\d+)", roi_text)
        data['avg_pace'] = f"{match.group(1)}'{match.group(2)}\" /km" if match else roi_text
    elif key == 'speed':
        match = re.search(r'(\d+[,\.]\d+)', roi_text)
        data['avg_speed'] = f"{match.group(1)} km/h" if match else roi_text
    elif key == 'cadence':
        match = re.search(r'(\d+)', roi_text)
        data['avg_cadence'] = f"{match.group(1)} steps/min" if match else roi_text
    elif key == 'stride':
        match = re.search(r'(\d+)', roi_text)
        data['avg_stride'] = f"{match.group(1)} cm" if match else roi_text
    elif key == 'steps':
        match = re.search(r'(\d+[.,]\d+)', roi_text)
        data['steps'] = f"{match.group(1)} steps" if match else roi_text
    elif key == 'heart_rate':
        match = re.search(r'(\d+)', roi_text)
        data['avg_heart_rate'] = f"{match.group(1)} bpm" if match else roi_text

print("=" * 60)
print("DATA OBJEKTIF HASIL OCR (ROI-based)")
print("=" * 60)
for key, value in data.items():
    print(f"{key.replace('_', ' ').title():<20}: {value}")
print("=" * 60)
