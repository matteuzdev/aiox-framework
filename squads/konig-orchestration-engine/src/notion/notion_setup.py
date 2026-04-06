"""Konig Systems — Notion Integration.

Cria e gerencia o workspace de gestão de processos no Notion.
Cada execução de squad atualiza automaticamente o Notion.

Setup (uma vez so):
  1. Crie uma integracao em https://www.notion.so/my-integrations
  2. Copie o Internal Integration Token
  3. Crie uma pagina no Notion e compartilhe com a integracao
  4. Cole o token e page ID no .env

Uso:
  python notion_setup.py            # Cria estrutura inicial
  python notion_sync.py             # Sincroniza estado atual
  python notion_sync.py --run-id XXX  # Atualiza com run especifico
"""

import os
import sys
import json
import httpx
from pathlib import Path
from datetime import datetime

# --- Config ---
BASE_DIR = Path(__file__).parent.parent.parent
SQUADS_DIR = BASE_DIR.parent

NOTION_VERSION = "2022-06-28"


def get_token():
    """Pega o token do .env ou variavel de ambiente."""
    token = os.environ.get("NOTION_TOKEN")
    if not token:
        env_file = BASE_DIR / ".env"
        if env_file.exists():
            for line in env_file.read_text().splitlines():
                if line.startswith("NOTION_TOKEN="):
                    token = line.split("=", 1)[1].strip()
                    break

    if not token:
        print("ERRO: NOTION_TOKEN nao definido.")
        print("1. Crie integracao em https://www.notion.so/my-integrations")
        print("2. Copie o 'Internal Integration Token'")
        print("3. Defina: setx NOTION_TOKEN 'seu_token'")
        sys.exit(1)

    return token


def get_headers():
    """Retorna headers para a API do Notion."""
    return {
        "Authorization": f"Bearer {get_token()}",
        "Notion-Version": NOTION_VERSION,
        "Content-Type": "application/json",
    }


def get_root_page_id():
    """Pega o page ID do .env ou pergunta."""
    page_id = os.environ.get("NOTION_PAGE_ID")
    if not page_id:
        env_file = BASE_DIR / ".env"
        if env_file.exists():
            for line in env_file.read_text().splitlines():
                if line.startswith("NOTION_PAGE_ID="):
                    page_id = line.split("=", 1)[1].strip()
                    break

    if not page_id:
        print("NOTION_PAGE_ID nao definido.")
        page_id = input("Cole o ID da pagina pai do Notion: ").strip()
        if not page_id:
            print("Abortando.")
            sys.exit(1)

    # Limpa o page ID (remove hifens se necessario)
    page_id = page_id.replace("-", "")
    return page_id


def create_squads_database(parent_page_id):
    """Cria database de Squads."""
    print("[NOTION] Criando database de Squads...")

    url = "https://api.notion.com/v1/databases"
    payload = {
        "parent": {"type": "page_id", "page_id": parent_page_id},
        "title": [{"text": {"content": "Konig Systems — Squads"}}],
        "description": [{"text": {"content": "Status e capacidade de cada squad da Konig Systems"}}],
        "properties": {
            "Squad": {"title": {}},
            "Status": {
                "select": {
                    "options": [
                        {"name": "Pronto", "color": "green"},
                        {"name": "Definicao OK", "color": "yellow"},
                        {"name": "Incompleto", "color": "red"},
                        {"name": "Em Execucao", "color": "blue"},
                    ]
                }
            },
            "Agentes": {"number": {}},
            "Tasks": {"number": {}},
            "Workflows": {"number": {}},
            "Runs Completados": {"number": {}},
            "Ultima Execucao": {"date": {}},
            "Confianca": {
                "select": {
                    "options": [
                        {"name": "Alta", "color": "green"},
                        {"name": "Media", "color": "yellow"},
                        {"name": "Baixa", "color": "red"},
                    ]
                }
            },
            "Entregaveis": {"rich_text": {}},
        },
    }

    response = httpx.post(url, headers=get_headers(), json=payload)
    if response.status_code == 200:
        db_id = response.json()["id"]
        print(f"[NOTION] Database de Squads criada: {db_id}")
        return db_id
    else:
        print(f"[NOTION] Erro ao criar database de Squads: {response.status_code} - {response.text}")
        return None


