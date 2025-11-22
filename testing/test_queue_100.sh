#!/bin/bash

API_URL="https://ocr.moveforelephants.id/api/v1/ocr-ecosteps"
API_KEY="sk_fast_ji2348sdf9snjamau66asd8nh3"
ENVIRONMENT="staging"

echo "🧪 Testing OCR Queue - 100 Parallel Requests"
echo "=============================================="
echo "Environment: $ENVIRONMENT"
echo "Sending 100 requests..."
echo ""

# URLs to cycle through
URLS=(
  "https://nos.jkt-1.neo.id/permata-wfe/reports/wildanal2_gmail_com/2025-11-19_174415.jpg"
  "https://nos.jkt-1.neo.id/permata-wfe/reports/wildanal3_gmail_com/2025-11-19_201011.jpg"
  "https://nos.jkt-1.neo.id/permata-wfe/reports/wildanal2_gmail_com/2025-11-19_201013.jpg"
  "https://nos.jkt-1.neo.id/permata-wfe/reports/wildanal2_gmail_com/2025-11-19_201443.jpg"
  "https://nos.jkt-1.neo.id/permata-wfe/reports/wildanal3_gmail_com/2025-11-19_201445.jpg"
)

send_request() {
  local report_id=$1
  local url_index=$((report_id % 5))
  local url=${URLS[$url_index]}
  curl -s -X POST "$API_URL" -H "Content-Type: application/json" -H "x-api-key: $API_KEY" \
    -d "{\"user_id\":145,\"report_id\":$report_id,\"s3_url\":\"$url\",\"environment\":\"$ENVIRONMENT\"}" > /dev/null
  echo "✓ Sent report_id: $report_id"
}

# Send 100 requests in parallel
for i in {1..100}; do
  send_request $((1000 + i)) &
done

wait

echo ""
echo "=============================================="
echo "✅ All 100 requests sent!"
echo ""
echo "Check queue status:"
echo "  curl https://ocr.moveforelephants.id/app-status | jq '.workers'"
