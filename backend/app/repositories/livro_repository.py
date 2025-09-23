from sqlalchemy.orm import Session
from backend.app.domain.models.Livro.livro import Livro
from backend.app.domain.schemas.cria_livro import LivroCreate, LivroUpdate
from backend.app.utils.atualizar_capas_pg import buscar_url_capa


class LivroRepository:
    def __init__(self, db: Session):
        self.db = db

    def listar(self):
        return self.db.query(Livro).all()

    def buscar_por_id(self, livro_id: int):
        return self.db.query(Livro).filter(Livro.id == livro_id).first()

    def adicionar(self, livro_data: LivroCreate, slug: str = None):
        try:
            livro_dict = livro_data.model_dump()
        except AttributeError:
            livro_dict = livro_data.dict()

        if slug:
            livro_dict['slug'] = slug


        if not livro_dict.get('capa_url'):
            url_capa = buscar_url_capa(livro_dict['titulo'], livro_dict['autor'])
            if url_capa:
                livro_dict['capa_url'] = url_capa

        livro = Livro(**livro_dict)
        self.db.add(livro)
        self.db.commit()
        self.db.refresh(livro)
        return livro

    def atualizar(self, livro_id: int, dados: LivroUpdate):
        livro = self.buscar_por_id(livro_id)

        if livro:
            try:
                dados_dict = dados.model_dump(exclude_unset=True)
            except AttributeError:
                dados_dict = dados.dict(exclude_unset=True)

            # Só atualiza campos que não são None/vazios
            for key, value in dados_dict.items():
                if value is not None:
                    setattr(livro, key, value)

            self.db.commit()
            self.db.refresh(livro)

        return livro

    def deletar(self, livro_id: int):
        """Método corrigido para deletar livro"""
        livro = self.buscar_por_id(livro_id)
        if livro:
            self.db.delete(livro)
            self.db.commit()
            return livro
        return None

    def buscar_por_slug(self, slug: str):
        return self.db.query(Livro).filter(Livro.slug == slug).first()

    def buscar_com_filtros(self,
                           autor: str = None,
                           titulo: str = None,
                           ano: int = None,
                           preco_min: float = None,
                           preco_max: float = None,
                           estoque_min: int = None,
                           estoque_max: int = None,
                           skip: int = 0,
                           limite: int = 100):
        """Método específico para buscas com filtros"""
        query = self.db.query(Livro)

        if autor:
            query = query.filter(Livro.autor.ilike(f"%{autor}%"))
        if titulo:
            query = query.filter(Livro.titulo.ilike(f"%{titulo}%"))
        if ano:
            query = query.filter(Livro.ano == ano)
        if preco_min is not None:
            query = query.filter(Livro.preco >= preco_min)
        if preco_max is not None:
            query = query.filter(Livro.preco <= preco_max)
        if estoque_min is not None:
            query = query.filter(Livro.estoque >= estoque_min)
        if estoque_max is not None:
            query = query.filter(Livro.estoque <= estoque_max)

        return query.offset(skip).limit(limite).all()

    def contar_total(self):
        """Conta o total de livros"""
        return self.db.query(Livro).count()