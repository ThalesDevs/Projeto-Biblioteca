import requests
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv

dotenv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '.env'))

load_dotenv()

db_config = {
    'user': os.getenv('POSTGRES_USER'),
    'password': os.getenv('POSTGRES_PASSWORD'),
    'host': os.getenv('POSTGRES_HOST'),
    'database': os.getenv('POSTGRES_DB'),
    'port': os.getenv('POSTGRES_PORT')
}


def buscar_url_capa(titulo, autor):
    """Busca a URL da capa de um livro na API do Google Books."""
    query = f"{titulo} {autor}"
    url_api = f"https://www.googleapis.com/books/v1/volumes?q={query}&maxResults=1"

    try:
        response = requests.get(url_api)
        response.raise_for_status()

        dados = response.json()

        if 'items' in dados and dados['items']:
            item = dados['items'][0]
            if 'imageLinks' in item['volumeInfo']:
                url_capa = item['volumeInfo']['imageLinks'].get('thumbnail', '')
                return url_capa

        return None

    except requests.exceptions.RequestException as e:
        print(f"Erro ao buscar capa para '{titulo}' ({autor}): {e}")
        return None


def atualizar_capas_no_banco():
    """Conecta ao banco e atualiza as URLs de capa dos livros."""
    conn = None
    try:
        print("Conectando ao banco de dados PostgreSQL...")
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        print("Conexão bem-sucedida.")

        cursor.execute("SELECT id, titulo, autor FROM livros WHERE capa_url IS NULL OR capa_url = ''")
        livros_sem_capa = cursor.fetchall()

        if not livros_sem_capa:
            print("Todos os livros já têm capa registrada.")
            return

        print(f"Encontrados {len(livros_sem_capa)} livros sem capa. Iniciando a busca...")

        for livro in livros_sem_capa:
            print(f"Buscando capa para: '{livro['titulo']}' de '{livro['autor']}'...")
            url_imagem = buscar_url_capa(livro['titulo'], livro['autor'])

            if url_imagem:
                print(f" -> Capa encontrada: {url_imagem}")
                cursor.execute(
                    "UPDATE livros SET capa_url = %s WHERE id = %s",
                    (url_imagem, livro['id'])
                )
            else:
                print(f" -> Capa não encontrada para: '{livro['titulo']}'")

        conn.commit()
        print("Processo de atualização de capas concluído.")

    except psycopg2.Error as e:
        print(f"Erro no banco de dados: {e}")
    finally:
        if conn:
            cursor.close()
            conn.close()
            print("Conexão com o banco de dados fechada.")

if __name__ == "__main__":
    atualizar_capas_no_banco()
