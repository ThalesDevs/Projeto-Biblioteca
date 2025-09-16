from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from dotenv import load_dotenv

load_dotenv()

# Usar variável de ambiente ou fallback
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://biblioteca:123456@localhost:5433/biblioteca"
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()