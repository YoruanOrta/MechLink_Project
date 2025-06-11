from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Database - SQLite for development
    DATABASE_URL: str = "sqlite:///./mechlink.db"
    
    # JWT
    SECRET_KEY: str = "tu-clave-secreta-muy-larga-y-segura-aqui-12345-mechlink"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    
    # App
    APP_NAME: str = "MechLink API"
    VERSION: str = "1.0.0"
    DEBUG: bool = True

settings = Settings()