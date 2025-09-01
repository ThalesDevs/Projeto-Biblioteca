from datetime import datetime
from sqlalchemy.orm import Session
from typing import List, Optional
import re

from app.domain.models.Livro.livro import Livro
from app.repositories.livro_repository import LivroRepository
from app.domain.schemas.cria_livro import LivroCreate, LivroUpdate
from fastapi import HTTPException, status


class LivroService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = LivroRepository(db)

    # ---------------------- LISTAR ----------------------
    def listar_livros(
            self,
            autor: Optional[str] = None,
            titulo: Optional[str] = None,
            ano: Optional[int] = None,
            preco_min: Optional[float] = None,
            preco_max: Optional[float] = None,
            estoque_min: Optional[int] = None,
            estoque_max: Optional[int] = None,
            skip: int = 0,
            limite: int = 100
    ) -> List[Livro]:
        """Lista livros com filtros opcionais"""
        if any([autor, titulo, ano, preco_min, preco_max, estoque_min, estoque_max]):
            return self.repo.buscar_com_filtros(
                autor=autor,
                titulo=titulo,
                ano=ano,
                preco_min=preco_min,
                preco_max=preco_max,
                estoque_min=estoque_min,
                estoque_max=estoque_max,
                skip=skip,
                limite=limite
            )
        else:
            # Lista todos com paginação
            query = self.db.query(Livro)
            return query.offset(skip).limit(limite).all()

    # ---------------------- OBTER ----------------------
    def obter_livro(self, livro_id: int) -> Livro:
        """Busca livro por ID - CORRIGIDO"""
        if not isinstance(livro_id, int) or livro_id <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="ID do livro deve ser um número inteiro positivo"
            )

        livro = self.repo.buscar_por_id(livro_id)
        if not livro:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Livro com ID {livro_id} não encontrado"
            )
        return livro

    def obter_livro_por_slug(self, slug: str) -> Livro:
        """Busca livro por slug"""
        if not slug or not slug.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Slug não pode estar vazio"
            )

        livro = self.repo.buscar_por_slug(slug.strip())
        if not livro:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Livro com slug '{slug}' não encontrado"
            )
        return livro

    # ---------------------- ADICIONAR ----------------------
    def adicionar_livro(self, livro: LivroCreate) -> Livro:
        """Adiciona um novo livro"""
        self.validar_livro(livro)

        # Gera slug único
        slug = self.gerar_slug(livro.titulo)
        contador = 1
        slug_original = slug

        while self.repo.buscar_por_slug(slug):
            slug = f"{slug_original}-{contador}"
            contador += 1

        return self.repo.adicionar(livro, slug)

    # ---------------------- ATUALIZAR ----------------------
    def atualizar_livro(self, livro_id: int, dados_atualizacao: LivroUpdate) -> Livro:
        """Atualiza livro existente - CORRIGIDO"""
        # Validar ID
        if not isinstance(livro_id, int) or livro_id <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="ID do livro deve ser um número inteiro positivo"
            )

        # Verificar se livro existe
        livro_existente = self.repo.buscar_por_id(livro_id)
        if not livro_existente:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Livro com ID {livro_id} não encontrado"
            )

        # Validar dados se houver campos obrigatórios sendo atualizados
        update_data = dados_atualizacao.model_dump(exclude_unset=True)

        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Nenhum campo para atualizar foi fornecido"
            )

        # Validações específicas para campos atualizados
        if 'titulo' in update_data and (not update_data['titulo'] or not update_data['titulo'].strip()):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Título não pode estar vazio"
            )

        if 'autor' in update_data and (not update_data['autor'] or not update_data['autor'].strip()):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Autor não pode estar vazio"
            )

        if 'preco' in update_data and update_data['preco'] <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Preço deve ser maior que zero"
            )

        if 'estoque' in update_data and update_data['estoque'] < 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Estoque não pode ser negativo"
            )

        if 'ano' in update_data and update_data['ano'] and (update_data['ano'] < 1000 or update_data['ano'] > 2030):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ano deve estar entre 1000 e 2030"
            )

        # Se o título foi alterado, gerar novo slug
        if 'titulo' in update_data:
            novo_slug = self.gerar_slug(update_data['titulo'])
            contador = 1
            slug_original = novo_slug

            # Garantir que o slug é único (exceto para o próprio livro)
            while True:
                livro_com_slug = self.repo.buscar_por_slug(novo_slug)
                if not livro_com_slug or livro_com_slug.id == livro_id:
                    break
                novo_slug = f"{slug_original}-{contador}"
                contador += 1

            dados_atualizacao.slug = novo_slug

        # Atualizar usando o repositório
        livro_atualizado = self.repo.atualizar(livro_id, dados_atualizacao)

        if not livro_atualizado:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro interno ao atualizar o livro"
            )

        return livro_atualizado

    # ---------------------- DELETAR ----------------------
    def deletar_livro(self, livro_id: int) -> bool:
        """Deleta um livro - CORRIGIDO"""
        if not isinstance(livro_id, int) or livro_id <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="ID do livro deve ser um número inteiro positivo"
            )

        livro = self.repo.buscar_por_id(livro_id)
        if not livro:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Livro com ID {livro_id} não encontrado"
            )

        resultado = self.repo.deletar(livro_id)
        return resultado is not None

    # ---------------------- BUSCAR ----------------------
    def buscar_livros(
            self,
            termo: str = None,
            autor: str = None,
            titulo: str = None,
            ano: int = None,
            skip: int = 0,
            limite: int = 100
    ) -> List[Livro]:
        """Busca livros por termo geral ou filtros específicos"""
        if termo:
            # Busca geral por título ou autor
            query = self.db.query(Livro)
            query = query.filter(
                (Livro.titulo.ilike(f"%{termo}%")) |
                (Livro.autor.ilike(f"%{termo}%"))
            )
            return query.offset(skip).limit(limite).all()
        else:
            return self.listar_livros(
                autor=autor,
                titulo=titulo,
                ano=ano,
                skip=skip,
                limite=limite
            )

    # ---------------------- AUXILIARES ----------------------
    def validar_livro(self, livro: LivroCreate):
        """Validações para criação de livro"""
        if not livro.titulo or not livro.titulo.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Título é obrigatório"
            )

        if not livro.autor or not livro.autor.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Autor é obrigatório"
            )

        if livro.preco <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Preço deve ser maior que zero"
            )

        if livro.estoque < 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Estoque não pode ser negativo"
            )

        if livro.ano and (livro.ano < 1000 or livro.ano > 2030):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ano deve estar entre 1000 e 2030"
            )

    @staticmethod
    def gerar_slug(titulo: str) -> str:
        """Gera slug a partir do título - MELHORADO"""
        if not titulo:
            return ""

        # Converter para minúsculas
        slug = titulo.lower()

        # Remover acentos e caracteres especiais
        slug = re.sub(r'[àáâãäå]', 'a', slug)
        slug = re.sub(r'[èéêë]', 'e', slug)
        slug = re.sub(r'[ìíîï]', 'i', slug)
        slug = re.sub(r'[òóôõö]', 'o', slug)
        slug = re.sub(r'[ùúûü]', 'u', slug)
        slug = re.sub(r'[ç]', 'c', slug)
        slug = re.sub(r'[ñ]', 'n', slug)

        # Manter apenas letras, números e espaços
        slug = re.sub(r'[^a-z0-9\s]', '', slug)

        # Substituir espaços por hífens
        slug = re.sub(r'\s+', '-', slug.strip())

        # Remover hífens duplicados
        slug = re.sub(r'-+', '-', slug)

        # Remover hífens do início e fim
        slug = slug.strip('-')

        return slug or "livro-sem-titulo"

    def obter_estatisticas(self) -> dict:
        """Retorna estatísticas dos livros"""
        total_livros = self.repo.contar_total()
        livros_sem_estoque = self.db.query(Livro).filter(Livro.estoque == 0).count()

        return {
            "total_livros": total_livros,
            "livros_sem_estoque": livros_sem_estoque,
            "livros_com_estoque": total_livros - livros_sem_estoque
        }