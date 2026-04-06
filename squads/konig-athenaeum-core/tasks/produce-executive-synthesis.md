---
task: Produce Executive Synthesis
responsavel: "@report-synthesizer"
responsavel_type: agent
atomic_layer: task
Entrada: |
  - strategic_brief: framed challenge
  - strategic_narrative: final narrative
  - preferred_path: recommended path
Saida: |
  - executive_brief: concise final report
  - decision_packet: recommendation, risks and next moves
Checklist:
  - "[ ] Keep it readable by executives"
  - "[ ] Put recommendation and risks upfront"
  - "[ ] Distinguish action now vs later"
---

# *produce-executive-synthesis

Produz sintese executiva final para decisao.
