"""Konig SDR Agent - Sales Development Representative.

Agente SDR humanizado com Python + Agno Framework + Groq/Llama.
Inspirado nas estrategias do GPT Maker e Zaya AI.
"""

import os
import json
import re
import httpx
from datetime import datetime
from pathlib import Path
from typing import Optional
from enum import Enum

from agno.agent import Agent
from agno.models.groq import Groq
from agno.db.sqlite import SqliteDb
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).parent.parent.parent
CRM_CONFIG = BASE_DIR.parent / "konig-orchestration-engine" / ".crm-config.json"


class CommunicationType(str, Enum):
    FORMAL = "FORMAL"
    NORMAL = "NORMAL"
    RELAXED = "RELAXED"


class AgentType(str, Enum):
    SUPPORT = "SUPPORT"
    SALE = "SALE"
    PERSONAL = "PERSONAL"


def _get_crm_config() -> dict:
    if CRM_CONFIG.exists():
        return json.loads(CRM_CONFIG.read_text())
    return {}


def _get_headers() -> dict:
    token = os.getenv("NOTION_TOKEN")
    return {
        "Authorization": f"Bearer {token}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json",
    }


def qualify_lead(name: str, company: str, role: str, initial_message: str, source: str = "Website") -> str:
    """Qualifica um lead usando criterios BANT."""
    score_map = {"alto": 2, "medio": 1, "baixo": 0, "desconhecido": 0}
    timing_map = {"urgente": 3, "<30 dias": 2, "<90 dias": 1, ">90 dias": 0, "desconhecido": 0}
    authority_map = {"decisor": 2, "influenciador": 1, "desconhecido": 0}

    budget = "medio"
    authority = "decisor" if any(w in role for w in ["CEO", "Diretor", "CTO", "Founder", "Socio"]) else "influenciador"
    need = "alto" if any(w in initial_message.lower() for w in ["preciso", "problema", "dor", "automacao", "escalar"]) else "medio"
    timing = "<30 dias"

    total = score_map.get(budget, 0) + authority_map.get(authority, 0) + score_map.get(need, 0) + timing_map.get(timing, 0)

    if total >= 7:
        score = "Quente"
    elif total >= 4:
        score = "Morno"
    else:
        score = "Frio"

    return json.dumps({
        "name": name,
        "company": company,
        "role": role,
        "budget": budget,
        "authority": authority,
        "need": need,
        "timing": timing,
        "score": score,
        "next_step": "Contato imediato" if score == "Quente" else "Sequencia de nurturing",
    }, ensure_ascii=False, indent=2)


def create_lead_in_crm(name: str, email: str, company: str, source: str = "Website", phone: str = "", role: str = "") -> str:
    """Cria um novo lead no CRM do Notion."""
    config = _get_crm_config()
    headers = _get_headers()
    db_id = config.get("crm_leads_db")
    if not db_id:
        return "ERRO: CRM nao configurado. Rode crm_setup.py primeiro."

    payload = {
        "parent": {"type": "database_id", "database_id": db_id},
        "properties": {
            "Nome": {"title": [{"text": {"content": name}}]},
            "Email": {"email": email},
            "Empresa": {"rich_text": [{"text": {"content": company}}]},
            "Fonte": {"select": {"name": source}},
            "Status": {"select": {"name": "Novo"}},
        },
    }
    if phone:
        payload["properties"]["Telefone"] = {"phone_number": phone}
    if role:
        payload["properties"]["Cargo"] = {"rich_text": [{"text": {"content": role}}]}

    r = httpx.post("https://api.notion.com/v1/pages", headers=headers, json=payload)
    if r.status_code == 200:
        return f"Lead '{name}' criado no CRM com sucesso!"
    return f"Erro ao criar lead: {r.text[:200]}"


