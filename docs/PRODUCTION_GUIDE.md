# 🚀 Production Deployment Guide - High Traffic (7000 users/day)

## 📊 Capacity Planning

### Current Capacity Analysis:
- **7000 users/day** = ~292 users/hour average
- **Peak time (20% in 2h)** = ~700 users/hour = ~12 users/minute
- **Processing time**: ~25 seconds/task average
- **Required capacity**: 12 tasks/minute = 5 seconds/task needed

### Recommended Configuration:

#### Small Server (4 CPU + GPU):
```env
WORKER_COUNT=5
MAX_QUEUE_SIZE=500
```
**Capacity**: ~12 tasks/minute (sufficient for average load)

#### Medium Server (8 CPU + GPU):
```env
WORKER_COUNT=10
MAX_QUEUE_SIZE=1000
```
**Capacity**: ~24 tasks/minute (2x peak capacity) ✅ **RECOMMENDED**

#### Large Server (16 CPU + 2 GPU):
```env
WORKER_COUNT=20
MAX_QUEUE_SIZE=2000
```
**Capacity**: ~48 tasks/minute (4x peak capacity)

---

## ⚠️ Critical Production Checklist

### 1. Environment Variables
```bash
# Copy and edit production config
cp .env.production .env

# MUST CHANGE:
API_KEY=<generate-strong-random-key>
LARAVEL_API_KEY=<your-laravel-api-key>
LARAVEL_API_URL=https://your-production-api.com

# Tune based on server:
WORKER_COUNT=10  # 1-2x CPU cores
MAX_QUEUE_SIZE=1000  # 2-3 hours of peak traffic
```

### 2. Server Requirements

**Minimum (7000 users/day):**
- CPU: 8 cores
- RAM: 16 GB
- GPU: NVIDIA with 6GB+ VRAM (optional but recommended)
- Disk: 50 GB SSD
- Network: 100 Mbps

**Recommended (with headroom):**
- CPU: 16 cores
- RAM: 32 GB
- GPU: NVIDIA RTX 3060+ (12GB VRAM)
- Disk: 100 GB NVMe SSD
- Network: 1 Gbps

### 3. Monitoring Setup

**Essential Metrics:**
```bash
# Queue size
curl https://your-api.com/app-status | jq '.queue.waiting_in_queue'

# Worker status
curl https://your-api.com/app-status | jq '.workers'

# System resources
curl https://your-api.com/app-status | jq '.system'
```

**Alert Thresholds:**
- Queue size > 800 (80% capacity) → Scale up
- CPU usage > 80% → Add workers or scale horizontally
- Memory usage > 85% → Investigate memory leak
- Failed tasks > 5% → Check OCR/webhook issues

### 4. Load Balancing (For >10k users/day)

**Horizontal Scaling:**
```yaml
# docker-compose.prod.yml
services:
  ocr-api-1:
    image: ocr-ecosteps:latest
    environment:
      - WORKER_COUNT=10
  
  ocr-api-2:
    image: ocr-ecosteps:latest
    environment:
      - WORKER_COUNT=10
  
  nginx:
    image: nginx:alpine
    # Load balance between ocr-api-1 and ocr-api-2
```

### 5. Database/Redis (Optional but Recommended)

**For persistent queue:**
```python
# Use Redis for queue instead of in-memory
# Benefits:
# - Survives restarts
# - Shared across multiple instances
# - Better monitoring
```

---

## 🔒 Security Hardening

### 1. Rate Limiting (CRITICAL!)
```python
# Add to routes.py
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@router.post("/api/v1/ocr-ecosteps")
@limiter.limit("10/minute")  # Max 10 requests per minute per IP
async def submit_ocr_queue(data: OCRRequest):
    ...
```

### 2. API Key Rotation
- Rotate API keys every 90 days
- Use different keys for dev/staging/production
- Store in secrets manager (AWS Secrets Manager, HashiCorp Vault)

