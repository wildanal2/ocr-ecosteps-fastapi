#!/bin/bash

API_URL="http://localhost:8000/api/v1/ocr-ecosteps"
API_KEY="sk_fast_ji2348sdf9snjamau66asd8nh3"

echo "🧪 Testing OCR Queue - Parallel Processing Test"
echo "================================================"
echo "Sending 10 UNIQUE requests simultaneously..."
echo ""

# Send all requests in parallel (background processes)
curl -X POST "$API_URL" -H "Content-Type: application/json" -H "x-api-key: $API_KEY" \
  -d '{"user_id":145,"report_id":101,"s3_url":"https://nos.jkt-1.neo.id/permata-wfe/reports/wildanal2_gmail_com/2025-11-19_174415.jpg"}' &

curl -X POST "$API_URL" -H "Content-Type: application/json" -H "x-api-key: $API_KEY" \
  -d '{"user_id":145,"report_id":102,"s3_url":"https://nos.jkt-1.neo.id/permata-wfe/reports/wildanal3_gmail_com/2025-11-19_201011.jpg"}' &

curl -X POST "$API_URL" -H "Content-Type: application/json" -H "x-api-key: $API_KEY" \
  -d '{"user_id":145,"report_id":103,"s3_url":"https://nos.jkt-1.neo.id/permata-wfe/reports/wildanal2_gmail_com/2025-11-19_201013.jpg"}' &

curl -X POST "$API_URL" -H "Content-Type: application/json" -H "x-api-key: $API_KEY" \
  -d '{"user_id":145,"report_id":104,"s3_url":"https://nos.jkt-1.neo.id/permata-wfe/reports/wildanal2_gmail_com/2025-11-19_201443.jpg"}' &

curl -X POST "$API_URL" -H "Content-Type: application/json" -H "x-api-key: $API_KEY" \
  -d '{"user_id":145,"report_id":105,"s3_url":"https://nos.jkt-1.neo.id/permata-wfe/reports/wildanal3_gmail_com/2025-11-19_201445.jpg"}' &

curl -X POST "$API_URL" -H "Content-Type: application/json" -H "x-api-key: $API_KEY" \
  -d '{"user_id":145,"report_id":106,"s3_url":"https://nos.jkt-1.neo.id/permata-wfe/reports/wildanal2_gmail_com/2025-11-19_174415.jpg"}' &

curl -X POST "$API_URL" -H "Content-Type: application/json" -H "x-api-key: $API_KEY" \
  -d '{"user_id":145,"report_id":107,"s3_url":"https://nos.jkt-1.neo.id/permata-wfe/reports/wildanal3_gmail_com/2025-11-19_201011.jpg"}' &

curl -X POST "$API_URL" -H "Content-Type: application/json" -H "x-api-key: $API_KEY" \
  -d '{"user_id":145,"report_id":108,"s3_url":"https://nos.jkt-1.neo.id/permata-wfe/reports/wildanal2_gmail_com/2025-11-19_201013.jpg"}' &

curl -X POST "$API_URL" -H "Content-Type: application/json" -H "x-api-key: $API_KEY" \
  -d '{"user_id":145,"report_id":109,"s3_url":"https://nos.jkt-1.neo.id/permata-wfe/reports/wildanal2_gmail_com/2025-11-19_201443.jpg"}' &

curl -X POST "$API_URL" -H "Content-Type: application/json" -H "x-api-key: $API_KEY" \
  -d '{"user_id":145,"report_id":110,"s3_url":"https://nos.jkt-1.neo.id/permata-wfe/reports/wildanal3_gmail_com/2025-11-19_201445.jpg"}' &

# Wait for all background jobs to complete
wait

echo ""
echo "================================================"
echo "✅ All 5 requests sent in parallel!"
echo ""
echo "Check server logs to see parallel processing"
echo "Check /app-status to see queue status:"
echo "  curl http://localhost:8000/app-status | jq '.workers'"
