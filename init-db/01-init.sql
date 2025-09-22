-- Script de inicialização do banco de dados
-- Este arquivo será executado automaticamente pelo PostgreSQL

-- Criar schema biblioteca se não existir
CREATE SCHEMA IF NOT EXISTS biblioteca;

-- Definir schema padrão
SET search_path TO biblioteca, public;

-- Garantir que o usuário tenha permissões
GRANT ALL PRIVILEGES ON SCHEMA biblioteca TO biblioteca;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA biblioteca TO biblioteca;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA biblioteca TO biblioteca;

-- Configurar permissões padrão para objetos futuros
ALTER DEFAULT PRIVILEGES IN SCHEMA biblioteca GRANT ALL ON TABLES TO biblioteca;
ALTER DEFAULT PRIVILEGES IN SCHEMA biblioteca GRANT ALL ON SEQUENCES TO biblioteca;

-- Log de conclusão
SELECT 'Banco inicializado com sucesso!' as status;