from pydantic_settings import BaseSettings
from typing import List
from pydantic import AnyHttpUrl

class Settings(BaseSettings):
    APP_NAME: str
    VERSION: str = "1.0.0"
    DEBUG: bool = True
    SECRET_KEY: str

    # Banco de dados
    DATABASE_URL: str

    # Email
    SMTP_SERVER: str
    SMTP_PORT: int
    EMAIL_USUARIO: str
    EMAIL_SENHA: str

    # App
    BASE_URL: AnyHttpUrl
    NOME_SITE: str = "Biblioteca Online"

    # CORS
    ALLOWED_ORIGINS: List[str] = []

    class Config:
        env_file = ".env"

settings = Settings()
