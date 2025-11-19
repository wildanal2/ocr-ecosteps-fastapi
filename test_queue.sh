#!/bin/bash

API_URL="http://localhost:8000/api/v1/ocr-ecosteps"
API_KEY="sk_fast_ji2348sdf9snjamau66asd8nh3"

echo "🧪 Testing OCR Queue with 5 requests..."
echo "========================================="

# Request 1
echo "📤 Request 1: user_id=145, report_id=15"
curl -X POST "$API_URL" \
  -H "Content-Type: application/json" \
  -H "x-api-key: $API_KEY" \
  -d '{
    "user_id": 145,
    "report_id": 15,
    "s3_url": "https://nos.jkt-1.neo.id/permata-wfe/reports/wildanal2_gmail_com/2025-11-19_174415.jpg"
  }'
echo -e "\n"

# Request 2
echo "📤 Request 2: user_id=145, report_id=16"
curl -X POST "$API_URL" \
  -H "Content-Type: application/json" \
  -H "x-api-key: $API_KEY" \
  -d '{
    "user_id": 145,
    "report_id": 16,
    "s3_url": "https://nos.jkt-1.neo.id/permata-wfe/reports/wildanal3_gmail_com/2025-11-19_201011.jpg"
  }'
echo -e "\n"

# Request 3 (duplicate report_id=15)
echo "📤 Request 3: user_id=145, report_id=15 (duplicate)"
curl -X POST "$API_URL" \
  -H "Content-Type: application/json" \
  -H "x-api-key: $API_KEY" \
  -d '{
    "user_id": 145,
    "report_id": 15,
    "s3_url": "https://nos.jkt-1.neo.id/permata-wfe/reports/wildanal2_gmail_com/2025-11-19_201013.jpg"
  }'
echo -e "\n"

# Request 4 (duplicate report_id=15)
echo "📤 Request 4: user_id=145, report_id=15 (duplicate)"
curl -X POST "$API_URL" \
  -H "Content-Type: application/json" \
  -H "x-api-key: $API_KEY" \
  -d '{
    "user_id": 145,
    "report_id": 15,
    "s3_url": "https://nos.jkt-1.neo.id/permata-wfe/reports/wildanal2_gmail_com/2025-11-19_201443.jpg"
  }'
echo -e "\n"

# Request 5 (duplicate report_id=16)
echo "📤 Request 5: user_id=145, report_id=16 (duplicate)"
curl -X POST "$API_URL" \
  -H "Content-Type: application/json" \
  -H "x-api-key: $API_KEY" \
  -d '{
    "user_id": 145,
    "report_id": 16,
    "s3_url": "https://nos.jkt-1.neo.id/permata-wfe/reports/wildanal3_gmail_com/2025-11-19_201445.jpg"
  }'
echo -e "\n"

echo "========================================="
echo "✅ All requests sent!"
echo "Check /app-status endpoint to see queue status"
