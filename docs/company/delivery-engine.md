# Konig Delivery Engine

## Base

O time de dev da Konig deve herdar princípios do `GSD 2`, sem importar o sistema inteiro para dentro deste repo.

## O que foi absorvido do GSD 2

- contexto limpo por unidade de trabalho
- pesquisa antes do plano
- plano antes da execução
- tarefas pequenas o bastante para caber numa janela de contexto
- handoff explícito
- reavaliação depois da entrega
- observabilidade do processo

## Fluxo de entrega

1. `Research`
2. `Plan`
3. `Execute`
4. `Verify`
5. `Summarize`
6. `Reassess`

## Regra do time de dev

O dev não deve receber:
- pedido cru do CEO
- briefing mal traduzido
- ambiguidade escondida

O dev deve receber:
- decisão clara
- contexto relevante
- qualidade esperada
- critérios de aceite
- riscos conhecidos

## Guard-rails

- tarefa grande demais deve ser quebrada
- site visual não pode ser tratado como "qualquer HTML serve"
- segurança e suporte são parte da reputação da empresa, não extras

## Segurança

A camada pesada de segurança, cyber, auditoria e hardening profundo será criada como módulo próprio depois.
Mas o delivery engine já assume:

- pensar em trust boundaries
- evitar padrões inseguros comuns em IA
- não tratar deploy como final da história
