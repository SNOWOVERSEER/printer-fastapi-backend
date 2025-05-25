from pydantic_settings import BaseSettings
from typing import Optional, Literal
import secrets
import os

environment = os.getenv("ENVIRONMENT", "development")
env_file_map = {
    "development": ".env.development",
    "production": ".env.production", 
}
selected_env_file = env_file_map.get(environment, ".env")

class Settings(BaseSettings):
    
    # Environment Configuration
    ENVIRONMENT: Literal["development", "production"] = "development"
    DEBUG: bool = True
    
    PROJECT_NAME: str = "Printer API"
    APP_NAME: str
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"
    FRONTEND_URL: str
    
    # Security Configuration
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day
    
    # Database Configuration
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_PORT: int = 5432
    POSTGRES_HOST: str
    POSTGRES_URL: str
    SQLALCHEMY_DATABASE_URI: Optional[str] = None
    
    # Stripe Configuration
    STRIPE_SECRET_KEY: str
    STRIPE_WEBHOOK_SECRET: str
    
    # File Upload Configuration
    UPLOAD_FOLDER: str = "uploads"
    MAX_CONTENT_LENGTH: int = 16 * 1024 * 1024  # 16MB
    
    # CORS Configuration
    ALLOWED_ORIGINS_RAW: str = "http://localhost:3000"
    ALLOWED_ORIGINS: list[str] = []
    
    # Cloudflare Configuration (for production)
    CLOUDFLARE_TUNNEL_TOKEN: Optional[str] = None
    CLOUDFLARE_TUNNEL_URL: Optional[str] = None
    
    class Config:
        case_sensitive = True
        env_file = selected_env_file

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        
        if not self.SQLALCHEMY_DATABASE_URI:
            self.SQLALCHEMY_DATABASE_URI = (
                f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
                f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
            )
        
        # production environment
        if self.ENVIRONMENT == "production":
            self.DEBUG = True # TODO: change to False
            if self.ALLOWED_ORIGINS_RAW:
                self.ALLOWED_ORIGINS = [origin.strip() for origin in self.ALLOWED_ORIGINS_RAW.split(",")]
            if self.CLOUDFLARE_TUNNEL_URL:
                self.ALLOWED_ORIGINS.append(self.CLOUDFLARE_TUNNEL_URL)
        elif self.ENVIRONMENT == "development":
            self.DEBUG = True
            # development environment
            self.ALLOWED_ORIGINS.extend([
                "http://localhost:3000",
                "http://127.0.0.1:3000",
                "http://localhost:8080"
            ])
            
        print(f"🔧 Loading configuration from: {selected_env_file}")
        print(f"🌍 Environment: {self.ENVIRONMENT}")
        print(f"🐛 Debug mode: {self.DEBUG}")
        print(f"🔧 ALLOWED_ORIGINS: {self.ALLOWED_ORIGINS}")

settings = Settings()