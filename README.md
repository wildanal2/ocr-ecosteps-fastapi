# OCR EcoSteps API

Professional OCR API for extracting fitness tracking data from images using EasyOCR.

## Features

- 🚀 FastAPI framework for high performance
- 📝 EasyOCR integration for text extraction
- 🔍 Smart regex-based data extraction
- 📊 Health check and status endpoints
- 📋 Comprehensive logging
- 🎯 Professional project structure

## Project Structure

```
ocr-ecosteps/
├── main.py              # FastAPI entry point
├── requirements.txt     # Python dependencies
├── README.md           # Documentation
├── app.log             # Application logs
├── app/                # Application package
│   ├── api/            # API routes
│   │   └── routes.py   # Endpoint definitions
│   ├── core/           # Core functionality
│   │   ├── config.py   # Configuration settings
│   │   └── logger.py   # Logging setup
│   └── models/         # Pydantic models
│       └── responses.py # Response schemas
└── research/           # Research and development files
    ├── ocr_best.py     # Base OCR implementation
    └── ...             # Other experimental files
```

## Installation

1. Clone the repository
```bash
cd ocr-ecosteps
```

2. Create virtual environment
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

## Usage

### Development Mode

#### Local Development
```bash
python main.py
```

Or using uvicorn directly:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### Docker Development
```bash
# Build and run
docker-compose up --build

# Run in background
docker-compose up -d

# Stop containers
docker-compose down
```

### API Endpoints

#### Root
```bash
GET /
```
Returns API information and documentation link.

#### Health Check
```bash
GET /health
```
Returns service health status and timestamp.

Response:
```json
{
  "status": "healthy",
  "timestamp": "2025-01-06T10:30:00",
  "service": "ocr-ecosteps"
}
```

#### Status
```bash
GET /status
```
Returns service status, uptime, and version.

Response:
```json
{
  "status": "running",
  "uptime": "0:15:30",
  "version": "1.0.0"
}
```

### Interactive Documentation

Access the auto-generated API documentation:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Production Deployment

### Docker Production Deployment

#### Build Production Image
```bash
docker build -f Dockerfile.prod -t ocr-ecosteps:latest .
```

#### Run with Docker Compose (Recommended)
```bash
# Start production container
docker-compose -f docker-compose.prod.yml up -d

# View logs
docker-compose -f docker-compose.prod.yml logs -f

# Stop container
docker-compose -f docker-compose.prod.yml down
```

#### Run with Docker
```bash
docker run -d \
  --name ocr-ecosteps \
  -p 8000:8000 \
  -e APP_NAME="OCR EcoSteps API" \
  -e APP_VERSION="1.0.0" \
  --restart unless-stopped \
  ocr-ecosteps:latest
```

### Environment Variables

| Variable | Description | Default |
|----------|-------------|----------|
| APP_NAME | Application name | OCR EcoSteps API |
| APP_VERSION | Application version | 1.0.0 |
| HOST | Server host | 0.0.0.0 |
| PORT | Server port | 8000 |
| LOG_LEVEL | Logging level | INFO |

### Production Checklist

- ✅ Use `Dockerfile.prod` for production builds
- ✅ Configure environment variables
- ✅ Set up reverse proxy (Nginx/Traefik)
- ✅ Enable HTTPS/SSL certificates
- ✅ Configure resource limits
- ✅ Set up monitoring and logging
- ✅ Regular backups
- ✅ Health check endpoints configured

### Scaling

To scale the application:
```bash
docker-compose -f docker-compose.prod.yml up -d --scale ocr-api=3
```

## Development

The `research/` folder contains experimental OCR implementations:
- `ocr_best.py` - Base EasyOCR implementation with smart extraction
- Other `.py` and `.ipynb` files - Various OCR experiments

## Logging

Application logs are written to:
- Console (stdout)
- `app.log` file

Log format: `timestamp - logger_name - level - message`

## Technology Stack

- **FastAPI** - Modern web framework
- **EasyOCR** - OCR engine
- **OpenCV** - Image preprocessing
- **Uvicorn** - ASGI server
- **Pydantic** - Data validation

## License

MIT

## Author

OCR EcoSteps Team
