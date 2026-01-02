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

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    return Settings()
