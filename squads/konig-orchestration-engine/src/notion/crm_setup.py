#!/usr/bin/env python3
"""Konig Systems - CRM Notion Setup.

Cria databases de CRM no Notion:
- Leads/Contatos
- Empresas
- Deals/Negocios com pipeline Kanban
- Atividades/Tarefas
"""

import json
import httpx
from pathlib import Path

# Config
BASE_DIR = Path(__file__).parent.parent.parent
NOTION_TOKEN = "ntn_c735562228178mKoCWkntIoCiDsCNkbTo01NeGmcR0cgOw"
NOTION_PAGE_ID = "3391b66de389803eb8b3f5de0fea3b1a"

HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json",
}


def create_leads_database(parent_page_id):
    """Cria database de Leads/Contatos."""
    print("[CRM] Criando database de Leads...")
    
    payload = {
        "parent": {"type": "page_id", "page_id": parent_page_id},
        "title": [{"text": {"content": "Konig CRM - Leads"}}],
        "description": [{"text": {"content": "Contatos e leads do pipeline de vendas"}}],
        "properties": {
            "Nome": {"title": {}},
            "Email": {"email": {}},
            "Telefone": {"phone_number": {}},
            "Empresa": {"rich_text": {}},
            "Cargo": {"rich_text": {}},
            "Fonte": {
                "select": {
                    "options": [
                        {"name": "Website", "color": "blue"},
                        {"name": "LinkedIn", "color": "purple"},
                        {"name": "Indicacao", "color": "green"},
                        {"name": "Cold Outreach", "color": "orange"},
                        {"name": "Evento", "color": "yellow"},
                        {"name": "Anuncio", "color": "red"},
                    ]
                }
            },
            "Status": {
                "select": {
                    "options": [
                        {"name": "Novo", "color": "blue"},
                        {"name": "Contatado", "color": "yellow"},
                        {"name": "Qualificado", "color": "green"},
                        {"name": "Desqualificado", "color": "red"},
                        {"name": "Em Negociacao", "color": "orange"},
                    ]
                }
            },
            "Score": {
                "select": {
                    "options": [
                        {"name": "Quente", "color": "red"},
                        {"name": "Morno", "color": "yellow"},
                        {"name": "Frio", "color": "blue"},
                    ]
                }
            },
            "Valor Estimado": {"number": {}},
            "Ultimo Contato": {"date": {}},
            "Notas": {"rich_text": {}},
        },
    }
    
    r = httpx.post("https://api.notion.com/v1/databases", headers=HEADERS, json=payload)
    if r.status_code == 200:
        db_id = r.json()["id"]
        print(f"[CRM] Database de Leads criada: {db_id}")
        return db_id
    else:
        print(f"[ERRO] {r.status_code}: {r.text}")
        return None


def create_companies_database(parent_page_id):
    """Cria database de Empresas."""
    print("[CRM] Criando database de Empresas...")
    
    payload = {
        "parent": {"type": "page_id", "page_id": parent_page_id},
        "title": [{"text": {"content": "Konig CRM - Empresas"}}],
        "description": [{"text": {"content": "Empresas e contas do pipeline"}}],
        "properties": {
            "Empresa": {"title": {}},
            "Website": {"url": {}},
            "Setor": {
                "select": {
                    "options": [
                        {"name": "Tecnologia", "color": "blue"},
                        {"name": "Servicos", "color": "green"},
                        {"name": "E-commerce", "color": "orange"},
                        {"name": "Saude", "color": "red"},
                        {"name": "Educacao", "color": "yellow"},
                        {"name": "Financeiro", "color": "purple"},
                    ]
                }
            },
            "Tamanho": {
                "select": {
                    "options": [
                        {"name": "1-10", "color": "gray"},
                        {"name": "11-50", "color": "brown"},
                        {"name": "51-200", "color": "orange"},
                        {"name": "201-1000", "color": "yellow"},
                        {"name": "1000+", "color": "green"},
                    ]
                }
            },
            "Receita Anual": {"number": {}},
            "Pais": {"rich_text": {}},
            "Contatos": {"number": {}},
            "Notas": {"rich_text": {}},
        },
    }
    
    r = httpx.post("https://api.notion.com/v1/databases", headers=HEADERS, json=payload)
    if r.status_code == 200:
        db_id = r.json()["id"]
        print(f"[CRM] Database de Empresas criada: {db_id}")
        return db_id
    else:
        print(f"[ERRO] {r.status_code}: {r.text}")
        return None


