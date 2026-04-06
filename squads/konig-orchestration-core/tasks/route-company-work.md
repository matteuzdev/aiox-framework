---
task: Route Company Work
responsavel: "@orchestration-chief"
responsavel_type: agent
atomic_layer: task
Entrada: |
  - objective: what must be achieved
  - urgency: timing and constraints
  - current_assets: links to briefs, offers, code, context or prior outputs
Saida: |
  - squad_route: ordered list of squads involved
  - owner_map: single owner for each stage
  - blockage_flags: what can stall execution
Checklist:
  - "[ ] Name the primary owner"
  - "[ ] Define the shortest valid route"
  - "[ ] Remove unnecessary parallel work"
  - "[ ] Escalate missing context before execution"
---

# *route-company-work

Decide o caminho minimo e correto para uma demanda atravessar a Konig Systems.
