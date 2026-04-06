---
task: Commission Market Research
responsavel: "@chief-of-staff"
responsavel_type: agent
atomic_layer: task
Entrada: |
  - decision_frame: clarified strategic question
  - niche: target niche or market
  - context_brief: brief from context layer
Saida: |
  - research_request: explicit research scope for research-intel
  - council_input_pack: material expected back before debate
Checklist:
  - "[ ] Decide if the council needs market research first"
  - "[ ] Frame what the research must prove or disprove"
  - "[ ] Route niche, ICP and opportunity questions to research-intel"
  - "[ ] Wait for a decision-grade return, not raw browsing noise"
---

# *commission-market-research

Task de ponte entre `clarify-direction` e o debate do conselho.
