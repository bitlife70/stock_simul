try:
    from pydantic_settings import BaseSettings
except ImportError:
    from pydantic import BaseSettings
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "sqlite:///./stock_backtesting.db"
    )
    
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Korean Stock Backtesting API"
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    
    # Redis (for caching)
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # Data Sources
    USE_CACHE: bool = True
    CACHE_EXPIRE_SECONDS: int = 60 * 60  # 1 hour
    
    # Korean Market Settings
    DEFAULT_MARKET: str = "KOSPI"
    AVAILABLE_MARKETS: list = ["KOSPI", "KOSDAQ", "KONEX"]
    
    # Backtesting Settings
    DEFAULT_INITIAL_CAPITAL: int = 10_000_000  # 1000만원
    MAX_POSITIONS: int = 20
    DEFAULT_COMMISSION: float = 0.003  # 0.3%
    
    class Config:
        env_file = ".env"

settings = Settings()