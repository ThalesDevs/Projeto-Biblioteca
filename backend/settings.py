from dotenv import load_dotenv
import os

load_dotenv()  # carrega variáveis do .env

DATABASE_URL = os.getenv("DATABASE_URL")
SECRET_KEY = os.getenv("SECRET_KEY", "mude-essa-chave-em-producao")
