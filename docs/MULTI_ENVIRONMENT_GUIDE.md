# 🌍 Multi-Environment Setup Guide

## Overview

OCR service mendukung **2 environment** (staging & production) dalam **1 server** yang sama.

## 🔧 Cara Kerja

Client mengirim field `environment` dalam request body:
- `"environment": "staging"` → POST ke staging API
- `"environment": "production"` → POST ke production API

## ⚙️ Configuration

### 1. Setup Environment Variables (.env)

```env
# Staging Environment
LARAVEL_API_URL_STAGING=https://staging-api.your-domain.com
LARAVEL_API_KEY_STAGING=sk_staging_xxxxx

# Production Environment
LARAVEL_API_URL_PRODUCTION=https://api.your-domain.com
LARAVEL_API_KEY_PRODUCTION=sk_production_xxxxx
```

### 2. Request Format

**Staging Request:**
```json
{
  "report_id": 123,
  "user_id": 456,
  "s3_url": "https://...",
  "environment": "staging"
}
```

**Production Request:**
```json
{
  "report_id": 123,
  "user_id": 456,
  "s3_url": "https://...",
  "environment": "production"
}
```

**Default (jika tidak ada field environment):**
```json
{
  "report_id": 123,
  "user_id": 456,
  "s3_url": "https://..."
}
// Default ke staging
```

## 📝 Example Usage

### cURL - Staging
```bash
curl -X POST "http://localhost:8000/api/v1/ocr-ecosteps" \
  -H "Content-Type: application/json" \
  -H "x-api-key: YOUR_API_KEY" \
  -d '{
    "user_id": 145,
    "report_id": 101,
    "s3_url": "https://example.com/image.jpg",
    "environment": "staging"
  }'
```

### cURL - Production
```bash
curl -X POST "http://localhost:8000/api/v1/ocr-ecosteps" \
  -H "Content-Type: application/json" \
  -H "x-api-key: YOUR_API_KEY" \
  -d '{
    "user_id": 145,
    "report_id": 101,
    "s3_url": "https://example.com/image.jpg",
    "environment": "production"
  }'
```

### JavaScript/TypeScript
```javascript
// Staging
await fetch('http://localhost:8000/api/v1/ocr-ecosteps', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'x-api-key': 'YOUR_API_KEY'
  },
  body: JSON.stringify({
    user_id: 145,
    report_id: 101,
    s3_url: 'https://example.com/image.jpg',
    environment: 'staging'
  })
});

// Production
await fetch('http://localhost:8000/api/v1/ocr-ecosteps', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'x-api-key': 'YOUR_API_KEY'
  },
  body: JSON.stringify({
    user_id: 145,
    report_id: 101,
    s3_url: 'https://example.com/image.jpg',
    environment: 'production'
  })
});
```

### PHP/Laravel
```php
// Staging
Http::withHeaders([
    'x-api-key' => env('OCR_API_KEY')
])->post('http://localhost:8000/api/v1/ocr-ecosteps', [
    'user_id' => 145,
    'report_id' => 101,
    's3_url' => 'https://example.com/image.jpg',
    'environment' => 'staging'
]);

// Production
Http::withHeaders([
    'x-api-key' => env('OCR_API_KEY')
])->post('http://localhost:8000/api/v1/ocr-ecosteps', [
    'user_id' => 145,
    'report_id' => 101,
    's3_url' => 'https://example.com/image.jpg',
    'environment' => 'production'
]);
```

## 🔍 Monitoring

### Check Logs
```bash
# Staging request
📤 [Worker-1] Sending to STAGING webhook: https://staging-api.your-domain.com/api/ocr/result

# Production request
📤 [Worker-1] Sending to PRODUCTION webhook: https://api.your-domain.com/api/ocr/result
```

### Verify Configuration
```bash
# Check if environment variables are set
curl http://localhost:8000/app-status
```

## ⚠️ Important Notes

1. **Default Environment**: Jika field `environment` tidak dikirim, default ke **staging**
2. **Case Insensitive**: `"PRODUCTION"`, `"production"`, `"Production"` semua valid
3. **Invalid Environment**: Jika environment tidak valid, default ke staging
4. **Backward Compatible**: Request lama tanpa field `environment` tetap berfungsi

## 🚀 Deployment

### Update .env Production
```bash
# Edit .env
nano .env

# Add staging & production URLs
LARAVEL_API_URL_STAGING=https://staging-api.your-domain.com
LARAVEL_API_KEY_STAGING=sk_staging_xxxxx
LARAVEL_API_URL_PRODUCTION=https://api.your-domain.com
LARAVEL_API_KEY_PRODUCTION=sk_production_xxxxx
```

### Restart Service
```bash
# Docker
docker-compose restart

# Systemd
systemctl restart ocr-ecosteps

# Manual
pkill -f "uvicorn main:app"
uvicorn main:app --host 0.0.0.0 --port 8000
```

## 🧪 Testing

### Test Script
```bash
#!/bin/bash

API_URL="http://localhost:8000/api/v1/ocr-ecosteps"
API_KEY="your-api-key"

# Test Staging
echo "Testing STAGING..."
curl -X POST "$API_URL" \
  -H "Content-Type: application/json" \
  -H "x-api-key: $API_KEY" \
  -d '{
    "user_id": 145,
    "report_id": 101,
    "s3_url": "https://example.com/image.jpg",
    "environment": "staging"
  }'

# Test Production
echo "Testing PRODUCTION..."
curl -X POST "$API_URL" \
  -H "Content-Type: application/json" \
  -H "x-api-key: $API_KEY" \
  -d '{
    "user_id": 145,
    "report_id": 102,
    "s3_url": "https://example.com/image.jpg",
    "environment": "production"
  }'
```

## 📊 Benefits

✅ **Single Server**: 1 OCR server untuk 2 environment
✅ **Cost Efficient**: Tidak perlu 2 server terpisah
✅ **Easy Maintenance**: Update code sekali untuk semua environment
✅ **Flexible**: Mudah tambah environment baru (dev, qa, etc)
✅ **Backward Compatible**: Request lama tetap berfungsi

## 🔐 Security

- API keys berbeda untuk staging & production
- Webhook URLs terpisah
- Logs menunjukkan environment yang digunakan
- Tidak ada cross-environment data leak

## 🎯 Best Practices

1. **Always specify environment** di client code
2. **Use different API keys** untuk staging & production
3. **Monitor logs** untuk memastikan routing benar
4. **Test both environments** setelah deployment
5. **Document environment field** di API documentation

---

**Ready to use!** 🚀
