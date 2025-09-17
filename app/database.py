import os
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Carrega o .env, mesmo dentro do container
dotenv_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path)

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://biblioteca:123456@localhost:5432/biblioteca"
)

engine = create_engine(DATABASE_URL, echo=True)  # echo=True para debug
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()
