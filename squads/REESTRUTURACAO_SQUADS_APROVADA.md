# REESTRUTURAÇÃO DOS SQUADS - DECISÃO DO CONSELHO + TRIADE

**Data:** 2026-04-06
**Participantes:** CAIO (CEO), Orion CTO, Chief of Staff (Andy Grove), Jobs, Thiel, Marçal, Hormozi

---

## DIAGNÓSTICO APROVADO

O Conselho analisou o relatório e aprovou a seguinte visão:

### O que está funcionando:
- 17 de 18 squads com config completa
- Dependencies bem mapeadas na maioria
- Estrutura base consistente

### O que precisa corrigir:

| # | Problema | Impacto | Ação |
|---|----------|---------|------|
| 1 | 12 squads com apenas 2 agentes | Squads muito magros, sem liderança clara | Adicionar domain-chief como lead |
| 2 | 6 squads sem workflows | Domínios sem pipeline definido | Adicionar ao menos 1 workflow se aplicável |
| 3 | cangaco-tech-core órfã | Referência quebrada em konig-engineering-core | Remover referência ou criar squad |
| 4 | Inconsistência brandcraft | Formato diferente dos outros | Manter conforme solicitado (já integrado ao branding) |

---

## TEMPLATE PADRÃO APROVADO

O Conselho aprovou o seguinte template mínimo:

```
squad/
├── squad.yaml              # Manifesto (obrigatório)
├── config/
│   ├── coding-standards.md  # Obrigatório
│   ├── tech-stack.md         # Obrigatório
│   └── source-tree.md        # Obrigatório
├── agents/                  # Mínimo 3 (chief, specialist, support)
│   └── {domain}-*.md
├── tasks/                   # Mínimo 3
│   └── {domain}-*.md
├── workflows/               # Se domínio tem pipeline
├── checklists/              # Mínimo 1 gate
│   └── {domain}-gate.md
├── templates/               # Se gera documentos
├── scripts/                 # Se tem automação
└── data/                    # Se tem dados estáticos
```

---

## DECISÕES DO CONSELHO

### Jobs (Produto e Simplicidade):
> "Cada squad deve saber fazer uma coisa excepcional. Se não consegue explicar em 3 frases o que o squad faz, está complexo demais."

**Ação:** Revisar descrição de cada squad para garantir clareza.

### Thiel (Posição e Vantagem):
> "Dependencies devem criar moat, não te fazer refém. Cada squad deve saber exatamente qual valor entrega que os outros não conseguem."

**Ação:** Mapear onde cada squad é insubstituível.

### Marçal (Narrativa e Crescimento):
> "Os squads de crescimento e revenue são os mais importantes. Devem ter mais recursos."

**Ação:** Garantir que konig-growth-core, konig-revenue-core tenham estrutura completa.

### Hormozi (Oferta e Dinheiro):
> "Todo squad precisa saber como contribui para revenue, direta ou indiretamente."

**Ação:** Adicionar em cada squad a pergunta "Como isso faz dinheiro?"

### Andy Grove (Execução):
> "Sem cadência, não há entrega. Todo squad precisa de checklist e gate claro."

**Ação:** Garantir 1 gate por squad.

---

## PLANO DE EXECUÇÃO

**Fase 1:**Corrigir squads órfãos (konig-engineering-core - remover cangaco-tech-core)

**Fase 2:** Adicionar domain-chief a todos os squads com apenas 2 agentes

**Fase 3:** Garantir pelo menos 1 workflow em cada squad

**Fase 4:** Padronizar descrições e tags

---

**Assinado:**
- CAIO (CEO)
- Orion CTO
- Chief of Staff (Andy Grove)
- Jobs (Product Counsel)
- Thiel (Strategy Counsel)
- Marçal (Growth Counsel)
- Hormozi (Revenue Counsel)

---

*Este documento deve ser seguido por todos os agentes ao criar ou modificar squads.*