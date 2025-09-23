import logging
import time
import traceback
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.security import HTTPBearer
from fastapi.openapi.utils import get_openapi
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.sessions import SessionMiddleware

from app.database import engine, Base
from app.routers import auth_router, livro_router, carrinho_router, pedido_router, usuario_router
from app.utils.formatters import formatar_preco, formatar_preco_sem_simbolo, formatar_data

# ================= LOGGING =================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("../app.log", encoding="utf-8")
    ]
)
logger = logging.getLogger("BibliotecaApp")

# ================= TEMPLATES =================
templates = Jinja2Templates(directory="app/templates")
templates.env.filters["moeda"] = formatar_preco
templates.env.filters["preco_sem_simbolo"] = formatar_preco_sem_simbolo
templates.env.filters["data_br"] = formatar_data

# ================= FASTAPI APP =================
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("=== INICIANDO APLICAÇÃO BIBLIOTECA ONLINE ===")
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Tabelas verificadas/criadas com sucesso")
    except Exception as e:
        logger.error(f"❌ Erro ao criar tabelas: {e}")
        raise
    yield
    logger.info("=== APLICAÇÃO ENCERRADA ===")

security = HTTPBearer()

app = FastAPI(
    title="Biblioteca Online",
    description="Sistema de gerenciamento de biblioteca com vendas",
    version="1.0.0",
    lifespan=lifespan
)

# ================= OPENAPI COM JWT =================
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {"type": "http", "scheme": "bearer", "bearerFormat": "JWT"}
    }
    openapi_schema["security"] = [{"BearerAuth": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# ================= MIDDLEWARE =================
app.add_middleware(
    SessionMiddleware,
    secret_key="aj3kL9f#0vPqZ8w!r2Xs",
    session_cookie="biblioteca_session"
)

from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ================= STATIC FILES =================
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# ================= ROUTERS =================

app.include_router(home_router.router, tags=["Home"])   # rota principal /
app.include_router(auth_router.router, prefix="/api/auth", tags=["Autenticação"])
app.include_router(usuario_router.router, prefix="/api/usuarios", tags=["Usuários"])
app.include_router(livro_router.router, prefix="/api/livros", tags=["Livros"])
app.include_router(carrinho_router.router, prefix="/api/carrinho", tags=["Carrinho"])
app.include_router(pedido_router.router, prefix="/api/pedidos", tags=["Pedidos"])


# ================= HANDLERS DE ERRO =================
@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request: Request, exc: StarletteHTTPException):
    if exc.status_code == 404:
        return templates.TemplateResponse(
            "404.html",
            {"request": request, "mensagem": "Página não encontrada"},
            status_code=404
        )
    return HTMLResponse(str(exc.detail), status_code=exc.status_code)

@app.exception_handler(500)
async def internal_server_error_handler(request: Request, exc: Exception):
    logger.error(f"Erro interno do servidor: {exc}", exc_info=True)
    detalhes_erro = "".join(traceback.format_exception(None, exc, exc.__traceback__))
    return templates.TemplateResponse(
        "erro.html",
        {"request": request, "mensagem": "Erro interno do servidor", "detalhes": detalhes_erro},
        status_code=500
    )

# ================= EXECUÇÃO =================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True, log_level="info")