def update_lead_status(name: str, status: str, score: str = "", notes: str = "") -> str:
    """Atualiza status e score de um lead no CRM."""
    config = _get_crm_config()
    headers = _get_headers()
    db_id = config.get("crm_leads_db")

    payload = {"filter": {"property": "Nome", "title": {"equals": name}}}
    r = httpx.post(f"https://api.notion.com/v1/databases/{db_id}/query", headers=headers, json=payload)
    if r.status_code != 200 or not r.json().get("results"):
        return f"Lead '{name}' nao encontrado."

    lead_id = r.json()["results"][0]["id"]
    update_props = {"Status": {"select": {"name": status}}}
    if score:
        update_props["Score"] = {"select": {"name": score}}
    if notes:
        update_props["Notas"] = {"rich_text": [{"text": {"content": notes}}]}

    r2 = httpx.patch(f"https://api.notion.com/v1/pages/{lead_id}", headers=headers, json={"properties": update_props})
    if r2.status_code == 200:
        return f"Lead '{name}' atualizado para '{status}' com score '{score}'."
    return f"Erro ao atualizar: {r2.text[:200]}"


def create_deal(deal_name: str, company: str, contact: str, value: float, stage: str = "Prospeccao") -> str:
    """Cria um deal no pipeline do CRM."""
    config = _get_crm_config()
    headers = _get_headers()
    db_id = config.get("crm_deals_db")
    if not db_id:
        return "ERRO: CRM nao configurado."

    payload = {
        "parent": {"type": "database_id", "database_id": db_id},
        "properties": {
            "Deal": {"title": [{"text": {"content": deal_name}}]},
            "Empresa": {"rich_text": [{"text": {"content": company}}]},
            "Contato": {"rich_text": [{"text": {"content": contact}}]},
            "Valor": {"number": value},
            "Etapa": {"select": {"name": stage}},
            "Criado Em": {"date": {"start": datetime.now().isoformat()}},
        },
    }

    r = httpx.post("https://api.notion.com/v1/pages", headers=headers, json=payload)
    if r.status_code == 200:
        return f"Deal '{deal_name}' criado com valor R${value:,.2f} na etapa '{stage}'."
    return f"Erro ao criar deal: {r.text[:200]}"


def schedule_activity(activity_name: str, activity_type: str, lead: str = "", due_date: str = "", notes: str = "") -> str:
    """Agenda uma atividade no CRM."""
    config = _get_crm_config()
    headers = _get_headers()
    db_id = config.get("crm_activities_db")
    if not db_id:
        return "ERRO: CRM nao configurado."

    payload = {
        "parent": {"type": "database_id", "database_id": db_id},
        "properties": {
            "Atividade": {"title": [{"text": {"content": activity_name}}]},
            "Tipo": {"select": {"name": activity_type}},
            "Status": {"select": {"name": "Pendente"}},
        },
    }
    if lead:
        payload["properties"]["Lead"] = {"rich_text": [{"text": {"content": lead}}]}
    if due_date:
        payload["properties"]["Data"] = {"date": {"start": due_date}}
    if notes:
        payload["properties"]["Notas"] = {"rich_text": [{"text": {"content": notes}}]}

    r = httpx.post("https://api.notion.com/v1/pages", headers=headers, json=payload)
    if r.status_code == 200:
        return f"Atividade '{activity_name}' agendada com sucesso."
    return f"Erro ao agendar: {r.text[:200]}"


def build_humanization_prompt(
    communication_type: CommunicationType = CommunicationType.NORMAL,
    job_name: str = "Konig Systems",
    job_description: str = "AI-powered business automation",
) -> str:
    tone_map = {
        CommunicationType.FORMAL: "formal e profissional, mas acessivel",
        CommunicationType.NORMAL: "natural e conversacional, como um colega experiente",
        CommunicationType.RELAXED: "casual e amigavel, como uma conversa entre amigos",
    }

    return f"""Voce e um SDR (Sales Development Representative) da {job_name}.

TOM DE VOZ: {tone_map[communication_type]}
OBJETIVO: {job_description}

PERSONALIDADE:
- Curioso e faz perguntas abertas
- Empatico e bom ouvinte
- Direto mas caloroso
- Usa linguagem natural, nunca robotica
- Evita jargoes corporativos
- Personaliza cada mensagem

REGRAS DE LINGUAGEM:
1. SEMPRE use o primeiro nome do lead
2. Faca perguntas abertas para entender a dor
3. Referencie contexto especifico do lead
4. NUNCA use templates genericos
5. Use transicoes naturais entre topicos
6. Inclua observacoes pessoais quando relevante
7. Varie o comprimento das frases
8. Use contracoes e linguagem coloquial quando apropriado
9. Demonstre empatia genuina
10. Respeite o tempo e limites do lead

REGRAS CRITICAS:
- NUNCA parea um robot
- SEMPRE personalize com base no contexto
- Evite "Espero que esteja bem" ou frases feitas
- Maximo 150 palavras por mensagem
- Faca UMA pergunta por mensagem"""


