---
task: Report Company Health
responsavel: "@health-auditor"
responsavel_type: agent
atomic_layer: task
Entrada: |
  - company_state: current signals from squads and operations
Saida: |
  - health_report: green, yellow and red zones
  - priority_alerts: what needs attention now
Checklist:
  - "[ ] Rate clarity, execution, revenue, delivery and risk"
  - "[ ] Show severity and next step"
  - "[ ] Keep report executive-friendly"
---

# *report-company-health

Relatório estilo monitor de sistema da empresa.
