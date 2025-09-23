FROM python:3.12-slim

# Dependências do sistema
RUN apt-get update \
    && apt-get install -y --no-install-recommends netcat-openbsd dnsutils dos2unix \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Instala dependências Python
COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia a aplicação
COPY main.py .
COPY app ./app/

# Corrige finais de linha e permissões
RUN dos2unix ./app/utils/entrypoint.sh && chmod +x ./app/utils/entrypoint.sh \
    && dos2unix ./app/utils/atualizar_capas_pg.py && chmod +x ./app/utils/atualizar_capas_pg.py

EXPOSE 8000

ENTRYPOINT ["./app/utils/entrypoint.sh"]
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
