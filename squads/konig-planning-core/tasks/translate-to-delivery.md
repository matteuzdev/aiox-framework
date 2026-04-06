---
task: Translate to Delivery
responsavel: "@technical-pm"
responsavel_type: agent
atomic_layer: task
Entrada: |
  - planning_packet: approved plan
Saida: |
  - delivery_spec: what design, dev and ops need to do
  - acceptance_view: what counts as done
Checklist:
  - "[ ] Translate plan into execution language"
  - "[ ] Remove hidden assumptions"
  - "[ ] Define what good delivery looks like"
---

# *translate-to-delivery

Entrega o planejamento em uma forma que o time de execução realmente entende.
