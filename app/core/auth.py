from fastapi import Header, HTTPException, status
from decouple import config
from app.core.logger import setup_logger

logger = setup_logger(__name__)

async def verify_api_key(x_api_key: str = Header(None)):
    """Verify API key from header"""
    expected_key = config("API_KEY", default="")
    
    if not expected_key:
        logger.warning("⚠ API_KEY not configured")
        return True
    
    if not x_api_key:
        logger.error("✘ Missing API key")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": "Unauthorized", "message": "API key is required"}
        )
    
    if x_api_key != expected_key:
        logger.error("✘ Invalid API key")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"error": "Forbidden", "message": "Invalid API key"}
        )
    
    logger.info("✓ API key validated")
    return True