def create_deals_database(parent_page_id):
    """Cria database de Deals com pipeline Kanban."""
    print("[CRM] Criando database de Deals (Pipeline)...")
    
    payload = {
        "parent": {"type": "page_id", "page_id": parent_page_id},
        "title": [{"text": {"content": "Konig CRM - Pipeline"}}],
        "description": [{"text": {"content": "Negocios ativos no funil de vendas"}}],
        "properties": {
            "Deal": {"title": {}},
            "Empresa": {"rich_text": {}},
            "Contato": {"rich_text": {}},
            "Valor": {"number": {}},
            "Moeda": {
                "select": {
                    "options": [
                        {"name": "BRL", "color": "green"},
                        {"name": "USD", "color": "blue"},
                        {"name": "EUR", "color": "purple"},
                    ]
                }
            },
            "Etapa": {
                "select": {
                    "options": [
                        {"name": "Prospeccao", "color": "gray"},
                        {"name": "Qualificacao", "color": "yellow"},
                        {"name": "Proposta", "color": "blue"},
                        {"name": "Negociacao", "color": "orange"},
                        {"name": "Fechamento", "color": "green"},
                        {"name": "Perdido", "color": "red"},
                    ]
                }
            },
            "Probabilidade": {
                "select": {
                    "options": [
                        {"name": "10%", "color": "red"},
                        {"name": "25%", "color": "orange"},
                        {"name": "50%", "color": "yellow"},
                        {"name": "75%", "color": "blue"},
                        {"name": "90%", "color": "green"},
                    ]
                }
            },
            "Data Prevista": {"date": {}},
            "Criado Em": {"date": {}},
            "Prioridade": {
                "select": {
                    "options": [
                        {"name": "Alta", "color": "red"},
                        {"name": "Media", "color": "yellow"},
                        {"name": "Baixa", "color": "green"},
                    ]
                }
            },
            "Motivo Perda": {"rich_text": {}},
            "Notas": {"rich_text": {}},
        },
    }
    
    r = httpx.post("https://api.notion.com/v1/databases", headers=HEADERS, json=payload)
    if r.status_code == 200:
        db_id = r.json()["id"]
        print(f"[CRM] Database de Deals criada: {db_id}")
        return db_id
    else:
        print(f"[ERRO] {r.status_code}: {r.text}")
        return None


def create_activities_database(parent_page_id):
    """Cria database de Atividades/Tarefas."""
    print("[CRM] Criando database de Atividades...")
    
    payload = {
        "parent": {"type": "page_id", "page_id": parent_page_id},
        "title": [{"text": {"content": "Konig CRM - Atividades"}}],
        "description": [{"text": {"content": "Tarefas e atividades do time de vendas"}}],
        "properties": {
            "Atividade": {"title": {}},
            "Tipo": {
                "select": {
                    "options": [
                        {"name": "Ligacao", "color": "green"},
                        {"name": "Email", "color": "blue"},
                        {"name": "Reuniao", "color": "purple"},
                        {"name": "Follow-up", "color": "yellow"},
                        {"name": "Proposta", "color": "orange"},
                        {"name": "Demo", "color": "red"},
                    ]
                }
            },
            "Status": {
                "select": {
                    "options": [
                        {"name": "Pendente", "color": "yellow"},
                        {"name": "Em Andamento", "color": "blue"},
                        {"name": "Concluida", "color": "green"},
                        {"name": "Cancelada", "color": "red"},
                    ]
                }
            },
            "Lead": {"rich_text": {}},
            "Deal": {"rich_text": {}},
            "Responsavel": {"rich_text": {}},
            "Data": {"date": {}},
            "Duracao": {"rich_text": {}},
            "Resultado": {"rich_text": {}},
            "Notas": {"rich_text": {}},
        },
    }
    
    r = httpx.post("https://api.notion.com/v1/databases", headers=HEADERS, json=payload)
    if r.status_code == 200:
        db_id = r.json()["id"]
        print(f"[CRM] Database de Atividades criada: {db_id}")
        return db_id
    else:
        print(f"[ERRO] {r.status_code}: {r.text}")
        return None


