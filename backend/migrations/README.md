# Migrações do Banco de Dados

## Como Executar as Correções

### 1. Backup do Banco Atual
```bash
# Fazer backup antes de executar as migrações
pg_dump -h localhost -p 5433 -U biblioteca -d biblioteca > backup_antes_migracao.sql
```

### 2. Executar Migração Principal
```bash
# Conectar ao PostgreSQL e executar
psql -h localhost -p 5433 -U biblioteca -d biblioteca -f fix_database_structure.sql
```

### 3. Verificar Execução
```sql
-- Verificar se tabela foi criada
SELECT * FROM information_schema.tables WHERE table_name = 'itens_pedido';

-- Verificar constraints
SELECT constraint_name, constraint_type 
FROM information_schema.table_constraints 
WHERE table_schema = 'biblioteca';

-- Verificar índices
SELECT indexname FROM pg_indexes WHERE schemaname = 'biblioteca';
```

### 4. Atualizar Código Python
- Aplicar as mudanças nos models propostos
- Importar o novo model `ItemPedido` onde necessário
- Atualizar imports para usar os enums

### 5. Rollback (Se Necessário)
```bash
# Apenas se algo der errado
psql -h localhost -p 5433 -U biblioteca -d biblioteca -f rollback_database_structure.sql
```

## Principais Mudanças

✅ **Tabela `itens_pedido` criada** - relaciona pedidos com livros  
✅ **Timestamps adicionados** - `created_at` e `updated_at` em todas as tabelas  
✅ **Campo `total` removido** - será calculado dinamicamente  
✅ **Constraints de validação** - preços positivos, quantidades válidas  
✅ **Índices para performance** - consultas mais rápidas  
✅ **Triggers automáticos** - `updated_at` atualizado automaticamente  
✅ **View com total calculado** - `v_pedidos_completos`  
✅ **Enum para status** - valores padronizados  

## Impacto no Código

- **Models atualizados** com timestamps e relacionamentos corretos
- **Repositories precisarão** usar `ItemPedido` ao invés de lógica duplicada
- **Services de pedido** devem usar propriedade `total` calculada
- **Status de pedidos** agora usa enum tipado

## Benefícios

🚀 **Performance melhorada** com índices otimizados  
🔒 **Integridade garantida** com constraints e FKs  
📊 **Dados consistentes** com triggers automáticos  
🎯 **Código mais limpo** com enums e relacionamentos corretos
