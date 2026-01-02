from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings."""
    
    database_url: str = "postgresql+asyncpg://qr_user:qr_password@localhost:5432/qr_que_db"
    redis_url: str = "redis://localhost:6379"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    
    # CORS settings
    cors_origins: list[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "https://staff.kaskyralmaty.dev",
        "https://display.kaskyralmaty.dev",
        "https://track.kaskyralmaty.dev",
    ]
    
    # Token generation
    token_length: int = 8
    
    # QR display timeout (seconds)
    qr_display_timeout: int = 30
    
    # JWT settings
    secret_key: str = "your-secret-key-change-in-production-make-it-long-and-random"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24 * 7  # 7 days
    
    # Default admin credentials (change in production!)
    admin_username: str = "admin"
    admin_password: str = "admin123"
    
    # Demo account credentials
    demo_username: str = "demo"
    demo_password: str = "demo123"

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    return Settings()
