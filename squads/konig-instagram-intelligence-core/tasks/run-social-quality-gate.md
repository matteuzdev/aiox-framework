---
task: Run Social Quality Gate
responsavel: "@social-quality-auditor"
responsavel_type: agent
atomic_layer: task
Entrada: |
  - carousel_batch: visual batch ready for review
  - caption_batch: copy batch ready for review
  - platform_rules: publishing criteria and quality bar
Saida: |
  - publish_verdict: pass, conditional pass or fail
  - correction_list: what must be fixed before publishing
Checklist:
  - "[ ] Check hook quality and message clarity"
  - "[ ] Check brand coherence and readability"
  - "[ ] Check CTA and post objective alignment"
  - "[ ] Reject weak or redundant posts"
---

# *run-social-quality-gate

Valida se o lote merece ser publicado ou se ainda enfraquece a autoridade.
