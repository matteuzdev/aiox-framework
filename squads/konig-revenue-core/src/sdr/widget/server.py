"""Konig SDR Widget Backend - FastAPI.

Backend para o widget de chat do SDR Agent.
Funciona como o widget do GPT Maker, mas com nosso SDR Agent por tras.

Endpoints:
  POST /api/chat - Envia mensagem e recebe resposta do SDR
  POST /api/lead - Cria lead no CRM
  GET  /api/widget-config - Configuracoes do widget
  GET  /api/widget.js - Script para injetar no site
"""

import os
import json
import uuid
import httpx
from pathlib import Path
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, PlainTextResponse
from pydantic import BaseModel

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from sdr_agent import SDRAgent, CommunicationType, qualify_lead, create_lead_in_crm, create_deal, schedule_activity

app = FastAPI(title="Konig SDR Widget", version="1.0.0")

# CORS - permite qualquer origem (widget injetado em sites externos)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Config paths
BASE_DIR = Path(__file__).parent.parent.parent
CRM_CONFIG = BASE_DIR.parent / "konig-orchestration-engine" / ".crm-config.json"

# Inicializa SDR Agent
sdr = SDRAgent(communication_type=CommunicationType.NORMAL)

# Sessoes de chat (em memoria - pode usar Redis em producao)
sessions: dict = {}


class ChatMessage(BaseModel):
    session_id: str
    message: str
    user_name: Optional[str] = None
    user_email: Optional[str] = None
    user_phone: Optional[str] = None
    source_url: Optional[str] = None


class LeadData(BaseModel):
    name: str
    email: str
    phone: Optional[str] = None
    company: Optional[str] = None
    message: Optional[str] = None
    source_url: Optional[str] = None


class WidgetConfig(BaseModel):
    title: str = "Konig SDR"
    subtitle: str = "Como posso te ajudar?"
    greeting: str = "Ola! Sou o assistente virtual da Konig Systems. Como posso te ajudar hoje?"
    placeholder: str = "Digite sua mensagem..."
    primary_color: str = "#6366f1"
    position: str = "right"
    company_name: str = "Konig Systems"


# Config padrao do widget
WIDGET_CONFIG = WidgetConfig(
    title="Konig SDR",
    subtitle="Assistente de Vendas",
    greeting="Ola! Sou o assistente virtual da Konig Systems. Como posso te ajudar hoje?",
    placeholder="Digite sua mensagem...",
    primary_color="#6366f1",
    position="right",
    company_name="Konig Systems",
)


@app.get("/api/widget-config")
async def get_widget_config():
    """Retorna configuracoes do widget."""
    return WIDGET_CONFIG.model_dump()


