#!/bin/bash

API_URL="http://localhost:8000/api/v1/ocr-ecosteps"
API_KEY="sk_fast_ji2348sdf9snjamau66asd8nh3"

echo "🧪 Testing OCR Queue - STAGING Environment"
echo "================================================"
echo "Sending 5 requests to STAGING..."
echo ""

send_request() {
  local report_id=$1
  local url=$2
  curl -s -X POST "$API_URL" -H "Content-Type: application/json" -H "x-api-key: $API_KEY" \
    -d "{\"user_id\":145,\"report_id\":$report_id,\"s3_url\":\"$url\",\"environment\":\"staging\"}" > /dev/null
  echo "✓ Sent report_id: $report_id [STAGING]"
}

send_request 201 "https://nos.jkt-1.neo.id/permata-wfe/reports/wildanal2_gmail_com/2025-11-19_174415.jpg" &
send_request 202 "https://nos.jkt-1.neo.id/permata-wfe/reports/wildanal3_gmail_com/2025-11-19_201011.jpg" &
send_request 203 "https://nos.jkt-1.neo.id/permata-wfe/reports/wildanal2_gmail_com/2025-11-19_201013.jpg" &
send_request 204 "https://nos.jkt-1.neo.id/permata-wfe/reports/wildanal2_gmail_com/2025-11-19_201443.jpg" &
send_request 205 "https://nos.jkt-1.neo.id/permata-wfe/reports/wildanal3_gmail_com/2025-11-19_201445.jpg" &

wait

echo ""
echo "✅ All STAGING requests sent!"
echo "Check logs for: 'Sending to STAGING webhook'"
