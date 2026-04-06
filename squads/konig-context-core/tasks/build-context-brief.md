---
task: Build Context Brief
responsavel: "@domain-translator"
responsavel_type: agent
atomic_layer: task
Entrada: |
  - ceo_input: short raw request
  - context_snapshot: synced context
Saida: |
  - context_brief: clear brief for planning or execution
  - unknowns: what still needs confirmation
Checklist:
  - "[ ] Convert short input into a stronger brief"
  - "[ ] Remove ambiguity and fluff"
  - "[ ] Keep unknowns explicit"
---

# *build-context-brief

Traduz input curto em brief utilizável.
