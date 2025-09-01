
-- Adicionar coluna is_admin (PostgreSQL)
ALTER TABLE biblioteca.usuarios ADD COLUMN IF NOT EXISTS is_admin BOOLEAN NOT NULL DEFAULT FALSE;

-- Tornar um usuário admin (altere o email conforme necessário):
UPDATE biblioteca.usuarios SET is_admin = TRUE WHERE email = 'admin@exemplo.com';
