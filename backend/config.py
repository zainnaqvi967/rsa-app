"""
Application configuration module.

Loads environment variables and provides configuration settings.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings:
    """Application settings loaded from environment variables."""
    
    # JWT Configuration
    JWT_SECRET: str = os.getenv("JWT_SECRET", "devsecret")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
    
    # Demo OTP (for development)
    DEMO_OTP: str = "1234"
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./roadside_assistance.db")


# Create a global settings instance
settings = Settings()

