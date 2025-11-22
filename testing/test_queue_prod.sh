#!/bin/bash

API_URL="http://localhost:8000/api/v1/ocr-ecosteps"
API_KEY="sk_fast_ji2348sdf9snjamau66asd8nh3"

echo "🧪 Testing OCR Queue - PRODUCTION Environment"
echo "================================================"
echo "⚠️  WARNING: This will send to PRODUCTION!"
echo "Sending 5 requests to PRODUCTION..."
echo ""

send_request() {
  local report_id=$1
  local url=$2
  curl -s -X POST "$API_URL" -H "Content-Type: application/json" -H "x-api-key: $API_KEY" \
    -d "{\"user_id\":145,\"report_id\":$report_id,\"s3_url\":\"$url\",\"environment\":\"production\"}" > /dev/null
  echo "✓ Sent report_id: $report_id [PRODUCTION]"
}

send_request 301 "https://nos.jkt-1.neo.id/permata-wfe/reports/wildanal2_gmail_com/2025-11-19_174415.jpg" &
send_request 302 "https://nos.jkt-1.neo.id/permata-wfe/reports/wildanal3_gmail_com/2025-11-19_201011.jpg" &
send_request 303 "https://nos.jkt-1.neo.id/permata-wfe/reports/wildanal2_gmail_com/2025-11-19_201013.jpg" &
send_request 304 "https://nos.jkt-1.neo.id/permata-wfe/reports/wildanal2_gmail_com/2025-11-19_201443.jpg" &
send_request 305 "https://nos.jkt-1.neo.id/permata-wfe/reports/wildanal3_gmail_com/2025-11-19_201445.jpg" &

wait

echo ""
echo "✅ All PRODUCTION requests sent!"
echo "Check logs for: 'Sending to PROD webhook'"
