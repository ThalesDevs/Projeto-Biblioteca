import os
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Carrega o .env do diretório pai
project_root = Path(__file__).parent.parent
dotenv_path = project_root / ".env"
load_dotenv(dotenv_path)

# Configurações do banco vindas do .env
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    # Fallback usando variáveis individuais
    user = os.getenv("POSTGRES_USER", "biblioteca")
    password = os.getenv("POSTGRES_PASSWORD", "123456")
    host = os.getenv("POSTGRES_HOST", "localhost")
    port = os.getenv("POSTGRES_PORT", "5432")
    db_name = os.getenv("POSTGRES_DB", "biblioteca")
    DATABASE_URL = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{db_name}"

print(f"Conectando ao banco: {DATABASE_URL.split('@')[1]}")  # Log sem senha

# Engine com configurações otimizadas para containers
engine = create_engine(
    DATABASE_URL,
    echo=False,  # Mudado para False em produção
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,  # Importante para containers
    pool_recycle=3600
)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()

def get_db():
    """Dependency para FastAPI"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()