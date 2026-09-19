# Agency OS Framework — Architecture v0.1

Framework operacional para uma agência híbrida de Marketing Digital + Inteligência Artificial.

## Princípio central

Um agente não é apenas um prompt/persona. Cada agente operacional é composto por:

```
Agent = Persona + Role + Skills + Context + Tools + Connectors + Workflows + Memory + Policies + QA + Metrics
```

A arquitetura combina duas ideias de referência:

1. **AIOX** — organização do trabalho em agentes/papéis, tarefas e workflows reutilizáveis.
2. **MatrAIx** — separação entre persona, aplicação/tarefa e ambiente de execução; personas estruturadas; execução por agentes; adapters; verificação e artefatos.

O framework NÃO copia essas bases. Ele adapta os princípios para uma agência que executa trabalho real.

## Camadas

```
CLIENT / BRAND CONTEXT
        ↓
ORCHESTRATOR
        ↓
DEPARTMENTS
        ↓
OPERATIONAL AGENTS
        ↓
SKILLS + WORKFLOWS
        ↓
CONNECTOR / TOOL ROUTER
        ↓
REAL SYSTEMS (social, ads, CRM, CMS, analytics, email, WhatsApp...)
        ↓
OBSERVABILITY + QA + APPROVAL
        ↓
MEMORY / LEARNING
```

## Núcleo inicial de agentes

### Executive / Strategy
- Agency Orchestrator
- Account Strategist
- Market & Competitor Researcher
- Brand Strategist
- Offer Strategist

### Growth / Marketing
- Social Media Operator
- Content Strategist
- Copywriter
- Creative Strategist
- Paid Media Operator
- SEO/GEO Operator
- CRO/Landing Page Operator
- Email/CRM Operator
- Analytics & Growth Analyst

### Sales
- Lead Researcher
- SDR / Outreach Operator
- Sales Agent
- Follow-up Agent

### AI / Automation
- Automation Architect
- AI Agent Engineer
- Integration Engineer
- Context Engineer
- Workflow Reliability Agent

### Quality
- Brand Guardian
- Marketing QA
- Compliance/Approval Gate
- Performance Auditor

## Operational Agent Contract

Todo agente executável deverá possuir um manifesto:

```yaml
id: social-media-operator
department: growth
persona: personas/social-media-operator.yaml
role: social-media
skills:
  - content-research
  - content-planning
  - copywriting
  - creative-brief
  - scheduling
  - community-management
connectors:
  required:
    - social-network
  optional:
    - analytics
    - asset-storage
workflows:
  - audit-profile
  - build-calendar
  - create-post
  - publish-post
  - monitor-performance
  - reply-community
memory:
  scopes:
    - brand
    - client
    - campaign
    - performance
approval:
  publish: required_by_default
metrics:
  - reach
  - engagement
  - clicks
  - leads
```

## Connector architecture

Agentes não devem conhecer diretamente cada API. Eles chamam capacidades padronizadas.

```
Agent
  → Tool Router
      → Connector Interface
          → Provider Adapter
```

Exemplo:

```
Social Media Agent
  → social.publish()
  → social.read_metrics()
  → social.read_comments()
  → social.reply()
        ↓
Social Connector
        ↓
Provider Adapter
        ↓
API/autorização oficial da plataforma
```

Isso permite trocar uma plataforma sem reescrever o agente.

## Social Media Agent — fluxo real

```
Brand Context
    ↓
Research
    ↓
Content Strategy
    ↓
Calendar
    ↓
Post Draft
    ↓
Creative
    ↓
Brand/QA Gate
    ↓
Human Approval (quando exigido)
    ↓
Social Connector
    ↓
Publish/Schedule
    ↓
Collect Metrics
    ↓
Performance Analysis
    ↓
Memory
    ↓
Next Content Cycle
```

O agente deve poder operar conectado às plataformas autorizadas pelo cliente, e não apenas gerar textos.

## Estrutura alvo do repositório

```
agency-os/
├── core/
│   ├── orchestrator/
│   ├── runtime/
│   ├── context/
│   ├── memory/
│   ├── tool-router/
│   ├── approvals/
│   └── observability/
├── personas/
│   ├── schema/
│   ├── executive/
│   ├── marketing/
│   ├── sales/
│   └── ai/
├── agents/
│   ├── strategy/
│   ├── social/
│   ├── content/
│   ├── paid-media/
│   ├── seo-geo/
│   ├── crm/
│   ├── sales/
│   └── automation/
├── skills/
├── workflows/
├── connectors/
│   ├── social/
│   ├── ads/
│   ├── crm/
│   ├── cms/
│   ├── messaging/
│   ├── email/
│   ├── analytics/
│   └── storage/
├── adapters/
├── clients/
├── policies/
├── qa/
├── evaluations/
├── templates/
└── docs/
```

## Persona layer

A persona operacional deve ser estruturada, não um parágrafo de prompt. O schema deverá guardar, entre outros:

- identidade profissional
- senioridade
- domínio
- subdomínios
- objetivos
- heurísticas de decisão
- comportamento
- comunicação
- competências
- restrições
- tolerância a risco
- ferramentas
- contexto permitido
- critérios de qualidade
- escalonamento
- anti-patterns

As personas do MatrAIx serão referência para profundidade e diversidade de atributos, mas as personas operacionais da agência terão dimensões específicas de competência, responsabilidade e execução.

## Segurança operacional

Ações externas devem possuir políticas por risco:

- READ: pode executar automaticamente.
- DRAFT: pode produzir automaticamente.
- WRITE: depende da política do cliente.
- SPEND: aprovação obrigatória por padrão.
- DELETE: aprovação obrigatória.
- CREDENTIALS: nunca expor ao modelo; usar secret manager/connector.
- PUBLISH: configurável, com aprovação humana padrão no início.

## Objetivo

Transformar a agência em um sistema operacional de agentes:

```
brief do cliente
→ contexto estruturado
→ plano
→ delegação
→ execução
→ ferramentas reais
→ QA
→ aprovação
→ publicação/ação
→ métricas
→ aprendizado
→ próximo ciclo
```

O framework deve servir tanto para prestação de serviços de marketing quanto para automações, integrações e agentes de IA.
