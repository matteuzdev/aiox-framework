---
task: Build Execution Contract
responsavel: "@handoff-architect"
responsavel_type: agent
atomic_layer: task
Entrada: |
  - routed_work: approved route through squads
  - current_context: known facts, assumptions and open questions
Saida: |
  - execution_contract: explicit input, output and boundaries for each stage
  - acceptance_map: what each receiving squad must validate
Checklist:
  - "[ ] Define exact input and output per stage"
  - "[ ] Write hidden assumptions explicitly"
  - "[ ] Clarify what blocks handoff approval"
  - "[ ] Keep the contract readable by operators"
---

# *build-execution-contract

Transforma uma rota em contrato operacional entre squads.
