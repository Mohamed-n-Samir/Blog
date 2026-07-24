from pydantic import SecretStr
from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

load_dotenv()

class Settings(BaseSettings):
    # Database
    database_url: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./blog.db")

    # Server
    port: int = int(os.getenv("PORT", "8000"))
    host: str = os.getenv("HOST", "0.0.0.0")
    environment: str = os.getenv("ENVIRONMENT", "development")
    debug: bool = os.getenv("DEBUG", "true").lower() == "true"
    app_mode: str = os.getenv("APP_MODE", "full")

    # JWT (Single Token System)
    secret_key: SecretStr = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    algorithm: str = os.getenv("ALGORITHM", "HS256")
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "10080"))  # 7 days

    max_upload_size_bytes: int = 5 * 1024 * 1024

    class Config:
        env_file = ".env"
        case_sensitive = False

# Create global settings instance
settings = Settings()