@app.post("/api/chat")
async def chat(data: ChatMessage):
    """Recebe mensagem do widget e retorna resposta do SDR Agent.
    
    Se o usuario deixou contato (nome/email), cria lead no CRM automaticamente.
    """
    session_id = data.session_id or str(uuid.uuid4())
    
    # Cria sessao se nao existe
    if session_id not in sessions:
        sessions[session_id] = {
            "id": session_id,
            "created_at": datetime.now().isoformat(),
            "messages": [],
            "lead_created": False,
            "user_data": {},
        }
    
    session = sessions[session_id]
    
    # Se usuario deixou contato e ainda nao criou lead
    if (data.user_name or data.user_email) and not session["lead_created"]:
        session["user_data"] = {
            "name": data.user_name or "",
            "email": data.user_email or "",
            "phone": data.user_phone or "",
            "company": data.user_name or "",
        }
        
        # Cria lead no CRM (com tratamento de erro)
        if data.user_email:
            try:
                name = data.user_name or data.user_email.split("@")[0]
                context = f"Veio do widget do site. Primeira mensagem: {data.message}"
                qual_result = qualify_lead(
                    name=name,
                    company=data.company or "Nao informada",
                    role="Visitante do site",
                    initial_message=data.message or "",
                    source="Website",
                )
                qual_data = json.loads(qual_result)
                
                crm_result = create_lead_in_crm(
                    name=name,
                    email=data.user_email,
                    company=data.company or "Nao informada",
                    source="Website",
                    phone=data.user_phone or "",
                    role="Visitante do site",
                )
                
                if qual_data.get("score") in ("Quente", "Morno"):
                    deal_value = 10000 if qual_data["score"] == "Quente" else 5000
                    create_deal(
                        deal_name=f"{name} - Website",
                        company=data.company or "Nao informada",
                        contact=name,
                        value=deal_value,
                        stage="Prospeccao",
                    )
                
                schedule_activity(
                    activity_name=f"Follow-up com {name}",
                    activity_type="Email",
                    lead=name,
                    due_date=datetime.now().strftime("%Y-%m-%d"),
                    notes=f"Lead veio do widget. Score: {qual_data.get('score')}.",
                )
                
                session["lead_created"] = True
            except Exception as e:
                # Se falhar CRM, continua a conversa normalmente
                print(f"CRM error (non-fatal): {e}")
                session["lead_created"] = True  # Marca como criado para nao tentar de novo
    
    # Adiciona mensagem do usuario
    session["messages"].append({
        "role": "user",
        "content": data.message,
        "timestamp": datetime.now().isoformat(),
    })
    
    # Gera resposta do SDR Agent
    # Constroi contexto da conversa
    conversation_context = "\n".join([
        f"{'Usuario' if m['role'] == 'user' else 'SDR'}: {m['content']}"
        for m in session["messages"][-6:]  # Ultimas 6 mensagens
    ])
    
    prompt = f"""Voce e um SDR humanizado da Konig Systems. Responda ao usuario de forma natural e conversacional.

Contexto da conversa:
{conversation_context}

REGRAS:
- Maximo 150 palavras
- Use linguagem natural, nunca robotica
- Faca UMA pergunta no final para manter a conversa
- Se o usuario demonstrou interesse, sugira uma conversa ou demo
- Se o usuario so esta explorando, ajude e deixe a porta aberta
- Evite jargoes corporativos
- Seja direto mas caloroso"""

    response = sdr.agent.run(prompt)
    reply = response.content
    
    # Adiciona resposta do SDR
    session["messages"].append({
        "role": "assistant",
        "content": reply,
        "timestamp": datetime.now().isoformat(),
    })
    
    return {
        "session_id": session_id,
        "reply": reply,
        "lead_created": session["lead_created"],
    }


@app.post("/api/lead")
async def create_lead(data: LeadData):
    """Cria lead diretamente no CRM."""
    name = data.name or data.email.split("@")[0]
    
    result = create_lead_in_crm(
        name=name,
        email=data.email,
        company=data.company or "Nao informada",
        source="Website",
        phone=data.phone or "",
        role="Visitante do site",
    )
    
    # Qualifica
    qual_result = qualify_lead(
        name=name,
        company=data.company or "Nao informada",
        role="Visitante do site",
        initial_message=data.message or "",
        source="Website",
    )
    qual_data = json.loads(qual_result)
    
    if qual_data["score"] in ("Quente", "Morno"):
        deal_value = 10000 if qual_data["score"] == "Quente" else 5000
        create_deal(
            deal_name=f"{name} - Website",
            company=data.company or "Nao informada",
            contact=name,
            value=deal_value,
            stage="Prospeccao",
        )
    
    return {
        "success": True,
        "lead_name": name,
        "score": qual_data["score"],
        "message": result,
    }


@app.get("/api/widget.js", response_class=PlainTextResponse)
async def get_widget_script():
    """Retorna o script do widget para injetar no site.
    
    Igual ao GPT Maker - 1 linha de script e o widget aparece.
    """
    widget_js_path = Path(__file__).parent / "widget.js"
    if widget_js_path.exists():
        return widget_js_path.read_text(encoding="utf-8")
    return "// Widget script not found"


@app.get("/health")
async def health():
    """Health check."""
    return {"status": "ok", "sessions": len(sessions)}


if __name__ == "__main__":
    import uvicorn
    print("=" * 60)
    print("KONIG SDR WIDGET BACKEND")
    print("=" * 60)
    print()
    print("Iniciando servidor...")
    print("Widget disponivel em: http://localhost:8000")
    print()
    print("Para usar no seu site, adicione:")
    print('<script src="http://localhost:8000/api/widget.js"></script>')
    print()
    uvicorn.run(app, host="0.0.0.0", port=8000)
