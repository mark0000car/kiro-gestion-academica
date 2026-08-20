"""
Configuración de la aplicación cargada desde variables de entorno (.env).
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Base de datos
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "gac"
    db_user: str = "postgres"
    db_password: str = "postgres"
    database_url: str = "postgresql://postgres:postgres@localhost:5432/gac"

    # API
    api_port: int = 8000

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


# Instancia global reutilizable
settings = Settings()
