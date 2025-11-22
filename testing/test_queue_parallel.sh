#!/bin/bash

API_URL="https://ocr.moveforelephants.id/api/v1/ocr-ecosteps"
API_KEY="sk_fast_ji2348sdf9snjamau66asd8nh3"
ENVIRONMENT="staging"  # Change to "production" for production testing

echo "🧪 Testing OCR Queue - Parallel Processing Test"
echo "================================================"
echo "Environment: $ENVIRONMENT"
echo "Sending 10 UNIQUE requests with random delays (0-1.5s)..."
echo ""

# Function to send request with random delay
send_request() {
  local report_id=$1
  local url=$2
  local delay=$(awk -v min=0 -v max=1.5 'BEGIN{srand(); print min+rand()*(max-min)}')
  sleep $delay
  curl -s -X POST "$API_URL" -H "Content-Type: application/json" -H "x-api-key: $API_KEY" \
    -d "{\"user_id\":145,\"report_id\":$report_id,\"s3_url\":\"$url\",\"environment\":\"$ENVIRONMENT\"}" > /dev/null
  echo "✓ Sent report_id: $report_id (after ${delay}s delay) [$ENVIRONMENT]"
}

# Send all requests in parallel (background processes)
send_request 101 "https://nos.jkt-1.neo.id/permata-wfe/reports/wildanal2_gmail_com/2025-11-19_174415.jpg" &
send_request 102 "https://nos.jkt-1.neo.id/permata-wfe/reports/wildanal3_gmail_com/2025-11-19_201011.jpg" &
send_request 103 "https://nos.jkt-1.neo.id/permata-wfe/reports/wildanal2_gmail_com/2025-11-19_201013.jpg" &
send_request 104 "https://nos.jkt-1.neo.id/permata-wfe/reports/wildanal2_gmail_com/2025-11-19_201443.jpg" &
send_request 105 "https://nos.jkt-1.neo.id/permata-wfe/reports/wildanal3_gmail_com/2025-11-19_201445.jpg" &
send_request 106 "https://nos.jkt-1.neo.id/permata-wfe/reports/wildanal2_gmail_com/2025-11-19_174415.jpg" &
send_request 107 "https://nos.jkt-1.neo.id/permata-wfe/reports/wildanal3_gmail_com/2025-11-19_201011.jpg" &
send_request 108 "https://nos.jkt-1.neo.id/permata-wfe/reports/wildanal2_gmail_com/2025-11-19_201013.jpg" &
send_request 109 "https://nos.jkt-1.neo.id/permata-wfe/reports/wildanal2_gmail_com/2025-11-19_201443.jpg" &
send_request 110 "https://nos.jkt-1.neo.id/permata-wfe/reports/wildanal3_gmail_com/2025-11-19_201445.jpg" &

# Wait for all background jobs to complete
wait

echo ""
echo "================================================"
echo "✅ All 10 requests sent with random delays!"
echo ""
echo "Check server logs to see parallel processing"
echo "Check /app-status to see queue status:"
echo "  curl http://localhost:8000/app-status | jq '.workers'"
