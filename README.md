# 📚 Projeto Biblioteca

[![Python](https://img.shields.io/badge/Python-3.11-blue)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100-green)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-Free-orange)](#)

Bem-vindo ao **Projeto Biblioteca**, um sistema completo de gerenciamento de biblioteca com:

- Cadastro de usuários  
- Gestão de livros  
- Carrinho de compras  
- Pedidos  
- Autenticação e perfil de usuários  

O backend é desenvolvido com **FastAPI** e renderização de páginas via **Jinja2**, com possibilidade de frontend separado futuramente.

---


---

## 🗂 Estrutura do Projeto

Projeto-Biblioteca/
├─ backend/
│ ├─ main.py
│ ├─ api/
│ │ ├─ auth_router.py
│ │ ├─ livro_router.py
│ │ ├─ carrinho_router.py
│ │ ├─ usuario_router.py
│ │ └─ pedido_router.py
│ ├─ templates/
│ │ └─ index.html
│ └─ static/
├─ frontend/ (Angular/React futuro)
├─ assets/ (imagens e GIFs)
├─ README.md
├─ .gitignore
└─ .env (não versionado)


---

## 💻 Tecnologias

- Python 3.11+  
- FastAPI  
- Jinja2  
- SQLAlchemy  
- PostgreSQL  
- Git/GitHub  

---

## 🔧 Instalação e Execução

```bash
git clone git@github.com:ThalesDevs/Projeto-Biblioteca.git
cd Projeto-Biblioteca/backend

python -m venv venv
source venv/Scripts/activate  # Windows
pip install -r requirements.txt

uvicorn main:app --reload