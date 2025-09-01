# alembic/versions/0001_criacao_inicial.py
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# Revisão Alembic
revision = '0001_criacao_inicial'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # ---------- USUARIOS ----------
    op.create_table(
        'usuarios',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('nome', sa.String(255), nullable=False),
        sa.Column('email', sa.String(255), nullable=False, unique=True),
        sa.Column('senha_hash', sa.String(255), nullable=False),
        sa.Column('telefone', sa.String(20)),
        sa.Column('cpf', sa.String(14)),
        sa.Column('data_nascimento', sa.Date),
        sa.Column('is_active', sa.Boolean, nullable=False, default=True),
        sa.Column('is_admin', sa.Boolean, nullable=False, default=False),
        sa.Column('email_confirmado', sa.Boolean, nullable=False, default=False),
        sa.Column('email_confirmado_em', sa.DateTime),
        sa.Column('ativo', sa.Boolean, nullable=False, default=True),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now())
    )

    # ---------- LIVROS ----------
    op.create_table(
        'livros',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('titulo', sa.String(255), nullable=False),
        sa.Column('autor', sa.String(255), nullable=False),
        sa.Column('isbn', sa.String(20), unique=True),
        sa.Column('capa_url', sa.String(500)),
        sa.Column('preco', sa.Numeric(10,2), nullable=False),
        sa.Column('estoque', sa.Integer, nullable=False, default=0),
        sa.Column('ativo', sa.Boolean, nullable=False, default=True),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now())
    )

    # ---------- ITENS_CARRINHO ----------
    op.create_table(
        'itens_carrinho',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('usuario_id', sa.Integer, sa.ForeignKey('usuarios.id'), nullable=False),
        sa.Column('livro_id', sa.Integer, sa.ForeignKey('livros.id'), nullable=False),
        sa.Column('quantidade', sa.Integer, nullable=False),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now())
    )

    # ---------- CARTOES_CREDITO ----------
    op.create_table(
        'cartoes_credito',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('usuario_id', sa.Integer, sa.ForeignKey('usuarios.id'), nullable=False),
        sa.Column('nome_titular', sa.String(255), nullable=False),
        sa.Column('numero_hash', sa.String(255), nullable=False),
        sa.Column('ultimos_digitos', sa.String(4)),
        sa.Column('bandeira', sa.String(50)),
        sa.Column('mes_vencimento', sa.Integer),
        sa.Column('ano_vencimento', sa.Integer),
        sa.Column('principal', sa.Boolean, nullable=False, default=False),
        sa.Column('ativo', sa.Boolean, nullable=False, default=True),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now())
    )

    # ---------- PEDIDOS ----------
    op.create_table(
        'pedidos',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('usuario_id', sa.Integer, sa.ForeignKey('usuarios.id'), nullable=False),
        sa.Column('cartao_id', sa.Integer, sa.ForeignKey('cartoes_credito.id')),
        sa.Column('total', sa.Numeric(10,2), nullable=False),
        sa.Column('status', sa.String(50), nullable=False),
        sa.Column('data_criacao', sa.DateTime, server_default=sa.func.now()),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now())
    )

    # ---------- ITENS_PEDIDO ----------
    op.create_table(
        'itens_pedido',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('pedido_id', sa.Integer, sa.ForeignKey('pedidos.id'), nullable=False),
        sa.Column('livro_id', sa.Integer, sa.ForeignKey('livros.id'), nullable=False),
        sa.Column('quantidade', sa.Integer, nullable=False),
        sa.Column('preco_unitario', sa.Numeric(10,2), nullable=False),
        sa.Column('subtotal', sa.Numeric(10,2), nullable=False),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now())
    )

    # ---------- CONFIRMACOES_EMAIL ----------
    op.create_table(
        'confirmacoes_email',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('usuario_id', sa.Integer, sa.ForeignKey('usuarios.id'), nullable=False),
        sa.Column('token', sa.String(255), nullable=False, unique=True),
        sa.Column('usado', sa.Boolean, nullable=False, default=False),
        sa.Column('expires_at', sa.DateTime, nullable=False),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now())
    )

    # ---------- ENDERECOS_USUARIOS ----------
    op.create_table(
        'enderecos_usuarios',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('usuario_id', sa.Integer, sa.ForeignKey('usuarios.id'), nullable=False),
        sa.Column('apelido', sa.String(255)),
        sa.Column('logradouro', sa.String(255)),
        sa.Column('numero', sa.String(20)),
        sa.Column('complemento', sa.String(255)),
        sa.Column('bairro', sa.String(100)),
        sa.Column('cidade', sa.String(100)),
        sa.Column('estado', sa.String(50)),
        sa.Column('cep', sa.String(20)),
        sa.Column('pais', sa.String(50)),
        sa.Column('principal', sa.Boolean, nullable=False, default=False),
        sa.Column('ativo', sa.Boolean, nullable=False, default=True),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now())
    )

    # ---------- TRANSACOES_PAGAMENTO ----------
    op.create_table(
        'transacoes_pagamento',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('pedido_id', sa.Integer, sa.ForeignKey('pedidos.id'), nullable=False),
        sa.Column('cartao_id', sa.Integer, sa.ForeignKey('cartoes_credito.id')),
        sa.Column('total', sa.Numeric(10,2), nullable=False),
        sa.Column('status', sa.String(50)),
        sa.Column('mensagem', sa.String(255)),
        sa.Column('data_criacao', sa.DateTime, server_default=sa.func.now()),
        sa.Column('data_atualizacao', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now())
    )

    # ---------- ALEMBIC_VERSION ----------
    op.create_table(
        'alembic_version',
        sa.Column('version_num', sa.String(32), primary_key=True)
    )

def downgrade():
    # Downgrade intencionalmente vazio para não derrubar tabelas importantes
    pass
