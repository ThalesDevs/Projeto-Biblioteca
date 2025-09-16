-- Script de Rollback - Execute apenas se precisar desfazer as mudanças
-- CUIDADO: Este script pode causar perda de dados!

-- 1. REMOVER TRIGGERS
DROP TRIGGER IF EXISTS update_pedidos_updated_at ON biblioteca.pedidos;
DROP TRIGGER IF EXISTS update_itens_pedido_updated_at ON biblioteca.itens_pedido;
DROP TRIGGER IF EXISTS update_itens_carrinho_updated_at ON biblioteca.itens_carrinho;
DROP TRIGGER IF EXISTS update_livros_updated_at ON biblioteca.livros;

-- 2. REMOVER FUNÇÃO DE UPDATE
DROP FUNCTION IF EXISTS biblioteca.update_updated_at_column();

-- 3. REMOVER VIEW
DROP VIEW IF EXISTS biblioteca.v_pedidos_completos;

-- 4. REMOVER FUNÇÃO DE CÁLCULO
DROP FUNCTION IF EXISTS biblioteca.calcular_total_pedido(INTEGER);

-- 5. REMOVER ÍNDICES
DROP INDEX IF EXISTS biblioteca.idx_pedidos_usuario_id;
DROP INDEX IF EXISTS biblioteca.idx_pedidos_status;
DROP INDEX IF EXISTS biblioteca.idx_pedidos_created_at;
DROP INDEX IF EXISTS biblioteca.idx_itens_pedido_pedido_id;
DROP INDEX IF EXISTS biblioteca.idx_itens_pedido_livro_id;
DROP INDEX IF EXISTS biblioteca.idx_itens_carrinho_usuario_id;
DROP INDEX IF EXISTS biblioteca.idx_itens_carrinho_livro_id;
DROP INDEX IF EXISTS biblioteca.idx_livros_titulo;
DROP INDEX IF EXISTS biblioteca.idx_livros_autor;

-- 6. REMOVER CONSTRAINTS
ALTER TABLE biblioteca.pedidos DROP CONSTRAINT IF EXISTS chk_status_valido;
ALTER TABLE biblioteca.livros DROP CONSTRAINT IF EXISTS chk_preco_positivo;
ALTER TABLE biblioteca.livros DROP CONSTRAINT IF EXISTS chk_estoque_nao_negativo;
ALTER TABLE biblioteca.itens_carrinho DROP CONSTRAINT IF EXISTS chk_quantidade_positiva;

-- 7. RESTAURAR CAMPO TOTAL (SE NECESSÁRIO)
ALTER TABLE biblioteca.pedidos ADD COLUMN IF NOT EXISTS total DECIMAL(10,2) DEFAULT 0.0;

-- 8. REMOVER TIMESTAMPS (CUIDADO: PERDA DE DADOS)
-- ALTER TABLE biblioteca.pedidos DROP COLUMN IF EXISTS created_at;
-- ALTER TABLE biblioteca.pedidos DROP COLUMN IF EXISTS updated_at;
-- ALTER TABLE biblioteca.itens_carrinho DROP COLUMN IF EXISTS created_at;
-- ALTER TABLE biblioteca.itens_carrinho DROP COLUMN IF EXISTS updated_at;
-- ALTER TABLE biblioteca.livros DROP COLUMN IF EXISTS created_at;
-- ALTER TABLE biblioteca.livros DROP COLUMN IF EXISTS updated_at;

-- 9. REMOVER TABELA ITENS_PEDIDO (CUIDADO: PERDA DE DADOS)
-- DROP TABLE IF EXISTS biblioteca.itens_pedido;
