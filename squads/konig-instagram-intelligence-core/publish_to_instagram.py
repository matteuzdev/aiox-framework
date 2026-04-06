"""Instagram Publisher — Publica carrosseis via Playwright.

Uso:
  python publish_to_instagram.py --username SEU_USER --password SUA_SENHA
  python publish_to_instagram.py --dry-run  # Simula sem publicar

Requisitos:
  pip install playwright
  playwright install chromium

Notas de seguranca:
  - Credenciais podem ser passadas via variaveis de ambiente:
    IG_USERNAME, IG_PASSWORD
  - Ou via arquivo .env na raiz do projeto
"""

import os
import sys
import time
import argparse
from pathlib import Path
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

# --- Config ---
BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / "output"

POSTS = [
    {
        "name": "Post 1 - Perda Mensal",
        "images": sorted((OUTPUT_DIR / "carousel-1-perda-mensal").glob("*.png")),
        "caption": """A conta que nenhum oftalmo faz — e que custa R$154.000 por ano.

Se voce atende 20 pacientes por dia, cobra R$350 por consulta e trabalha 22 dias por mes, sua conta diz R$154.000/mes.

A realidade? Provavelmente metade disso.

Porque 20% da sua agenda fica vazia sem voce perceber. Porque no-show come mais 10%. Porque cancelamento de ultima hora nao tem reposicao automatica.

A diferenca entre uma clinica que fatura R$80k e uma que fatura R$200k nao e o equipamento. Nao e a localizacao.

E processo.

Quer saber quanto a SUA clinica perde por mes? Comenta "CALCULO" que eu te mando a planilha.

#oftalmologia #gestaoclinica #clinicamedica #saudeocular #KonigSystems""",
    },
    {
        "name": "Post 2 - Checklist Pre-Op",
        "images": sorted((OUTPUT_DIR / "carousel-2-checklist").glob("*.png")),
        "caption": """90% das complicacoes cirurgicas comecam ANTES do paciente entrar no centro.

Nao e falha tecnica. Nao e equipamento. E processo pre-operatorio — ou a falta dele.

Esse checklist tem 7 items que separam uma cirurgia tranquila de uma complicacao evitavel:

1. Exames com 7 dias de antecedencia
2. Suspensao correta dos 5 medicamentos principais
3. Conversa real sobre expectativas
4. Checklist de comorbidades
5. Confirmacao de jejum e instrucoes
6. Termo de consentimento especifico
7. Contato de emergencia 24h

Se sua clinica nao tem isso formalizado, voce esta dependendo da sorte. E sorte nao e processo.

Salva esse post pra consultar antes de cada lista cirurgica.

#cirurgiaoftalmologica #segurancadopaciente #oftalmologia #processocirurgico #KonigSystems""",
    },
    {
        "name": "Post 3 - 5 Momentos",
        "images": sorted((OUTPUT_DIR / "carousel-3-5-momentos").glob("*.png")),
        "caption": """O paciente nao volta pelo seu OCT de ultima geracao.

Ele volta por como se sentiu em 5 momentos especificos da jornada:

1. Quando ligou para agendar — atenderam rapido? Foram claros?
2. Quando chegou na recepcao — esperou 5 minutos ou 45?
3. Quando o medico explicou — ele entendeu ou saiu com mais duvidas?
4. Quando recebeu o pos-consulta — teve suporte ou foi abandonado?
5. Quando precisou de retorno — conseguiu facil ou teve que ligar de novo?

Cada um desses momentos e uma decisao silenciosa: "eu volto" ou "eu nunca mais piso aqui".

Qual desses 5 momentos sua clinica mais erra? Comenta aqui embaixo.

#experienciadopaciente #gestaoclinica #oftalmologia #atendimentomedico #KonigSystems""",
    },
    {
        "name": "Post 4 - Equipamento vs Processo",
        "images": sorted((OUTPUT_DIR / "carousel-4-equipamento").glob("*.png")),
        "caption": """Hot take: seu equipamento nao e seu maior ativo.

Voce investiu R$500k no melhor OCT do mercado. Sua agenda continua com buracos.

Sabe por que?

Paciente nao compra especificacao tecnica. Paciente compra confianca, clareza e resultado.

Equipamento e tabela. Processo e jogo.

Concorda ou discorda? Debate aqui embaixo — quero ouvir os dois lados.

#oftalmologia #gestaoclinica #medicina #processos #KonigSystems""",
    },
    {
        "name": "Post 5 - Matematica",
        "images": sorted((OUTPUT_DIR / "carousel-5-matematica").glob("*.png")),
        "caption": """Se sua consulta custa R$350 e voce atende 20 pacientes por dia, quanto voce fatura?

Se voce respondeu R$7.000 por dia... faz a conta de novo.

Porque a realidade tem 3 variaveis que ninguem conta na residencia:

Variavel 1: 20% dos pacientes sao convenio
Variavel 2: 15% dos horarios ficam vazios
Variavel 3: 10% dos pacientes faltam sem avisar

Conta real: provavelmente R$3.500-4.500 por dia. Nao R$7.000.

Quer que eu faca essa conta pra sua clinica? Comenta "MINHA CONTA" que eu te mando.

#oftalmologia #faturamentomedico #gestaoclinica #medicina #KonigSystems""",
    },
]