def create_dashboard_page(parent_page_id, leads_db, companies_db, deals_db, activities_db):
    """Cria pagina de Dashboard do CRM."""
    print("[CRM] Criando Dashboard...")
    
    payload = {
        "parent": {"type": "page_id", "page_id": parent_page_id},
        "properties": {"title": {"title": [{"text": {"content": "Konig CRM - Dashboard"}}]}},
        "children": [
            {"object": "block", "type": "heading_1", "heading_1": {"rich_text": [{"text": {"content": "Konig CRM - Painel de Vendas"}}]}},
            {"object": "block", "type": "paragraph", "paragraph": {"rich_text": [{"text": {"content": "Visao completa do funil de vendas. O agente SDR atualiza automaticamente leads e deals."}}]}},
            {"object": "block", "type": "heading_2", "heading_2": {"rich_text": [{"text": {"content": "Como Funciona"}}]}},
            {"object": "block", "type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"text": {"content": "SDR Agent qualifica leads e atualiza o pipeline automaticamente"}}]}},
            {"object": "block", "type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"text": {"content": "Cada lead passa por: Prospeccao -> Qualificacao -> Proposta -> Negociacao -> Fechamento"}}]}},
            {"object": "block", "type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"text": {"content": "Score automatico: Quente, Morno, Frio baseado em engagement e fit"}}]}},
            {"object": "block", "type": "divider", "divider": {}},
            {"object": "block", "type": "heading_2", "heading_2": {"rich_text": [{"text": {"content": "Estrategia de Humanizacao do SDR"}}]}},
            {"object": "block", "type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"text": {"content": "Communication Style: NORMAL (equilibrio entre profissional e natural)"}}]}},
            {"object": "block", "type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"text": {"content": "Personalidade: Curioso, empatico, direto ao ponto"}}]}},
            {"object": "block", "type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"text": {"content": "Linguagem: Evita jargoes, usa perguntas abertas, faz follow-up personalizado"}}]}},
            {"object": "block", "type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"text": {"content": "Timing: Respostas em 2-5 min, follow-ups em 24-48h"}}]}},
            {"object": "block", "type": "divider", "divider": {}},
            {"object": "block", "type": "heading_2", "heading_2": {"rich_text": [{"text": {"content": "Databases"}}]}},
            {"object": "block", "type": "paragraph", "paragraph": {"rich_text": [{"text": {"content": f"Leads: {leads_db}"}}]}},
            {"object": "block", "type": "paragraph", "paragraph": {"rich_text": [{"text": {"content": f"Empresas: {companies_db}"}}]}},
            {"object": "block", "type": "paragraph", "paragraph": {"rich_text": [{"text": {"content": f"Deals: {deals_db}"}}]}},
            {"object": "block", "type": "paragraph", "paragraph": {"rich_text": [{"text": {"content": f"Atividades: {activities_db}"}}]}},
        ],
    }
    
    r = httpx.post("https://api.notion.com/v1/pages", headers=HEADERS, json=payload)
    if r.status_code == 200:
        page_id = r.json()["id"]
        print(f"[CRM] Dashboard criado: {page_id}")
        return page_id
    else:
        print(f"[ERRO] {r.status_code}: {r.text}")
        return None


def main():
    print("=" * 60)
    print("KONIG CRM - Notion Setup")
    print("=" * 60)
    print()
    
    leads_db = create_leads_database(NOTION_PAGE_ID)
    companies_db = create_companies_database(NOTION_PAGE_ID)
    deals_db = create_deals_database(NOTION_PAGE_ID)
    activities_db = create_activities_database(NOTION_PAGE_ID)
    dashboard = create_dashboard_page(NOTION_PAGE_ID, leads_db, companies_db, deals_db, activities_db)
    
    config = {
        "crm_leads_db": leads_db,
        "crm_companies_db": companies_db,
        "crm_deals_db": deals_db,
        "crm_activities_db": activities_db,
        "crm_dashboard": dashboard,
    }
    
    config_file = BASE_DIR / ".crm-config.json"
    config_file.write_text(json.dumps(config, indent=2))
    print(f"\n[CRM] Config salva em {config_file}")
    print()
    print("CRM criado com sucesso!")


if __name__ == "__main__":
    main()
