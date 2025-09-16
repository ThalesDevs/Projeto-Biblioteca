from sqlalchemy import create_engine

engine = create_engine("postgresql+psycopg2://biblioteca:123456@localhost:5433/biblioteca")
conn = engine.connect()
print("Conexão OK")
conn.close()
