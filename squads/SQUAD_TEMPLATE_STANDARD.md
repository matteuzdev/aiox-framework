# SQUAD TEMPLATE PADRÃO - KONIG SYSTEMS

## Estrutura Mínima Viable por Squad

### Componentes Obrigatórios:
- `squad.yaml` - Manifesto com versão, descrição, author, license
- `config/` - coding-standards, tech-stack, source-tree
- `agents/` - Mínimo 3 agentes (Lead + Specialist + Support)
- `tasks/` - Mínimo 3 tarefas específicas do domínio
- `checklists/` - Pelo menos 1 gate de validação

### Componentos Opcionais:
- `workflows/` - Se o domínio precisa de pipeline
- `templates/` - Se o domínio gera documentos
- `scripts/` - Se o domínio tem automação
- `data/` - Se o domínio tem dados estáticos

### Dependencies:
- Todo squad deve listar suas dependências explicitamente
- Dependencies devem ser bidirecionais onde faz sentido

---

## Padrão de Agents por Squad

Todo squad deve ter:

```yaml
agents:
  - {domain}-chief.md        # Lead do domínio
  - {domain}-specialist.md  # Executor especializado
  - {domain}-support.md     # Suporte/analista
```

**Exceções:**
- Squads estratégicos podem ter mais (até 5-7)
- Squads operacionais podem ter 2 se bem justificado

---

## Padrão de Tasks por Squad

```yaml
tasks:
  - {domain}-analyze.md     # Análise do domínio
  - {domain}-execute.md     # Execução principal
  - {domain}-report.md      # Relatório/交付
```

---

## Checklist Obrigatória

Todo squad deve ter pelo menos:
```yaml
checklists:
  - {domain}-gate.md        # Gate de validação
```

---

## Tags Padrão

Todo squad deve ter tags claras:
- Domínio principal (revenue, product, growth, etc)
- Tipo (core, support, factory)
- Área (strategy, execution, intelligence)