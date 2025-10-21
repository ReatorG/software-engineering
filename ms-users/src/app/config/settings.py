from pydantic_settings import BaseSettings
from pathlib import Path

# Buscar .env en el directorio raíz del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
ENV_FILE = BASE_DIR / ".env"

class Settings(BaseSettings):
    # DB
    DATABASE_URL: str

    # App
    APP_ENV: str = "development"
    DEBUG: bool = True

    # Seguridad JWT
    SECRET_KEY: str = "secret-demo"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Seguridad Passwords
    PASSWORD_SCHEME: str = "bcrypt" 

    # CORS
    ALLOWED_ORIGINS: list[str] = ["*"]

    class Config:
        env_file = str(ENV_FILE)

settings = Settings()
