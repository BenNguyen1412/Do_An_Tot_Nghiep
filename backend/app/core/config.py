from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database Settings
    DB_HOST: str = "localhost"
    DB_PORT: str = "5432"
    DB_DATABASE: str = "postgres"
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "141204"
    
    # JWT Settings
    SECRET_KEY: str = "OceXRNLlufuBtERHT-pXEgsa_v5KFCA7Ny12PPDCOTI"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Application Settings
    DEBUG: bool = True
    
    # CORS
    BACKEND_CORS_ORIGINS: list = ["http://localhost:5173", "http://localhost:3000"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()

# Tạo DATABASE_URL từ các thông tin
def get_database_url() -> str:
    return f"postgresql://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_DATABASE}"