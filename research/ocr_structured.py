import pytesseract
import cv2
import re
from datetime import datetime

# Path gambar
image_path = 'WhatsApp Image 2025-11-06 at 11.15.40.jpeg'

# Preprocessing
img = cv2.imread(image_path)
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
gray = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
_, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

# OCR
text = pytesseract.image_to_string(thresh, config=r'--oem 3 --psm 6')

# Ekstraksi data objektif
data = {}

# Tanggal (format: DD Month YYYY at HH.MM)
date_match = re.search(r'(\d{1,2}\s+\w+\s+\d{4})\s+at\s+(\d{1,2}\.\d{2})', text)
if date_match:
    data['date'] = f"{date_match.group(1)} at {date_match.group(2)}"

# Duration (format: HH:MM:SS) - fix OCR error 119 -> 19
duration_match = re.search(r'(\d{2}):(\d{2,3}):(\d{2})', text)
if duration_match:
    mins = duration_match.group(2)
    if len(mins) == 3 and mins.startswith('1'):
        mins = mins[1:]  # Remove leading 1 from OCR error
    data['duration'] = f"{duration_match.group(1)}:{mins}:{duration_match.group(3)}"

# Total calories
cal_match = re.search(r'(\d+)\s*(?:ca|kcal)', text, re.IGNORECASE)
if cal_match:
    data['total_calories'] = f"{cal_match.group(1)} kcal"

# Avg pace (format: M'SS" /km)
pace_match = re.search(r"(\d+)'(\d+)\"\s*/km", text)
if pace_match:
    data['avg_pace'] = f"{pace_match.group(1)}'{pace_match.group(2)}\" /km"

# Avg speed (format: X,XX km/h)
speed_match = re.search(r'(\d+[,\.]\d+)\s*km[/\\]?[mh]', text)
if speed_match:
    data['avg_speed'] = f"{speed_match.group(1)} km/h"

# Avg cadence (format: XXX steps/min) - fix missing leading 1
cadence_match = re.search(r'(\d+)\s*steps?/min', text)
if cadence_match:
    cad = cadence_match.group(1)
    # If cadence < 100, likely missing leading 1
    if int(cad) < 100:
        cad = '1' + cad
    data['avg_cadence'] = f"{cad} steps/min"

# Avg stride (format: XX cm)
stride_match = re.search(r'(\d+)\s*cm', text)
if stride_match:
    data['avg_stride'] = f"{stride_match.group(1)} cm"

# Steps (format: X.XXX steps)
steps_match = re.search(r'(\d+[.,]\d+)\s*(?:steps?|seps)', text, re.IGNORECASE)
if steps_match:
    data['steps'] = f"{steps_match.group(1)} steps"

# Avg heart rate (format: XXX bpm)
hr_match = re.search(r'(\d+)\s*bpm', text)
if hr_match:
    data['avg_heart_rate'] = f"{hr_match.group(1)} bpm"

# Output terstruktur
print("=" * 60)
print("DATA OBJEKTIF HASIL OCR")
print("=" * 60)
for key, value in data.items():
    print(f"{key.replace('_', ' ').title():<20}: {value}")
print("=" * 60)
