-- Script de Migração para Correção da Estrutura do Banco
-- Execute este script no PostgreSQL

-- 1. CRIAR TABELA ITENS_PEDIDO (FALTANDO)
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

-- 2. ADICIONAR TIMESTAMPS NAS TABELAS EXISTENTES
ALTER TABLE biblioteca.pedidos 
ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;

ALTER TABLE biblioteca.itens_carrinho 
ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;

ALTER TABLE biblioteca.livros 
ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;

-- 3. REMOVER CAMPO TOTAL DOS PEDIDOS (SERÁ CALCULADO)
ALTER TABLE biblioteca.pedidos DROP COLUMN IF EXISTS total;

-- 4. MELHORAR CAMPO STATUS COM CONSTRAINT
ALTER TABLE biblioteca.pedidos 
DROP CONSTRAINT IF EXISTS chk_status_valido;

ALTER TABLE biblioteca.pedidos 
ADD CONSTRAINT chk_status_valido 
CHECK (status IN ('PENDENTE', 'CONFIRMADO', 'ENVIADO', 'ENTREGUE', 'CANCELADO'));

-- 5. ADICIONAR CONSTRAINTS DE VALIDAÇÃO
ALTER TABLE biblioteca.livros 
ADD CONSTRAINT IF NOT EXISTS chk_preco_positivo CHECK (preco > 0),
ADD CONSTRAINT IF NOT EXISTS chk_estoque_nao_negativo CHECK (estoque >= 0);

ALTER TABLE biblioteca.itens_carrinho 
ADD CONSTRAINT IF NOT EXISTS chk_quantidade_positiva CHECK (quantidade > 0);

-- 6. CRIAR ÍNDICES PARA PERFORMANCE
CREATE INDEX IF NOT EXISTS idx_pedidos_usuario_id ON biblioteca.pedidos(usuario_id);
CREATE INDEX IF NOT EXISTS idx_pedidos_status ON biblioteca.pedidos(status);
CREATE INDEX IF NOT EXISTS idx_pedidos_created_at ON biblioteca.pedidos(created_at);

CREATE INDEX IF NOT EXISTS idx_itens_pedido_pedido_id ON biblioteca.itens_pedido(pedido_id);
CREATE INDEX IF NOT EXISTS idx_itens_pedido_livro_id ON biblioteca.itens_pedido(livro_id);

CREATE INDEX IF NOT EXISTS idx_itens_carrinho_usuario_id ON biblioteca.itens_carrinho(usuario_id);
CREATE INDEX IF NOT EXISTS idx_itens_carrinho_livro_id ON biblioteca.itens_carrinho(livro_id);

CREATE INDEX IF NOT EXISTS idx_livros_titulo ON biblioteca.livros(titulo);
CREATE INDEX IF NOT EXISTS idx_livros_autor ON biblioteca.livros(autor);

-- 7. FUNÇÃO PARA ATUALIZAR UPDATED_AT AUTOMATICAMENTE
CREATE OR REPLACE FUNCTION biblioteca.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 8. TRIGGERS PARA UPDATED_AT
DROP TRIGGER IF EXISTS update_pedidos_updated_at ON biblioteca.pedidos;
CREATE TRIGGER update_pedidos_updated_at 
    BEFORE UPDATE ON biblioteca.pedidos 
    FOR EACH ROW EXECUTE FUNCTION biblioteca.update_updated_at_column();

DROP TRIGGER IF EXISTS update_itens_pedido_updated_at ON biblioteca.itens_pedido;
CREATE TRIGGER update_itens_pedido_updated_at 
    BEFORE UPDATE ON biblioteca.itens_pedido 
    FOR EACH ROW EXECUTE FUNCTION biblioteca.update_updated_at_column();

DROP TRIGGER IF EXISTS update_itens_carrinho_updated_at ON biblioteca.itens_carrinho;
CREATE TRIGGER update_itens_carrinho_updated_at 
    BEFORE UPDATE ON biblioteca.itens_carrinho 
    FOR EACH ROW EXECUTE FUNCTION biblioteca.update_updated_at_column();

DROP TRIGGER IF EXISTS update_livros_updated_at ON biblioteca.livros;
CREATE TRIGGER update_livros_updated_at 
    BEFORE UPDATE ON biblioteca.livros 
    FOR EACH ROW EXECUTE FUNCTION biblioteca.update_updated_at_column();

-- 9. FUNÇÃO PARA CALCULAR TOTAL DO PEDIDO
CREATE OR REPLACE FUNCTION biblioteca.calcular_total_pedido(pedido_id_param INTEGER)
RETURNS DECIMAL(10,2) AS $$
DECLARE
    total_calculado DECIMAL(10,2);
BEGIN
    SELECT COALESCE(SUM(quantidade * preco_unitario), 0)
    INTO total_calculado
    FROM biblioteca.itens_pedido
    WHERE pedido_id = pedido_id_param;
    
    RETURN total_calculado;
END;
$$ LANGUAGE plpgsql;

-- 10. VIEW PARA PEDIDOS COM TOTAL CALCULADO
DROP VIEW IF EXISTS biblioteca.v_pedidos_completos;
CREATE VIEW biblioteca.v_pedidos_completos AS
SELECT 
    p.id,
    p.usuario_id,
    p.status,
    p.created_at,
    p.updated_at,
    COALESCE(biblioteca.calcular_total_pedido(p.id), 0) as total_calculado,
    COALESCE(COUNT(ip.id), 0) as total_itens
FROM biblioteca.pedidos p
LEFT JOIN biblioteca.itens_pedido ip ON p.id = ip.pedido_id
GROUP BY p.id, p.usuario_id, p.status, p.created_at, p.updated_at;

-- 11. COMENTÁRIOS
COMMENT ON TABLE biblioteca.itens_pedido IS 'Tabela para armazenar itens de cada pedido';
COMMENT ON VIEW biblioteca.v_pedidos_completos IS 'View com pedidos e total calculado dinamicamente';

-- 12. VERIFICAÇÃO FINAL
DO $$
BEGIN
    -- Verificar se tabela existe
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'biblioteca' AND table_name = 'itens_pedido') THEN
        RAISE EXCEPTION 'Tabela itens_pedido não foi criada!';
    END IF;
    
    -- Verificar se função existe
    IF NOT EXISTS (SELECT 1 FROM information_schema.routines WHERE routine_schema = 'biblioteca' AND routine_name = 'calcular_total_pedido') THEN
        RAISE EXCEPTION 'Função calcular_total_pedido não foi criada!';
    END IF;
    
    -- Verificar se view existe
    IF NOT EXISTS (SELECT 1 FROM information_schema.views WHERE table_schema = 'biblioteca' AND table_name = 'v_pedidos_completos') THEN
        RAISE EXCEPTION 'View v_pedidos_completos não foi criada!';
    END IF;
    
    RAISE NOTICE 'Migração executada com sucesso! Todas as estruturas foram criadas.';
END $$;
