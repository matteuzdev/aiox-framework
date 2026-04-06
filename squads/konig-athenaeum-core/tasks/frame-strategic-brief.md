---
task: Frame Strategic Brief
responsavel: "@intake-analyst"
responsavel_type: agent
atomic_layer: task
Entrada: |
  - raw_challenge: vague issue or strategic problem
  - known_context: known facts, actors and constraints
Saida: |
  - strategic_brief: framed challenge, objective and decision scope
  - ambiguity_map: what is known, unknown and contested
Checklist:
  - "[ ] Define the real decision behind the problem"
  - "[ ] Separate facts from assumptions"
  - "[ ] Name missing context explicitly"
  - "[ ] Keep the brief usable by the next agents"
---

# *frame-strategic-brief

Transforma um desafio difuso em briefing estrategico utilizavel.
