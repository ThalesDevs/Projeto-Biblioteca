from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
from dotenv import load_dotenv
import os
import sys

# Adiciona o diretório raiz ao path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(project_root)

# Carrega variáveis de ambiente
env_path = os.path.join(project_root, ".env")
load_dotenv(env_path)

# Configuração do Alembic
config = context.config

# Interpreta o arquivo de config para logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Importa os modelos para auto-geração
try:
    from app.database import Base
    from app.models import *  # Importa todos os modelos

    target_metadata = Base.metadata
except ImportError as e:
    print(f"Erro ao importar modelos: {e}")
    target_metadata = None


# Obtém a URL do banco
def get_database_url():
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        user = os.getenv("POSTGRES_USER", "biblioteca")
        password = os.getenv("POSTGRES_PASSWORD", "123456")
        host = os.getenv("POSTGRES_HOST", "localhost")
        port = os.getenv("POSTGRES_PORT", "5432")
        db_name = os.getenv("POSTGRES_DB", "biblioteca")
        database_url = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{db_name}"
    return database_url


# Define a URL do banco
config.set_main_option("sqlalchemy.url", get_database_url())


def run_migrations_offline() -> None:
    """Executa migrações em modo 'offline'."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Executa migrações em modo 'online'."""
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = get_database_url()

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()