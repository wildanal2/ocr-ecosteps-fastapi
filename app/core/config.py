from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "OCR EcoSteps API"
    APP_VERSION: str = "1.0.3"
    APP_DESCRIPTION: str = "Professional OCR API for extracting fitness tracking data using EasyOCR"
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    class Config:
        case_sensitive = True

settings = Settings()
