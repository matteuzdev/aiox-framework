---
task: Update CRM Pipeline
responsavel: "@sdr-agent"
responsavel_type: agent
atomic_layer: task
Entrada: |
  - lead_id: ID do lead no CRM
  - new_stage: nova etapa do pipeline
  - interaction_notes: notas da interacao
  - next_action: proxima acao necessaria
Saida: |
  - crm_updated: true/false
  - stage_history: historico de mudancas
  - follow_up_date: data do proximo follow-up
Checklist:
  - "[ ] Atualizar etapa do lead no CRM"
  - "[ ] Registrar notas da interacao"
  - "[ ] Agendar proximo follow-up"
  - "[ ] Criar atividade se necessario"
---

# *update-crm-pipeline

Atualiza o pipeline do CRM conforme o lead progride no funil.

## Etapas do Pipeline

1. **Prospeccao** - Lead identificado, primeiro contato pendente
2. **Qualificacao** - Em dialogo, avaliando fit e interesse
3. **Proposta** - Lead qualificado, proposta enviada
4. **Negociacao** - Discutindo termos, objecoes
5. **Fechamento** - Deal fechado (ganho ou perdido)

## Regras de Progressao

- So avanca uma etapa por vez
- Cada etapa requer pelo menos 1 interacao registrada
- Follow-up automatico se sem resposta em 48h
- Lead sem resposta em 7 dias volta para Qualificacao