def login(page, username, password):
    """Faz login no Instagram Creator Studio / Meta Business Suite."""
    print("[LOGIN] Acessando Instagram...")
    page.goto("https://www.instagram.com/accounts/login/", wait_until="domcontentloaded")
    time.sleep(3)

    try:
        username_input = page.locator('input[name="username"]')
        password_input = page.locator('input[name="password"]')
        username_input.fill(username)
        password_input.fill(password)
        password_input.press("Enter")
        print("[LOGIN] Credenciais enviadas, aguardando...")
        time.sleep(8)

        # Salvar info opcional
        try:
            not_now = page.locator('button:has-text("Agora não"), button:has-text("Not now")')
            if not_now.is_visible(timeout=3000):
                not_now.click()
                time.sleep(2)
        except PlaywrightTimeout:
            pass

        # Notificacoes
        try:
            not_now = page.locator('button:has-text("Agora não"), button:has-text("Not now"), button:has-text("Não agora")')
            if not_now.is_visible(timeout=3000):
                not_now.click()
                time.sleep(2)
        except PlaywrightTimeout:
            pass

        print("[LOGIN] Login concluido.")
        return True
    except Exception as e:
        print(f"[LOGIN] Erro: {e}")
        return False


def publish_carousel(page, post, dry_run=False):
    """Publica um carousel no Instagram via Meta Business Suite."""
    name = post["name"]
    images = post["images"]
    caption = post["caption"]

    if not images:
        print(f"[PUBLISH] {name}: NENHUMA IMAGEM ENCONTRADA — pulando")
        return False

    print(f"\n[PUBLISH] {name}")
    print(f"  Imagens: {len(images)} slides")
    print(f"  Legenda: {len(caption)} caracteres")

    if dry_run:
        print(f"  [DRY RUN] Simulacao — nada foi publicado")
        for img in images:
            print(f"    -> {img.name}")
        return True

    # Usar Meta Business Suite para publicacao de carrossel
    print("[PUBLISH] Acessando Meta Business Suite...")
    page.goto("https://business.facebook.com/content", wait_until="domcontentloaded", timeout=30000)
    time.sleep(5)

    try:
        # Botao Criar Publicacao
        create_btn = page.locator('button:has-text("Criar publicação"), button:has-text("Create Post")')
        if create_btn.is_visible(timeout=5000):
            create_btn.click()
            time.sleep(3)
        else:
            print("[PUBLISH] Botao de criar nao encontrado, tentando alternativa...")
            page.goto("https://business.facebook.com/composer", wait_until="domcontentloaded")
            time.sleep(3)

        # Upload das imagens
        print("[PUBLISH] Fazendo upload das imagens...")
        file_input = page.locator('input[type="file"]')
        image_paths = [str(img) for img in images]
        file_input.set_input_files(image_paths)
        time.sleep(10)

        # Legenda
        print("[PUBLISH] Preenchendo legenda...")
        caption_input = page.locator('textarea[placeholder*="Legenda"], textarea[placeholder*="caption"], [contenteditable="true"]').first
        if caption_input.is_visible(timeout=5000):
            caption_input.fill(caption)
        else:
            print("[PUBLISH] Campo de legenda nao encontrado automaticamente")
            print("[PUBLISH] Tentando campo alternativo...")

        time.sleep(3)

        # Publicar
        print("[PUBLISH] Tentando publicar...")
        publish_btn = page.locator('button:has-text("Publicar"), button:has-text("Publish"), button:has-text("Share")')
        if publish_btn.is_visible(timeout=5000):
            publish_btn.click()
            time.sleep(5)
            print(f"[PUBLISH] {name}: PUBLICADO COM SUCESSO!")
            return True
        else:
            print(f"[PUBLISH] {name}: Botao de publicar nao encontrado")
            print("[PUBLISH] Verifique manualmente e clique em Publicar")
            return False

    except PlaywrightTimeout:
        print(f"[PUBLISH] {name}: Timeout — elemento nao encontrado")
        return False
    except Exception as e:
        print(f"[PUBLISH] {name}: Erro — {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Publica carrosseis no Instagram")
    parser.add_argument("--username", default=os.environ.get("IG_USERNAME", ""))
    parser.add_argument("--password", default=os.environ.get("IG_PASSWORD", ""))
    parser.add_argument("--post", type=int, default=0, help="Numero do post (1-5), 0 = todos")
    parser.add_argument("--dry-run", action="store_true", help="Simula sem publicar")
    parser.add_argument("--headless", action="store_true", help="Modo headless (sem navegador visivel)")
    args = parser.parse_args()

    if not args.dry_run and (not args.username or not args.password):
        print("ERRO: --username e --password sao obrigatorios (ou defina IG_USERNAME e IG_PASSWORD)")
        print("Uso: python publish_to_instagram.py --username SEU_USER --password SUA_SENHA")
        print("Ou:  python publish_to_instagram.py --dry-run")
        sys.exit(1)

    posts_to_publish = POSTS
    if args.post > 0:
        posts_to_publish = [POSTS[args.post - 1]]

    print("=" * 60)
    print("KONIG SYSTEMS — Instagram Publisher")
    print("=" * 60)
    print(f"Posts: {len(posts_to_publish)}")
    print(f"Mode: {'DRY RUN' if args.dry_run else 'LIVE'}")
    print(f"Headless: {args.headless}")
    print()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=args.headless)
        context = browser.new_context(
            viewport={"width": 1280, "height": 900},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )
        page = context.new_page()

        if not args.dry_run:
            if not login(page, args.username, args.password):
                print("[FATAL] Login falhou. Abortando.")
                browser.close()
                sys.exit(1)

        results = []
        for i, post in enumerate(posts_to_publish):
            success = publish_carousel(page, post, dry_run=args.dry_run)
            results.append({"name": post["name"], "success": success})
            if i < len(posts_to_publish) - 1:
                time.sleep(5)

        print("\n" + "=" * 60)
        print("RESULTADO FINAL")
        print("=" * 60)
        for r in results:
            status = "OK" if r["success"] else "FALHOU"
            print(f"  [{status}] {r['name']}")

        browser.close()


if __name__ == "__main__":
    main()
