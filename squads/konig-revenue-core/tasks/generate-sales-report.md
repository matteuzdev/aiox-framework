---
task: Generate Sales Report
responsavel: "@sdr-agent"
responsavel_type: agent
atomic_layer: task
Entrada: |
  - period: periodo do relatorio (weekly, monthly)
  - start_date: data inicio
  - end_date: data fim
Saida: |
  - report: relatorio completo em markdown
  - metrics: metricas chave
  - insights: insights e recomendacoes
Checklist:
  - "[ ] Coletar dados do periodo"
  - "[ ] Calcular metricas de conversao"
  - "[ ] Analisar performance por fonte"
  - "[ ] Identificar gargalos no funil"
  - "[ ] Gerar recomendacoes"
---

# *generate-sales-report

Gera relatorio semanal/mensal de performance de vendas.

## Metricas Principais

- Total de novos leads
- Leads qualificados vs desqualificados
- Taxa de conversao por etapa
- Valor total em pipeline
- Deals fechados (ganho/perdido)
- Tempo medio por etapa
- Performance por fonte de lead

## Formato do Relatorio

```markdown
# Sales Report - [Periodo]

## Resumo
- Novos leads: X
- Qualificados: Y (Z%)
- Em negociacao: W
- Fechados: V

## Funil de Conversao
Prospeccao -> Qualificacao: X%
Qualificacao -> Proposta: Y%
Proposta -> Negociacao: Z%
Negociacao -> Fechamento: W%

## Top Fontes
1. Website - X leads
2. LinkedIn - Y leads
3. Indicacao - Z leads

## Insights
- ...

## Recomendacoes
- ...
```
