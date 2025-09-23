from pydantic import BaseModel, Field, EmailStr

class UsuarioCreate(BaseModel):
    nome: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    senha: str = Field(..., min_length=6)

class UsuarioOut(BaseModel):
    id: int
    nome: str
    email: str

    class Config:
        from_attributes = True

class LoginInput(BaseModel):
    email: EmailStr
    senha: str