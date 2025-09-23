from typing import Optional
from pydantic import BaseModel, Field, validator
from datetime import datetime


class LivroCreate(BaseModel):
    titulo: str = Field(..., min_length=1, max_length=500, description="Título do livro")
    autor: str = Field(..., min_length=1, max_length=300, description="Autor do livro")
    ano: Optional[int] = Field(None, ge=1000, le=2030, description="Ano de publicação")
    preco: float = Field(..., gt=0, description="Preço do livro")
    estoque: int = Field(..., ge=0, description="Quantidade em estoque")
    capa_url: Optional[str] = Field(None, description="URL da imagem da capa")
    isbn: Optional[str] = Field(None, min_length=10, max_length=13, description="ISBN do livro")

    @validator('titulo', 'autor')
    def validate_not_empty(cls, v):
        if v and not v.strip():
            raise ValueError('Campo não pode estar vazio')
        return v.strip() if v else v

    @validator('isbn')
    def validate_isbn(cls, v):
        if v:
            # Remove hífens e espaços do ISBN
            isbn_clean = v.replace('-', '').replace(' ', '')
            if len(isbn_clean) not in [10, 13]:
                raise ValueError('ISBN deve ter 10 ou 13 dígitos')
            if not isbn_clean.isdigit():
                raise ValueError('ISBN deve conter apenas números')
            return isbn_clean
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "titulo": "Dom Casmurro",
                "autor": "Machado de Assis",
                "ano": 1899,
                "preco": 29.90,
                "estoque": 15,
                "capa_url": "https://example.com/capa.jpg",
                "isbn": "9788525406259"
            }
        }


class LivroOut(BaseModel):
    id: int
    titulo: str
    autor: str
    ano: Optional[int]
    preco: float
    estoque: int
    capa_url: Optional[str]
    isbn: Optional[str]
    slug: Optional[str]
    data_criacao: Optional[datetime]
    data_atualizacao: Optional[datetime]

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "titulo": "Dom Casmurro",
                "autor": "Machado de Assis",
                "ano": 1899,
                "preco": 29.90,
                "estoque": 15,
                "capa_url": "https://example.com/capa.jpg",
                "isbn": "9788525406259",
                "slug": "dom-casmurro",
                "data_criacao": "2024-01-15T10:30:00Z",
                "data_atualizacao": "2024-01-15T10:30:00Z"
            }
        }


class LivroUpdate(BaseModel):
    titulo: Optional[str] = Field(None, min_length=1, max_length=500)
    autor: Optional[str] = Field(None, min_length=1, max_length=300)
    ano: Optional[int] = Field(None, ge=1000, le=2030)
    preco: Optional[float] = Field(None, gt=0)
    estoque: Optional[int] = Field(None, ge=0)
    capa_url: Optional[str] = Field(None)
    isbn: Optional[str] = Field(None, min_length=10, max_length=13)
    slug: Optional[str] = None  # Gerado automaticamente

    @validator('titulo', 'autor')
    def validate_not_empty(cls, v):
        if v is not None and not v.strip():
            raise ValueError('Campo não pode estar vazio')
        return v.strip() if v else v

    @validator('isbn')
    def validate_isbn(cls, v):
        if v:
            isbn_clean = v.replace('-', '').replace(' ', '')
            if len(isbn_clean) not in [10, 13]:
                raise ValueError('ISBN deve ter 10 ou 13 dígitos')
            if not isbn_clean.isdigit():
                raise ValueError('ISBN deve conter apenas números')
            return isbn_clean
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "titulo": "Dom Casmurro - Edição Revisada",
                "preco": 32.90,
                "estoque": 20
            }
        }


class LivroFiltros(BaseModel):
    """Schema para filtros de busca"""
    titulo: Optional[str] = None
    autor: Optional[str] = None
    ano: Optional[int] = None
    preco_min: Optional[float] = Field(None, ge=0)
    preco_max: Optional[float] = Field(None, ge=0)
    estoque_min: Optional[int] = Field(None, ge=0)
    estoque_max: Optional[int] = Field(None, ge=0)
    termo: Optional[str] = Field(None, min_length=2, description="Busca geral por título ou autor")

    class Config:
        json_schema_extra = {
            "example": {
                "autor": "Machado de Assis",
                "preco_max": 50.0,
                "estoque_min": 1
            }
        }


class LivroPaginacao(BaseModel):
    """Schema para resposta paginada"""
    livros: list[LivroOut]
    total: int
    skip: int
    limite: int
    tem_proximo: bool

    class Config:
        json_schema_extra = {
            "example": {
                "livros": [],
                "total": 150,
                "skip": 0,
                "limite": 10,
                "tem_proximo": True
            }
        }


class LivroEstatisticas(BaseModel):
    """Schema para estatísticas"""
    total_livros: int
    livros_com_estoque: int
    livros_sem_estoque: int
    preco_medio: Optional[float]
    autor_com_mais_livros: Optional[str]

    class Config:
        json_schema_extra = {
            "example": {
                "total_livros": 150,
                "livros_com_estoque": 120,
                "livros_sem_estoque": 30,
                "preco_medio": 45.67,
                "autor_com_mais_livros": "Machado de Assis"
            }
        }