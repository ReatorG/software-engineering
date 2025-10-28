import os
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Configuración del modelo ML
    ml_model_name: str = "mistralai/Mistral-7B-Instruct-v0.3"
    ml_model_device: str = "auto"
    ml_model_dtype: str = "float16"
    max_new_tokens: int = 700
    
    # Configuración de la API
    api_host: str = "localhost"
    api_port: int = 8000
    debug_mode: bool = False
    
    # Configuración de logging
    log_level: str = "INFO"
    log_file: Optional[str] = None
    
    # Configuración de base de datos PostgreSQL
    database_url: str = "postgresql://postgres:postgres@localhost:5433/postgres"
    database_host: str = "localhost"
    database_port: int = 5433
    database_name: str = "postgres"
    database_user: str = "postgres"
    database_password: str = "postgres"
    
    class Config:
        env_file = ".env"
        env_prefix = "APP_" 

# Instancia global de configuración
settings = Settings()
