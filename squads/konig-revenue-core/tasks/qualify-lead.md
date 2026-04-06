---
task: Qualify Lead
responsavel: "@sdr-agent"
responsavel_type: agent
atomic_layer: task
Entrada: |
  - lead_name: nome do contato
  - lead_email: email do contato
  - lead_company: empresa do lead
  - lead_source: fonte do lead (Website, LinkedIn, Indicacao, etc)
  - initial_message: primeira mensagem ou contexto do lead
Saida: |
  - lead_score: Quente, Morno ou Frio
  - qualification_notes: notas da qualificacao
  - next_step: proximo passo recomendado
  - crm_updated: true/false
Checklist:
  - "[ ] Analisar fit do lead com ICP"
  - "[ ] Avaliar nivel de interesse"
  - "[ ] Identificar dor principal"
  - "[ ] Definir score (Quente/Morno/Frio)"
  - "[ ] Criar no CRM com dados completos"
  - "[ ] Definir proximo passo"
---

# *qualify-lead

Qualifica um novo lead usando criterios de BANT (Budget, Authority, Need, Timing).

## Criterios de Qualificacao

### Budget
- Tem orcamento definido?
- Faixa de investimento esperada?
- Urgencia financeira?

### Authority
- E o decisor ou influenciador?
- Precisa envolver outras pessoas?
- Hierarquia na empresa?

### Need
- Qual dor o lead tem?
- Quao critica e a dor?
- Ja tentou resolver antes?

### Timing
- Quando precisa da solucao?
- Existe deadline?
- Qual urgencia real?

## Score automatico

### Quente (Hot)
- Budget definido + Authority + Need claro + Timing < 30 dias

### Morno (Warm)
- 2-3 criterios atendidos + Timing < 90 dias

### Frio (Cold)
- 0-1 criterios atendidos + Timing > 90 dias ou indefinido
