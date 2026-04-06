---
task: Force To Done
responsavel: "@delivery-chief"
responsavel_type: agent
atomic_layer: task
Entrada: |
  - delivery_spec: scoped work with acceptance criteria
  - current_state: latest artifacts, blockers and owner notes
Saida: |
  - shippable_output: the finished artifact or package
  - closure_note: what was finished, what remains and what evidence exists
Checklist:
  - "[ ] Confirm definition of done before more execution"
  - "[ ] Resolve blockers or escalate them"
  - "[ ] Produce a usable final artifact"
  - "[ ] Attach evidence that the output is real"
---

# *force-to-done

Puxa uma iniciativa ate existir entrega utilizavel.
