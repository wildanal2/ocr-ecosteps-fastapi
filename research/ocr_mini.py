import pytesseract
from PIL import Image
import cv2

# Path gambar
image_path = 'WhatsApp Image 2025-11-06 at 11.15.40.jpeg'

# Baca dan preprocess gambar
img = cv2.imread(image_path)
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
gray = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
_, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

# OCR dengan config minimal
config = r'--oem 3 --psm 6'
text = pytesseract.image_to_string(thresh, config=config)

print("Hasil OCR:")
print("-" * 50)
print(text)
