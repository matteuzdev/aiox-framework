---
task: Stabilize Operations
responsavel: "@ops-chief"
responsavel_type: agent
atomic_layer: task
Entrada: |
  - current_operation_state: bottlenecks, incidents and queue
  - delivery_plan: active execution priorities
Saida: |
  - stabilization_plan: immediate actions and owners
  - risk_watchlist: operational risks to monitor
Checklist:
  - "[ ] Identify highest operational risks"
  - "[ ] Define owners and deadlines"
  - "[ ] Confirm short feedback loop for corrections"
---

# *stabilize-operations

Restaura ordem operacional para manter entrega previsivel.
