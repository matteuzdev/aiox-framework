# Instagram Pilot Run - Oftalmo (Manual Execution)

Date: 2026-04-04
Squad: `konig-instagram-intelligence-core`
Vertical: oftalmologia privada
Objective: testar o squad em um caso real da Konig Systems e gerar um primeiro lote editorial utilizavel
Execution: Manual (Codex CLI com limite de uso atingido — executado pelo Claude diretamente)

## Stage 1 — Competitor Intel

[HANDOFF]
de: instagram-chief
para: competitor-intel-analyst
objetivo: mapear concorrentes e referencias publicas de oftalmo para entender posicionamento, gaps e sinais editoriais
artefatos: niche=oftalmo, objective=criar conteudo de autoridade
criterio_de_aceite: competitor_map.md, viral_patterns.md e content_gaps.md entregues com evidencia e inferencias separadas
status: completed
[/HANDOFF]

Outputs:
- competitor_map.md — 4 perfis analisados (Alclin, CBCO, COE, Rede Oftalmo), evidencia separada de inferencia
- viral_patterns.md — 5 hooks recorrentes, 4 formatos, benchmarks de cadencia
- content_gaps.md — 5 gaps identificados e priorizados

## Stage 2 — Editorial War Map

[HANDOFF]
de: competitor-intel-analyst
para: content-pattern-strategist
objetivo: transformar leitura competitiva em pilares editoriais, angulos e backlog inicial de posts
artefatos: competitor_map.md, viral_patterns.md, content_gaps.md
criterio_de_aceite: editorial_war_map.md e post_backlog.md priorizados para publicacao
status: completed
[/HANDOFF]

Outputs:
- editorial_pillars.md — 4 pilares com series e distribuicao (40/30/20/10)
- post_backlog.md — 5 posts P0 + 5 posts P1
- platform_rules.md — regras de hook, slide, CTA, cadencia e qualidade

## Stage 3 — Carousel Batch

[HANDOFF]
de: content-pattern-strategist
para: carousel-factory
objetivo: converter backlog priorizado em estruturas de carrossel com logica de slides
artefatos: editorial_pillars.md, post_backlog.md, platform_rules.md
criterio_de_aceite: carousel_batch.md com lote inicial utilizavel
status: completed
[/HANDOFF]

Outputs:
- carousel_batch.md — 5 carrosseis completos com conteudo slide a slide
- slide_logic.md — tabela de hook, progressao e CTA por slide

## Stage 4 — Caption Batch

[HANDOFF]
de: carousel-factory
para: caption-engineer
objetivo: escrever hooks, legendas e CTAs para o lote inicial
artefatos: carousel_batch.md, slide_logic.md
criterio_de_aceite: caption_batch.md alinhado ao objetivo de autoridade e demanda
status: completed
[/HANDOFF]

Outputs:
- caption_batch.md — 5 legendas completas com hook, body, CTA, hashtags e alt-text
- accessibility_notes.md — diretrizes de acessibilidade por post

## Stage 5 — Social Quality Gate

[HANDOFF]
de: caption-engineer
para: social-quality-auditor
objetivo: validar se o lote merece ir ao ar como piloto da Konig
artefatos: carousel_batch.md, caption_batch.md, platform_rules.md
criterio_de_aceite: qa_report.md com veredito claro e correcoes necessarias
status: completed
[/HANDOFF]

Outputs:
- qa_report.md — Veredito: CONDITIONAL PASS (8.3/10 media do lote)
  - 4 correcoes obrigatorias identificadas
  - Recomendacoes de sequencia de publicacao
  - Score individual por post

## Resultado Final

**STATUS: CONDITIONAL PASS**

Lote aprovado como piloto da Konig Systems para oftalmologia privada, com 4 correcoes obrigatorias antes de publicar.

Artefatos totais gerados: 11
- competitor_map.md
- viral_patterns.md
- content_gaps.md
- editorial_pillars.md
- post_backlog.md
- platform_rules.md
- carousel_batch.md
- slide_logic.md
- caption_batch.md
- accessibility_notes.md
- qa_report.md
