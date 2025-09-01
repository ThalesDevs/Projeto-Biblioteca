-- Script de Migração Simplificado - SEM VERIFICAÇÃO AUTOMÁTICA
-- Execute este script no PostgreSQL

-- 1. CRIAR TABELA ITENS_PEDIDO
CREATE TABLE IF NOT EXISTS biblioteca.itens_pedido (
    id SERIAL PRIMARY KEY,
    pedido_id INTEGER NOT NULL,
    livro_id INTEGER NOT NULL,
    quantidade INTEGER NOT NULL CHECK (quantidade > 0),
    preco_unitario DECIMAL(10,2) NOT NULL CHECK (preco_unitario > 0),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT fk_itens_pedido_pedido 
        FOREIGN KEY (pedido_id) REFERENCES biblioteca.pedidos(id) ON DELETE CASCADE,
    CONSTRAINT fk_itens_pedido_livro 
        FOREIGN KEY (livro_id) REFERENCES biblioteca.livros(id) ON DELETE RESTRICT
);

-- 2. ADICIONAR TIMESTAMPS
ALTER TABLE biblioteca.pedidos 
ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;

ALTER TABLE biblioteca.itens_carrinho 
ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;

ALTER TABLE biblioteca.livros 
ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;

-- 3. REMOVER CAMPO TOTAL DOS PEDIDOS
ALTER TABLE biblioteca.pedidos DROP COLUMN IF EXISTS total;

-- 4. CONSTRAINTS DE STATUS
ALTER TABLE biblioteca.pedidos 
DROP CONSTRAINT IF EXISTS chk_status_valido;

ALTER TABLE biblioteca.pedidos 
ADD CONSTRAINT chk_status_valido 
CHECK (status IN ('PENDENTE', 'CONFIRMADO', 'ENVIADO', 'ENTREGUE', 'CANCELADO'));

-- 5. CONSTRAINTS DE VALIDAÇÃO
ALTER TABLE biblioteca.livros 
ADD CONSTRAINT IF NOT EXISTS chk_preco_positivo CHECK (preco > 0),
ADD CONSTRAINT IF NOT EXISTS chk_estoque_nao_negativo CHECK (estoque >= 0);

ALTER TABLE biblioteca.itens_carrinho 
ADD CONSTRAINT IF NOT EXISTS chk_quantidade_positiva CHECK (quantidade > 0);

-- 6. ÍNDICES
CREATE INDEX IF NOT EXISTS idx_pedidos_usuario_id ON biblioteca.pedidos(usuario_id);
CREATE INDEX IF NOT EXISTS idx_pedidos_status ON biblioteca.pedidos(status);
CREATE INDEX IF NOT EXISTS idx_itens_pedido_pedido_id ON biblioteca.itens_pedido(pedido_id);
CREATE INDEX IF NOT EXISTS idx_itens_pedido_livro_id ON biblioteca.itens_pedido(livro_id);

-- 7. FUNÇÃO DE UPDATE TIMESTAMP
CREATE OR REPLACE FUNCTION biblioteca.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 8. TRIGGERS
DROP TRIGGER IF EXISTS update_pedidos_updated_at ON biblioteca.pedidos;
CREATE TRIGGER update_pedidos_updated_at 
    BEFORE UPDATE ON biblioteca.pedidos 
    FOR EACH ROW EXECUTE FUNCTION biblioteca.update_updated_at_column();

DROP TRIGGER IF EXISTS update_itens_pedido_updated_at ON biblioteca.itens_pedido;
CREATE TRIGGER update_itens_pedido_updated_at 
    BEFORE UPDATE ON biblioteca.itens_pedido 
    FOR EACH ROW EXECUTE FUNCTION biblioteca.update_updated_at_column();

-- 9. FUNÇÃO PARA CALCULAR TOTAL
CREATE OR REPLACE FUNCTION biblioteca.calcular_total_pedido(pedido_id_param INTEGER)
RETURNS DECIMAL(10,2) AS $$
BEGIN
    RETURN COALESCE(
        (SELECT SUM(quantidade * preco_unitario) 
         FROM biblioteca.itens_pedido 
         WHERE pedido_id = pedido_id_param), 
        0
    );
END;
$$ LANGUAGE plpgsql;

-- 10. VIEW SIMPLES
DROP VIEW IF EXISTS biblioteca.v_pedidos_completos;
CREATE VIEW biblioteca.v_pedidos_completos AS
SELECT 
    p.id,
    p.usuario_id,
    p.status,
    p.created_at,
    p.updated_at,
    biblioteca.calcular_total_pedido(p.id) as total_calculado
FROM biblioteca.pedidos p;

-- COMENTÁRIOS
COMMENT ON TABLE biblioteca.itens_pedido IS 'Itens de cada pedido';
COMMENT ON VIEW biblioteca.v_pedidos_completos IS 'Pedidos com total calculado';
