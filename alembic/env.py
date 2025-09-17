from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
from dotenv import load_dotenv
import os
import sys

# =========================
# Carrega .env e ajusta path
# =========================
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(project_root)  # Para que 'app' seja encontrado
load_dotenv(os.path.join(project_root, ".env"))

# =========================
# Importa Base do SQLAlchemy
# =========================
from app.database import Base

# =========================
# Config Alembic
# =========================
config = context.config
fileConfig(config.config_file_name)
target_metadata = Base.metadata

# Substitui URL do banco pelo .env
database_url = os.getenv("DATABASE_URL")
if not database_url:
    raise RuntimeError("Variável DATABASE_URL não encontrada no .env")
config.set_main_option("sqlalchemy.url", database_url)

# =========================
# Migrations offline
# =========================
def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
    )
    with context.begin_transaction():
        context.run_migrations()

# =========================
# Migrations online
# =========================
def run_migrations_online():
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()

# =========================
# Executa migrações
# =========================
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
