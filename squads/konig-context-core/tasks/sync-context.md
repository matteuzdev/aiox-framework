---
task: Sync Context
responsavel: "@context-master"
responsavel_type: agent
atomic_layer: task
Entrada: |
  - source_artifacts: relevant docs, chats or project files
  - current_focus: what matters now
Saida: |
  - context_snapshot: short state of the company or project
  - critical_constraints: what cannot be missed
Checklist:
  - "[ ] Read only the highest-signal sources first"
  - "[ ] Remove stale or irrelevant context"
  - "[ ] Produce a short snapshot"
---

# *sync-context

Mantém a memória operacional viva e usável.
