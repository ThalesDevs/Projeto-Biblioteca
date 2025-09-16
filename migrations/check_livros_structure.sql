-- Verificar estrutura exata da tabela livros
SELECT column_name, data_type, is_nullable
FROM information_schema.columns 
WHERE table_schema = 'biblioteca' AND table_name = 'livros'
ORDER BY ordinal_position;
