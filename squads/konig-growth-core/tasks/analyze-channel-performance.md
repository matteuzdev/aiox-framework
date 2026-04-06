---
task: Analyze Channel Performance
responsavel: "@acquisition-operator"
responsavel_type: agent
atomic_layer: task
Entrada: |
  - channel_data: campaign and funnel metrics
  - growth_loop_plan: active experiments
Saida: |
  - channel_verdict: keep, improve or cut
  - action_plan: immediate optimization actions
Checklist:
  - "[ ] Compare channel performance against target metrics"
  - "[ ] Identify bottlenecks by stage"
  - "[ ] Recommend action with owner and priority"
---

# *analyze-channel-performance

Transforma dados de canal em decisao operacional de crescimento.
