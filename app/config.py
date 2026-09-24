import os
from pydantic import BaseModel

class Settings(BaseModel):
    APP_NAME: str = "Private Millionaires Barber Studio"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "pm_barber_studio_ultra_secure_jwt_secret_2026_x89a")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./barber_studio.db")
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "static/images/uploads")
    
    # Studio Details
    STUDIO_NAME: str = "Private Millionaires Barber Studio"
    STUDIO_TAGLINE: str = "Luxury Grooming, Master Craftsmanship & VIP Precision"
    STUDIO_ADDRESS: str = "1740 East Washington Street, Colton, CA 92324"
    STUDIO_PHONE: str = "(909) 430-4591"
    STUDIO_EMAIL: str = "vip@privatemillionairesbarber.com"
    STUDIO_MAPS_URL: str = "https://maps.app.goo.gl/F4WUJes6jkD8sakB6"
    
settings = Settings()
