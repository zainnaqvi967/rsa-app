"""
Application Configuration
=========================
This file contains all the settings for our application.
We keep them in one place so they're easy to find and change.

For beginners:
- Settings are like "global variables" that control how the app behaves
- In production, you'd load these from environment variables (.env file)
- For development, we use simple default values
"""

import os


class Settings:
    """
    All application settings in one place.
    
    Usage:
        from app.core.config import settings
        print(settings.DATABASE_URL)
    """
    
    # ===================
    # DATABASE SETTINGS
    # ===================
    # SQLite creates a file called 'rsa.db' in your project folder
    # The 'sqlite:///' prefix tells SQLAlchemy to use SQLite
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./rsa.db")
    
    # ===================
    # JWT SETTINGS
    # ===================
    # JWT (JSON Web Token) is how we keep users logged in
    # The SECRET_KEY is used to sign tokens - keep it secret in production!
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "your-super-secret-key-change-in-production")
    JWT_ALGORITHM: str = "HS256"  # The encryption algorithm
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # Token valid for 24 hours
    
    # ===================
    # OTP SETTINGS
    # ===================
    # OTP = One-Time Password (the code sent to your phone)
    # For development, we use a fixed OTP so you don't need real SMS
    DEMO_OTP: str = "1234"
    
    # ===================
    # APP SETTINGS
    # ===================
    APP_NAME: str = "RSA - Roadside Assistance API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"


# Create a single instance that we import everywhere
# This is called the "singleton pattern" - only one Settings object exists
settings = Settings()