def create_runs_database(parent_page_id):
    """Cria database de Execucoes/Runs."""
    print("[NOTION] Criando database de Execucoes...")

    # Lista squads para options
    squad_options = []
    if SQUADS_DIR.exists():
        for squad_dir in sorted(SQUADS_DIR.iterdir()):
            if squad_dir.is_dir() and not squad_dir.name.startswith(".") and squad_dir.name not in ("pixel-agents", "konig-orchestration-engine", "agent-ajuda"):
                squad_options.append({"name": squad_dir.name, "color": "blue"})

    url = "https://api.notion.com/v1/databases"
    payload = {
        "parent": {"type": "page_id", "page_id": parent_page_id},
        "title": [{"text": {"content": "Konig Systems — Execucoes"}}],
        "description": [{"text": {"content": "Historico de execucoes dos squads"}}],
        "properties": {
            "Run ID": {"title": {}},
            "Squad": {
                "select": {
                    "options": squad_options
                }
            },
            "Workflow": {"rich_text": {}},
            "Status": {
                "select": {
                    "options": [
                        {"name": "Sucesso", "color": "green"},
                        {"name": "Falhou", "color": "red"},
                        {"name": "Em Andamento", "color": "yellow"},
                        {"name": "Pausado", "color": "gray"},
                    ]
                }
            },
            "Inicio": {"date": {}},
            "Termino": {"date": {}},
            "Duracao": {"rich_text": {}},
            "Artifacts": {"number": {}},
            "Tasks Executadas": {"number": {}},
            "Tasks com Sucesso": {"number": {}},
            "Erros": {"rich_text": {}},
        },
    }

    response = httpx.post(url, headers=get_headers(), json=payload)
    if response.status_code == 200:
        db_id = response.json()["id"]
        print(f"[NOTION] Database de Execucoes criada: {db_id}")
        return db_id
    else:
        print(f"[NOTION] Erro ao criar database de Execucoes: {response.status_code} - {response.text}")
        return None


