---
task: Run Council Debate
responsavel: "@chief-of-staff"
responsavel_type: agent
atomic_layer: task
Entrada: |
  - decision_frame: the question to be debated
  - assumptions: explicit assumptions and constraints
  - target_outcome: what kind of answer the CEO needs
Saida: |
  - council_positions: each counsel's strongest view
  - points_of_agreement: consensus areas
  - tensions: disagreements that matter
  - recommended_bet: best current move
Checklist:
  - "[ ] Collect growth, offer, strategy, product and technical lenses"
  - "[ ] Keep each lens practical and non-theatrical"
  - "[ ] Surface the real tensions"
  - "[ ] Produce a short recommended bet"
  - "[ ] Hand off to CEO decision"
---

# *run-council-debate

Roda o debate do conselho sem transformar a reunião em espetáculo.
