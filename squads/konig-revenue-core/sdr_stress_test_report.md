# Stress Test - SDR Agent

## Resumo
- **Data**: 2026-04-05 03:11
- **Total**: 15
- **Pass**: 14
- **Fail**: 1
- **Taxa**: 93%

## Resultados

| # | Teste | Status | Detalhes |
|---|-------|--------|----------|
| 1 | Normal | PASS |  |
| 2 | Com contexto | PASS |  |
| 3 | Vazio | FAIL | Esperava erro, got 200 |
| 4 | Emoji | PASS |  |
| 5 | HTML injection | PASS |  |
| 6 | SQL injection | PASS |  |
| 7 | Unicode | PASS |  |
| 8 | Agressivo | PASS |  |
| 9 | Fora contexto | PASS |  |
| 10 | Com email | PASS |  |
| 11 | Turno 1 | PASS |  |
| 12 | Turno 2 | PASS |  |
| 13 | Turno 3 | PASS |  |
| 14 | User 1 | PASS |  |
| 15 | User 2 | PASS |  |

## Categorias
1. Mensagens Normais
2. Edge Cases (vazio, emoji, injection, unicode)
3. Comportamento (agressivo, fora contexto)
4. Lead Creation
5. Multi-Turno
6. Concorrente