def create_dashboard_page(parent_page_id, squads_db_id, runs_db_id):
    """Cria pagina de Dashboard com instrucoes."""
    print("[NOTION] Criando pagina de Dashboard...")

    url = "https://api.notion.com/v1/pages"
    payload = {
        "parent": {"type": "page_id", "page_id": parent_page_id},
        "properties": {"title": {"title": [{"text": {"content": "Konig Systems — Dashboard"}}]}},
        "children": [
            {"object": "block", "type": "heading_1", "heading_1": {"rich_text": [{"text": {"content": "Konig Systems — Painel de Controle"}}]}},
            {"object": "block", "type": "paragraph", "paragraph": {"rich_text": [{"text": {"content": "Visao geral da empresa de agentes. Os databases abaixo atualizam automaticamente quando os squads executam."}}]}},
            {"object": "block", "type": "heading_2", "heading_2": {"rich_text": [{"text": {"content": "Como Funciona"}}]}},
            {"object": "block", "type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"text": {"content": "Cada squad roda via CLI: konig run workflow <workflow> --squad <squad>"}}]}},
            {"object": "block", "type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"text": {"content": "Ao finalizar, o run e registrado automaticamente no Notion"}}]}},
            {"object": "block", "type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"text": {"content": "Voce ve tudo aqui sem precisar abrir o terminal"}}]}},
            {"object": "block", "type": "divider", "divider": {}},
            {"object": "block", "type": "heading_2", "heading_2": {"rich_text": [{"text": {"content": "Squads Prontos"}}]}},
            {"object": "block", "type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"text": {"content": "konig-instagram-intelligence-core — 6 agents, 6 tasks, pipeline completo, 3 runs provados"}}]}},
            {"object": "block", "type": "heading_2", "heading_2": {"rich_text": [{"text": {"content": "Squads em Definicao"}}]}},
            {"object": "block", "type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"text": {"content": "company-strategic-core, konig-athenaeum-core, konig-experience-core, konig-growth-core"}}]}},
            {"object": "block", "type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"text": {"content": "konig-delivery-factory-core, konig-orchestration-core, konig-context-core, konig-engineering-core"}}]}},
            {"object": "block", "type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"text": {"content": "konig-planning-core, konig-product-core, konig-research-intel-core, konig-revenue-core"}}]}},
            {"object": "block", "type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"text": {"content": "konig-governance-core, konig-ops-core"}}]}},
        ],
    }

    response = httpx.post(url, headers=get_headers(), json=payload)
    if response.status_code == 200:
        page_id = response.json()["id"]
        print(f"[NOTION] Dashboard criado: {page_id}")
        return page_id
    else:
        print(f"[NOTION] Erro ao criar Dashboard: {response.status_code} - {response.text}")
        return None


def sync_squads_to_notion(database_id):
    """Popula database de Squads com dados reais."""
    print("[NOTION] Sincronizando squads...")

    squads_data = []
    for squad_dir in sorted(SQUADS_DIR.iterdir()):
        if not squad_dir.is_dir() or squad_dir.name.startswith("."):
            continue
        if squad_dir.name in ("pixel-agents", "konig-orchestration-engine", "agent-ajuda"):
            continue

        squad_yaml = squad_dir / "squad.yaml"
        if not squad_yaml.exists():
            continue

        try:
            import yaml
            manifest = yaml.safe_load(squad_yaml.read_text())
        except ImportError:
            print("  [AVISO] PyYAML nao instalado. Pulando squad.")
            continue

        agents_dir = squad_dir / "agents"
        tasks_dir = squad_dir / "tasks"
        workflows_dir = squad_dir / "workflows"
        runs_dir = BASE_DIR.parent / "runs" / squad_dir.name

        agent_count = len(list(agents_dir.glob("*.md"))) if agents_dir.exists() else 0
        task_count = len(list(tasks_dir.glob("*.md"))) if tasks_dir.exists() else 0
        workflow_count = len(list(workflows_dir.glob("*.md"))) if workflows_dir.exists() else 0

        # Contar runs
        run_count = 0
        last_run = None
        if runs_dir.exists():
            runs = list(runs_dir.glob("*/run-state.json"))
            run_count = len(runs)
            if runs:
                latest = max(runs, key=lambda r: r.stat().st_mtime)
                run_data = json.loads(latest.read_text())
                last_run = run_data.get("completedAt")

        # Determinar status
        components = manifest.get("components", {})
        has_checklists = len(components.get("checklists", [])) > 0
        has_config = (squad_dir / "config").exists()

        if run_count > 0 and workflow_count > 0 and has_checklists:
            status = "Pronto"
            confianca = "Alta"
        elif agent_count > 0 and task_count > 0 and has_checklists and has_config:
            status = "Definicao OK"
            confianca = "Media"
        else:
            status = "Incompleto"
            confianca = "Baixa"

        # Entregaveis
        entregaveis = []
        if task_count > 0:
            for task_file in tasks_dir.glob("*.md"):
                try:
                    content = task_file.read_text()
                    if "---" in content:
                        frontmatter = content.split("---")[1]
                        task_data = yaml.safe_load(frontmatter)
                        if task_data and "Saida" in task_data:
                            entregaveis.append(task_data["Saida"].strip()[:80])
                except Exception:
                    pass

        squads_data.append({
            "name": squad_dir.name,
            "status": status,
            "agents": agent_count,
            "tasks": task_count,
            "workflows": workflow_count,
            "runs": run_count,
            "last_run": last_run,
            "confianca": confianca,
            "entregaveis": "\n".join(entregaveis[:3]) if entregaveis else "Nenhum entregavel definido",
        })

    # Criar paginas no database
    url = "https://api.notion.com/v1/pages"
    
    for squad in squads_data:
        # Simplifica entregaveis para evitar problemas de encoding
        entregaveis_text = squad["entregaveis"][:500].replace("\n", " ")
        
        payload = {
            "parent": {"type": "database_id", "database_id": database_id},
            "properties": {
                "Squad": {"title": [{"text": {"content": squad["name"]}}]},
                "Status": {"select": {"name": squad["status"]}},
                "Agentes": {"number": squad["agents"]},
                "Tasks": {"number": squad["tasks"]},
                "Workflows": {"number": squad["workflows"]},
                "Runs Completados": {"number": squad["runs"]},
                "Ultima Execucao": {"date": {"start": squad["last_run"][:10]}} if squad["last_run"] else None,
                "Confianca": {"select": {"name": squad["confianca"]}},
                "Entregaveis": {"rich_text": [{"text": {"content": entregaveis_text}}]},
            },
        }

        response = httpx.post(url, headers=get_headers(), json=payload)
        if response.status_code == 200:
            print(f"  [OK] {squad['name']} — {squad['status']}")
        else:
            print(f"  [ERRO] {squad['name']}: {response.status_code} - {response.text[:200]}")

    print(f"[NOTION] {len(squads_data)} squads sincronizados.")


def sync_runs_to_notion(database_id):
    """Popula database de Runs com dados reais."""
    print("[NOTION] Sincronizando execucoes...")

    runs_dir = BASE_DIR.parent / "runs"
    if not runs_dir.exists():
        print("[NOTION] Diretorio de runs nao encontrado.")
        return

    run_count = 0
    url = "https://api.notion.com/v1/pages"
    for squad_dir in sorted(runs_dir.iterdir()):
        if not squad_dir.is_dir():
            continue

        for run_dir in sorted(squad_dir.iterdir()):
            run_state_file = run_dir / "run-state.json"
            if not run_state_file.exists():
                continue

            try:
                run_data = json.loads(run_state_file.read_text())
                tasks = run_data.get("tasks", [])
                tasks_success = sum(1 for t in tasks if t.get("status") == "completed")

                # Calcular duracao
                duracao = ""
                if run_data.get("startedAt") and run_data.get("completedAt"):
                    start = datetime.fromisoformat(run_data["startedAt"].replace("Z", "+00:00"))
                    end = datetime.fromisoformat(run_data["completedAt"].replace("Z", "+00:00"))
                    diff = end - start
                    minutos = int(diff.total_seconds() / 60)
                    segundos = int(diff.total_seconds() % 60)
                    duracao = f"{minutos}m {segundos}s"

                # Contar artifacts
                artifacts = len([f for f in run_dir.iterdir() if f.is_file() and f.name != "run-state.json"])

                # Erros
                erros = []
                for t in tasks:
                    if t.get("error"):
                        erros.append(f"{t['task']}: {t['error'][:100]}")

                payload = {
                    "parent": {"type": "database_id", "database_id": database_id},
                    "properties": {
                        "Run ID": {"title": [{"text": {"content": run_data.get("id", run_dir.name)}}]},
                        "Squad": {"select": {"name": squad_dir.name}},
                        "Workflow": {"rich_text": [{"text": {"content": run_data.get("workflow", "N/A")}}]},
                        "Status": {"select": {"name": "Sucesso" if run_data.get("status") == "completed" else "Falhou"}},
                        "Inicio": {"date": {"start": run_data.get("startedAt", "")[:10]}},
                        "Termino": {"date": {"start": run_data.get("completedAt", "")[:10]}} if run_data.get("completedAt") else None,
                        "Duracao": {"rich_text": [{"text": {"content": duracao}}]},
                        "Artifacts": {"number": artifacts},
                        "Tasks Executadas": {"number": len(tasks)},
                        "Tasks com Sucesso": {"number": tasks_success},
                        "Erros": {"rich_text": [{"text": {"content": "\n".join(erros)[:2000]}}]},
                    },
                }

                response = httpx.post(url, headers=get_headers(), json=payload)
                if response.status_code == 200:
                    run_count += 1
                    print(f"  [OK] {run_data.get('id', run_dir.name)} - {run_data.get('status', 'unknown')}")
                else:
                    print(f"  [ERRO] {run_dir.name}: {response.status_code} - {response.text[:200]}")

            except Exception as e:
                print(f"  [ERRO] {run_dir.name}: {e}")

    print(f"[NOTION] {run_count} execucoes sincronizadas.")


def update_run_on_complete(run_data):
    """Atualiza Notion quando um run e concluido (chamado pelo task-runner)."""
    config_file = BASE_DIR / ".notion-config.json"
    if not config_file.exists():
        print("[NOTION] Config do Notion nao encontrada. Rode --setup primeiro.")
        return False

    config = json.loads(config_file.read_text())
    runs_db_id = config.get("runs_database_id")
    if not runs_db_id:
        print("[NOTION] runs_database_id nao encontrado na config.")
        return False

    try:
        tasks = run_data.get("tasks", [])
        tasks_success = sum(1 for t in tasks if t.get("status") == "completed")

        duracao = ""
        if run_data.get("startedAt") and run_data.get("completedAt"):
            start = datetime.fromisoformat(run_data["startedAt"].replace("Z", "+00:00"))
            end = datetime.fromisoformat(run_data["completedAt"].replace("Z", "+00:00"))
            diff = end - start
            minutos = int(diff.total_seconds() / 60)
            segundos = int(diff.total_seconds() % 60)
            duracao = f"{minutos}m {segundos}s"

        erros = []
        for t in tasks:
            if t.get("error"):
                erros.append(f"{t['task']}: {t['error'][:100]}")

        url = "https://api.notion.com/v1/pages"
        payload = {
            "parent": {"type": "database_id", "database_id": runs_db_id},
            "properties": {
                "Run ID": {"title": [{"text": {"content": run_data.get("id", "unknown")}}]},
                "Squad": {"select": {"name": run_data.get("squad", "unknown")}},
                "Workflow": {"rich_text": [{"text": {"content": run_data.get("workflow", "N/A")}}]},
                "Status": {"select": {"name": "Sucesso" if run_data.get("status") == "completed" else "Falhou"}},
                "Inicio": {"date": {"start": run_data.get("startedAt", "")[:10]}},
                "Termino": {"date": {"start": run_data.get("completedAt", "")[:10]}} if run_data.get("completedAt") else None,
                "Duracao": {"rich_text": [{"text": {"content": duracao}}]},
                "Tasks Executadas": {"number": len(tasks)},
                "Tasks com Sucesso": {"number": tasks_success},
                "Erros": {"rich_text": [{"text": {"content": "\n".join(erros)[:2000]}}]},
            },
        }

        response = httpx.post(url, headers=get_headers(), json=payload)
        if response.status_code == 200:
            print(f"[NOTION] Run registrado: {run_data.get('id', 'unknown')}")
            return True
        else:
            print(f"[NOTION] Erro ao registrar run: {response.status_code} - {response.text}")
            return False

    except Exception as e:
        print(f"[NOTION] Erro ao registrar run: {e}")
        return False


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Konig Systems — Notion Integration")
    parser.add_argument("--setup", action="store_true", help="Cria estrutura inicial")
    parser.add_argument("--sync", action="store_true", help="Sincroniza dados atuais")
    args = parser.parse_args()

    if not args.setup and not args.sync:
        print("Uso:")
        print("  python notion_setup.py --setup   # Cria estrutura inicial")
        print("  python notion_setup.py --sync     # Sincroniza dados atuais")
        return

    parent_page_id = get_root_page_id()

    if args.setup:
        print("=" * 60)
        print("KONIG SYSTEMS — Notion Setup")
        print("=" * 60)
        print()

        squads_db_id = create_squads_database(parent_page_id)
        runs_db_id = create_runs_database(parent_page_id)
        dashboard_id = create_dashboard_page(parent_page_id, squads_db_id, runs_db_id)

        # Salva IDs para uso futuro
        config = {
            "squads_database_id": squads_db_id,
            "runs_database_id": runs_db_id,
            "dashboard_page_id": dashboard_id,
        }
        config_file = BASE_DIR / ".notion-config.json"
        config_file.write_text(json.dumps(config, indent=2))
        print(f"\n[NOTION] Config salva em {config_file}")

        # Salva no .env
        env_file = BASE_DIR / ".env"
        env_content = env_file.read_text() if env_file.exists() else ""
        if "NOTION_SQUADS_DB" not in env_content and squads_db_id:
            with open(env_file, "a") as f:
                f.write(f"\nNOTION_SQUADS_DB={squads_db_id}\n")
                f.write(f"NOTION_RUNS_DB={runs_db_id}\n")
            print(f"[NOTION] Database IDs adicionados ao .env")

    if args.sync:
        print("=" * 60)
        print("KONIG SYSTEMS — Notion Sync")
        print("=" * 60)
        print()

        # Carrega config
        config_file = BASE_DIR / ".notion-config.json"
        if config_file.exists():
            config = json.loads(config_file.read_text())
            squads_db_id = config.get("squads_database_id")
            runs_db_id = config.get("runs_database_id")

            if squads_db_id:
                sync_squads_to_notion(squads_db_id)
            if runs_db_id:
                sync_runs_to_notion(runs_db_id)
        else:
            print("[ERRO] Config do Notion nao encontrada. Rode --setup primeiro.")


if __name__ == "__main__":
    main()
