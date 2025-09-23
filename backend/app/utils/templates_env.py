from fastapi.templating import Jinja2Templates

from backend.app.utils.formatters import formatar_preco_sem_simbolo

templates = Jinja2Templates(directory="app/templates")  # ou "app/templates" se estiver lá

# Filtros personalizados
def moeda_br(valor):
    if valor is None:
        valor = 0
    return f"{valor:,.2f}".replace('.', ',')

def url_for(name: str, **params):
    """Função personalizada para simular url_for do Flask"""
    if name == "static":
        path = params.get("path") or params.get("filename", "")
        return f"/static/{path}"
    elif name == "home":
        return "/"
    elif name == "livros.lista" or name == "livros":
        return "/livros/"  # Com barra no final
    elif name == "livros.detalhes":
        livro_id = params.get("livro_id") or params.get("id", "")
        return f"/livros/{livro_id}"
    elif name == "usuario.perfil" or name == "usuarios.perfil":
        return "/usuarios/perfil"
    elif name == "usuarios.cadastro":
        return "/usuarios/cadastro"
    elif name == "carrinho.ver" or name == "carrinho":
        return "/carrinho/"  # Com barra no final
    elif name == "auth.logout":
        return "/auth/logout"
    elif name == "auth.login":
        return "/auth/login"
    elif name == "auth.cadastro":
        return "/auth/cadastro"
    else:
        return f"/{name.replace('.', '/')}"

templates.env.filters['moeda'] = moeda_br
templates.env.filters["moeda_sem_simbolo"] = formatar_preco_sem_simbolo
templates.env.globals["url_for"] = url_for  # Registra a função