class SDRAgent:
    """Agente SDR humanizado com Agno + Groq/Llama."""

    def __init__(
        self,
        model: str = "llama-3.3-70b-versatile",
        communication_type: CommunicationType = CommunicationType.NORMAL,
    ):
        agent_db = SqliteDb(db_file=str(BASE_DIR / "sdr_memory.db"))

        self.agent = Agent(
            name="Konig SDR Agent",
            model=Groq(id=model),
            instructions=build_humanization_prompt(communication_type),
            db=agent_db,
            markdown=True,
            add_history_to_context=True,
            num_history_runs=10,
        )

    def _extract_json(self, text: str) -> Optional[dict]:
        """Extrai JSON da resposta do LLM."""
        match = re.search(r'\{[^{}]*\}', text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass
        return None

    def process_lead(self, name: str, email: str, company: str, role: str, source: str = "Website", context: str = "", deal_value: float = 0) -> str:
        """Processa um lead completo: qualifica, cria no CRM, gera outreach."""
        output = []

        # 1. Qualifica
        qual_result = qualify_lead(name, company, role, context, source)
        qual_data = json.loads(qual_result)
        score = qual_data["score"]

        output.append(f"## Qualificacao BANT")
        output.append(f"- **Score**: {score}")
        output.append(f"- **Budget**: {qual_data['budget']}")
        output.append(f"- **Authority**: {qual_data['authority']}")
        output.append(f"- **Need**: {qual_data['need']}")
        output.append(f"- **Timing**: {qual_data['timing']}")
        output.append(f"- **Proximo passo**: {qual_data['next_step']}")
        output.append("")

        # 2. Cria no CRM
        crm_result = create_lead_in_crm(name, email, company, source, role=role)
        output.append(f"## CRM: {crm_result}")
        output.append("")

        # 3. Atualiza status baseado no score
        if score == "Quente":
            status = "Qualificado"
        elif score == "Morno":
            status = "Contatado"
        else:
            status = "Novo"

        update_result = update_lead_status(name, status, score, f"Qualificado automaticamente pelo SDR Agent. Score: {score}")
        output.append(f"## Status: {update_result}")
        output.append("")

        # 4. Cria deal se score for Quente ou Morno
        if score in ("Quente", "Morno") and deal_value > 0:
            deal_result = create_deal(
                f"{company} - {name}",
                company,
                name,
                deal_value,
                "Prospeccao" if score == "Morno" else "Qualificacao",
            )
            output.append(f"## Deal: {deal_result}")
            output.append("")

            # 5. Agenda follow-up
            from datetime import timedelta
            follow_up_date = (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d")
            activity_result = schedule_activity(
                f"Follow-up com {name}",
                "Email",
                lead=name,
                due_date=follow_up_date,
                notes=f"Lead score: {score}. Contexto: {context[:100]}",
            )
            output.append(f"## Atividade: {activity_result}")
            output.append("")

        # 6. Gera mensagem de outreach via LLM
        outreach_prompt = f"""Crie uma mensagem de outreach para este lead:

Nome: {name}
Cargo: {role}
Empresa: {company}
Contexto: {context}
Score: {score}

REGRAS: Maximo 150 palavras. Use o primeiro nome. Faca uma pergunta aberta no final. Seja natural."""

        response = self.agent.run(outreach_prompt)
        output.append(f"## Mensagem de Outreach")
        output.append(response.content)
        output.append("")

        return "\n".join(output)


def main():
    print("=" * 60)
    print("KONIG SDR AGENT - Groq + Llama 3.3")
    print("=" * 60)
    print()

    sdr = SDRAgent(communication_type=CommunicationType.NORMAL)

    print("Processando lead: Maria Silva - TechStartup Brasil")
    print()

    result = sdr.process_lead(
        name="Maria Silva",
        email="maria@techstartup.com.br",
        company="TechStartup Brasil",
        role="CEO",
        source="LinkedIn",
        context="Vi que estao expandindo e contratando. Provavelmente precisam de automacao para escalar operacoes.",
        deal_value=15000,
    )

    print(result)
    print()
    print("=" * 60)


if __name__ == "__main__":
    main()
