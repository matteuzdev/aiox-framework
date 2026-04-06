---
task: Drive Delivery Slices
responsavel: "@engineering-chief"
responsavel_type: agent
atomic_layer: task
Entrada: |
  - technical_plan: approved architecture direction
  - prioritized_roadmap: delivery order
Saida: |
  - shipped_slices: increments with verification
  - delivery_report: what shipped, risks and next step
Checklist:
  - "[ ] Deliver one slice at a time with verification"
  - "[ ] Keep rollback path explicit"
  - "[ ] Publish concise delivery report"
---

# *drive-delivery-slices

Executa entregas incrementais para reduzir risco e acelerar aprendizado.
