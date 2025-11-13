from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from app.api.routes import router
from app.core.config import settings
from app.core.logger import setup_logger
from app.core.queue import lifespan

logger = setup_logger(__name__)

app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
    lifespan=lifespan
)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    logger.error(f"✘ Validation error on {request.url.path}: {errors}")
    
    error_messages = []
    for error in errors:
        field = " -> ".join(str(loc) for loc in error["loc"])
        message = error["msg"]
        error_messages.append(f"{field}: {message}")
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "Validation Error",
            "message": "Data yang dikirim tidak valid",
            "details": error_messages
        }
    )

app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    logger.info(f"Starting {settings.APP_NAME}...")
    uvicorn.run(app, host=settings.HOST, port=settings.PORT)