### 3. HTTPS Only
```bash
# Use reverse proxy (Nginx/Traefik) with SSL
# Redirect HTTP → HTTPS
# Use Let's Encrypt for free SSL certificates
```

---

## 📈 Performance Optimization

### 1. GPU Optimization
```python
# Already implemented:
# - Singleton EasyOCR reader
# - Thread-safe GPU access
# - Batch processing ready
```

### 2. Image Caching
```python
# Add Redis cache for processed images
# Cache key: hash(image_url)
# TTL: 24 hours
# Reduces duplicate processing
```

### 3. CDN for Images
- Use CloudFlare/AWS CloudFront
- Reduces image download time
- Saves bandwidth

---

## 🚨 Disaster Recovery

### 1. Backup Strategy
```bash
# Backup logs daily
tar -czf logs-$(date +%Y%m%d).tar.gz app.log

# Backup queue state (if using Redis)
redis-cli SAVE
```

### 2. Graceful Shutdown
```bash
# Already implemented in lifespan()
# Workers finish current tasks before shutdown
docker-compose down  # Waits for workers
```

### 3. Health Checks
```yaml
# docker-compose.prod.yml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 40s
```

---

## 📊 Monitoring Dashboard (Recommended)

### Grafana + Prometheus Setup:
```yaml
# Add to docker-compose.prod.yml
prometheus:
  image: prom/prometheus
  volumes:
    - ./prometheus.yml:/etc/prometheus/prometheus.yml

grafana:
  image: grafana/grafana
  ports:
    - "3000:3000"
```

### Key Metrics to Track:
- Requests per minute
- Queue size over time
- Processing time percentiles (p50, p95, p99)
- Error rate
- Worker utilization
- GPU memory usage

---

## 🎯 Go-Live Checklist

- [ ] Environment variables configured
- [ ] API keys changed from defaults
- [ ] HTTPS enabled
- [ ] Rate limiting configured
- [ ] Monitoring setup
- [ ] Alerts configured
- [ ] Backup strategy in place
- [ ] Load testing completed (see below)
- [ ] Disaster recovery plan documented
- [ ] Team trained on monitoring/alerts

---

## 🧪 Load Testing

### Before Production:
```bash
# Install Apache Bench
sudo apt-get install apache2-utils

# Test with 1000 requests, 50 concurrent
ab -n 1000 -c 50 -H "x-api-key: YOUR_KEY" \
   -p test_payload.json -T application/json \
   https://your-api.com/api/v1/ocr-ecosteps

# Expected results:
# - 95% requests < 30 seconds
# - 0% failed requests
# - No memory leaks
```

---

## 📞 Support & Troubleshooting

### Common Issues:

**Queue Full:**
- Increase `MAX_QUEUE_SIZE`
- Add more workers
- Scale horizontally

**High Memory Usage:**
- Check for memory leaks in logs
- Restart workers periodically
- Reduce `WORKER_COUNT`

**Slow Processing:**
- Check GPU utilization
- Optimize image preprocessing
- Use faster storage (NVMe SSD)

**Webhook Failures:**
- Check Laravel API health
- Increase timeout
- Add retry logic

---

## 🚀 Deployment Commands

### Docker Production:
```bash
# Build
docker build -f Dockerfile.prod -t ocr-ecosteps:latest .

# Deploy
docker-compose -f docker-compose.prod.yml up -d

# Monitor logs
docker-compose -f docker-compose.prod.yml logs -f

# Scale workers
docker-compose -f docker-compose.prod.yml up -d --scale ocr-api=3
```

### Kubernetes (Advanced):
```bash
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/hpa.yaml  # Auto-scaling
```

---

## 📈 Success Metrics

**Target SLAs:**
- Uptime: 99.9% (8.76 hours downtime/year)
- Response time: < 30 seconds (95th percentile)
- Error rate: < 1%
- Queue wait time: < 5 minutes (peak)

**Monitor Weekly:**
- Total requests processed
- Average processing time
- Error rate trend
- Peak load capacity

---

**READY FOR 7000+ USERS/DAY!** 🎉
