#!/bin/sh
set -e

DB_HOST=${DB_HOST:-${POSTGRES_HOST:-biblioteca_db}}
DB_PORT=${DB_PORT:-${POSTGRES_PORT:-5432}}

echo "⏳ Aguardando o banco de dados em $DB_HOST:$DB_PORT..."

# Espera até o banco estar disponível
while ! nc -z "$DB_HOST" "$DB_PORT"; do
  sleep 1
done

echo "✅ Banco de dados pronto!"

# Atualiza capas dos livros
python ./app/utils/atualizar_capas_pg.py

# Executa o comando principal do container (uvicorn)
exec "$@"
