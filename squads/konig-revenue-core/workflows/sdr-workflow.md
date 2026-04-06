---
workflow: SDR Workflow
description: "Fluxo completo do SDR Agent: da prospecção ao fechamento"
trigger: "Novo lead no CRM ou via prospecção automatica"
owner: "@sdr-agent"
---

# SDR Workflow

## Fluxo Principal

```
[Prospecção] → [Novo Lead no CRM] → [Qualificação BANT] → [Score]
      ↓
[Score = Quente] → [Outreach Imediato] → [Agendar Demo] → [Proposta]
[Score = Morno]  → [Nurturing Sequence] → [Re-qualificar em 7 dias]
[Score = Frio]   → [Email Marketing]    → [Re-qualificar em 30 dias]
```

## Etapas Detalhadas

### 1. Entrada do Lead
- **Fonte**: Prospecção automatica, Website, LinkedIn, Indicação
- **Ação**: Criar lead no CRM com dados completos
- **Responsavel**: Prospecting Agent ou formulario

### 2. Qualificação BANT (Automática)
- **Agente**: @sdr-agent
- **Task**: qualify-lead.md
- **Criterios**:
  - Budget: Tem orçamento? Qual faixa?
  - Authority: E decisor ou influenciador?
  - Need: Qual a dor? Quao critica?
  - Timing: Quando precisa da solução?

### 3. Score e Roteamento
- **Quente**: Outreach imediato (até 5 min)
- **Morno**: Sequencia de nurturing (3 toques em 14 dias)
- **Frio**: Email marketing mensal

### 4. Outreach Humanizado
- **Agente**: @sdr-agent
- **Regras**:
  - Usar primeiro nome
  - Personalizar com contexto da empresa
  - Pergunta aberta no final
  - Maximo 150 palavras
  - Tom: NORMAL (conversacional)

### 5. Follow-up Inteligente
- **Sem resposta em 48h**: Follow-up com valor agregado
- **Sem resposta em 7 dias**: Ultimo toque casual
- **Sem resposta em 14 dias**: Voltar para nurturing

### 6. Atualização do Pipeline
- **Task**: update-crm-pipeline.md
- **Regras**:
  - Registrar cada interação
  - Atualizar etapa automaticamente
  - Criar atividades de follow-up

### 7. Relatório Semanal
- **Task**: generate-sales-report.md
- **Metricas**:
  - Novos leads por fonte
  - Taxa de conversão por etapa
  - Tempo medio por etapa
  - Valor em pipeline
  - Insights e recomendações

## SLAs

| Etapa | Tempo Maximo |
|-------|-------------|
| Qualificação | 1 hora após entrada |
| Primeiro contato (Quente) | 5 minutos |
| Primeiro contato (Morno) | 24 horas |
| Follow-up | 48 horas |
| Re-qualificação (Frio) | 30 dias |

## Integrações

- **CRM**: Notion (leads, deals, atividades)
- **Prospecção**: Google Maps, LinkedIn
- **Comunicação**: Email, WhatsApp (futuro)
- **Analytics**: Relatorios automaticos
