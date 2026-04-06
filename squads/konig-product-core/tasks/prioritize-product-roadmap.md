---
task: Prioritize Product Roadmap
responsavel: "@value-designer"
responsavel_type: agent
atomic_layer: task
Entrada: |
  - product_spec: approved scope
  - delivery_constraints: team capacity and timeline
Saida: |
  - prioritized_roadmap: ordered slices by impact and risk
  - tradeoff_log: what was deferred and why
Checklist:
  - "[ ] Prioritize by impact, risk and feasibility"
  - "[ ] Keep first slices small and shippable"
  - "[ ] Make tradeoffs explicit"
---

# *prioritize-product-roadmap

Organiza o roadmap para acelerar valor e reduzir risco cedo.
