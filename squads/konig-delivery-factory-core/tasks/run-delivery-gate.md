---
task: Run Delivery Gate
responsavel: "@completion-enforcer"
responsavel_type: agent
atomic_layer: task
Entrada: |
  - shippable_output: the claimed final output
  - acceptance_view: what counts as done
Saida: |
  - gate_result: pass, conditional pass or fail
  - failure_reasons: why it is not done if rejected
Checklist:
  - "[ ] Check the artifact exists"
  - "[ ] Check the artifact matches the acceptance view"
  - "[ ] Check there is evidence, not only claims"
  - "[ ] Reject unfinished work clearly"
---

# *run-delivery-gate

Valida se a entrega esta pronta para uso real.
