# Sales Cycle Workflow

## Overview
Workflow completo do ciclo de vendas

## Quando usar
- Processar leads até fechamento
- Executar prospecção ativa
- Fechar deals

## Stages

### Stage 1: Prospecting (konig-prospecting-core)
**Duração:** Contínuo

**Steps:**
1. Definir ICP
2. Scrap Google Maps / LinkedIn
3. Enrich dados (emails, phones)
4. Feed CRM

**Entrega:** Leads qualificados no CRM

---

### Stage 2: Revenue (konig-revenue-core)
**Duração:** 7-21 dias

**Steps:**
1. SDR qualification
2. Discovery call
3. Enviar proposta
4. Negociar
5. Fechar

**Entrega:** Deal fechado

---

### Stage 3: Delivery (konig-delivery-factory-core)
**Duração:** Define per project

**Steps:**
1. Definition of done
2. Execução
3. Evidence
4. Accepted deliverable

**Entrega:** Cliente feliz

---

### Stage 4: Operations (konig-ops-core)
**Duração:** Contínuo

**Steps:**
1. Onboard cliente
2. Suporte contínuo
3. Upsell / cross-sell
4. Estabilidade

**Entrega:** Retention + expansão

---

## Dependencies
- konig-prospecting-core → konig-revenue-core
- konig-revenue-core → konig-delivery-factory-core
- konig-delivery-factory-core → konig-ops-core

## Owner
**Stage Lead:** Revenue Chief
**Quota Owner:** SDR Lead