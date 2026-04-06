"""Gerador de carrosseis com Nano Banana 2 via Gemini API (OAuth).

Usa o SDK google-genai com autenticacao OAuth do seu plano Gemini.
Sem custo extra — usa sua cota existente do Gemini.

Setup OAuth (uma vez so):
  1. Rode: python setup_gemini_oauth.py
  2. Faca login com sua conta Google (a mesma do seu plano Gemini)
  3. Autorize o acesso
  4. O token e salvo em ~/.config/generative-ai/

Uso:
  python generate_carousels_gemini.py
  python generate_carousels_gemini.py --post 1  # So carousel 1
"""

import os
import sys
import time
import json
import urllib.request
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import textwrap

try:
    from google import genai
    from google.genai import types
except ImportError:
    print("ERRO: google-genai nao instalado. Rode: pip install google-genai")
    sys.exit(1)

# --- Config ---
BASE_DIR = Path(__file__).parent
OUTPUT_BASE = BASE_DIR / "output"

# Cores Konig
BG_DARK = "#0a0f0d"
ACCENT = "#0a4b41"
ACCENT_LIGHT = "#1a7b6b"
TEXT_WHITE = "#f0ece4"
MUTED = "#5f6a70"
GOLD = "#9e6731"

SLIDE_SIZE = 1080

# --- Prompts visuais para cada slide ---
CAROUSEL_PROMPTS = {
    1: {
        "name": "Perda Mensal",
        "slides": [
            {
                "text": "Sua clinica de oftalmo\nperde R$15-40k por mes.",
                "visual": "Empty modern ophthalmology clinic waiting room, warm ambient lighting, photorealistic, cinematic, moody atmosphere, professional medical office, shallow depth of field, dark tones, editorial photography",
            },
            {
                "text": "E nao e com equipamento.\nNao e com equipe.",
                "visual": "Close-up of expensive ophthalmology OCT machine in dark room, dramatic lighting, photorealistic, cinematic composition, shallow depth of field, editorial photography",
            },
            {
                "text": "E com agenda vazia\nque voce nem percebe.",
                "visual": "Empty appointment calendar on a desk, soft morning light through window, photorealistic, minimal composition, melancholic mood, professional photography, dark tones",
            },
            {
                "text": "20%",
                "subtext": "dos horarios ficam sem\npreenchimento todo mes",
                "visual": "Abstract geometric pattern with gaps and empty spaces, dark minimalist design, subtle green tones, modern corporate art, photorealistic texture, editorial photography",
            },
            {
                "text": "Cada vaga vazia = R$350\nque nao volta.",
                "visual": "Single empty chair in a modern medical office, dramatic spotlight, photorealistic, cinematic, dark moody atmosphere, professional photography, editorial style",
            },
            {
                "text": "R$154k",
                "subtext": "perdidos por ano\nem horarios nao preenchidos",
                "visual": "Stack of money fading into darkness, dramatic lighting, photorealistic, cinematic composition, dark tones with subtle green accent, editorial photography",
            },
            {
                "text": "Isso sem contar no-show,\ncancelamento e retorno\nnao agendado.",
                "visual": "Blurred phone screen showing missed calls and cancelled appointments, dark background, photorealistic, shallow depth of field, moody lighting, editorial photography",
            },
            {
                "text": "Quer saber quanto a SUA\nclinica perde?",
                "cta": "Comenta CALCULO",
                "visual": "Professional ophthalmologist looking directly at camera, confident expression, modern clinic background, cinematic portrait lighting, photorealistic, dark tones with green accent",
            },
        ],
    },
    2: {
        "name": "Checklist Pre-Op",
        "slides": [
            {
                "text": "90% das complicacoes\ncomecam ANTES da cirurgia.",
                "visual": "Operating room through glass door, dramatic lighting, sterile environment, photorealistic, cinematic, medical photography, dark moody atmosphere, editorial style",
            },
            {
                "text": "Nao e no centro cirurgico.\nE na consulta.",
                "visual": "Doctor consulting with patient in modern office, warm lighting, photorealistic, professional medical photography, shallow depth of field, editorial photography",
            },
            {
                "text": "CHECKLIST",
                "subtext": "Pre-Operatorio",
                "is_checklist_header": True,
                "visual": "Clean medical clipboard with checklist, modern desk, natural light, photorealistic, minimal composition, professional photography, editorial style",
            },
            {
                "text": "ITEMS 1-2",
                "subtext": "Exames + Medicamentos",
                "is_checklist_body": True,
                "checklist_items": [
                    "Exames completos com 7 dias de antecedencia",
                    "Suspensao correta dos 5 medicamentos principais",
                ],
                "visual": "Medical test results and prescription bottles arranged neatly, clean surface, natural light, photorealistic, professional photography",
            },
            {
                "text": "ITEMS 3-4",
                "subtext": "Expectativas + Comorbidades",
                "is_checklist_body": True,
                "checklist_items": [
                    "Conversa sobre expectativas reais do paciente",
                    "Checklist de comorbidades (diabetes, hipertensao)",
                ],
                "visual": "Doctor and patient in conversation, modern consultation room, warm lighting, photorealistic, professional medical photography",
            },
            {
                "text": "ITEMS 5-7",
                "subtext": "Jejum + Termo + Emergencia",
                "is_checklist_body": True,
                "checklist_items": [
                    "Confirmacao de jejum e instrucoes pre-cirurgia",
                    "Termo de consentimento especifico (nao generico)",
                    "Contato de emergencia disponivel 24h",
                ],
                "visual": "Signed medical consent form on desk with pen, clean modern office, natural light, photorealistic, professional photography",
            },
            {
                "text": "Se sua clinica nao tem isso\nformalizado, voce esta\ndependendo da sorte.",
                "visual": "Four leaf clover on medical desk next to surgical instruments, dramatic lighting, photorealistic, cinematic, dark moody atmosphere, editorial photography",
            },
            {
                "text": "E sorte nao e processo.",
                "visual": "Organized surgical process flow chart on modern wall, clean clinical environment, photorealistic, professional medical photography, bright and clean",
            },
            {
                "text": "Checklist que todo oftalmo\ndeveria ter na gaveta.",
                "cta": "Salva pra consultar antes",
                "visual": "Open desk drawer with organized medical checklists and documents, clean modern office, natural light, photorealistic, professional photography",
            },
            {
                "text": "KONIG SYSTEMS\nAutoridade Operacional",
                "cta": "Siga para mais",
                "visual": "Modern corporate office building at dusk, dramatic sky, photorealistic, cinematic, professional architecture photography, dark tones with green accent",
            },
        ],
    },
    3: {
        "name": "5 Momentos",
        "slides": [
            {
                "text": "O paciente nao volta\npelo equipamento.",
                "visual": "Expensive ophthalmology equipment in dark room, dramatic single spotlight, photorealistic, cinematic, shallow depth of field, moody atmosphere, editorial photography",
            },
            {
                "text": "Ele volta por como se sentiu\nnesses 5 momentos:",
                "visual": "Patient walking into modern clinic reception, warm welcoming light, photorealistic, professional photography, shallow depth of field, editorial style",
            },
            {
                "text": "1. Quando ligou para agendar",
                "subtext": "(atendeu rapido? foi claro?)",
                "visual": "Modern phone on reception desk, soft warm light, clean clinic environment, photorealistic, professional photography, minimal composition",
            },
            {
                "text": "2. Quando chegou na recepcao",
                "subtext": "(esperou 5 min ou 45?)",
                "visual": "Modern clinic waiting room with comfortable seating, warm ambient lighting, photorealistic, architectural photography, clean and inviting",
            },
            {
                "text": "3. Quando o medico explicou",
                "subtext": "(entendeu ou ficou com duvida?)",
                "visual": "Doctor explaining eye examination results to patient, modern consultation room, warm natural light, photorealistic, professional medical photography",
            },
            {
                "text": "4. Quando recebeu o pos-consulta",
                "subtext": "(teve suporte ou foi abandonado?)",
                "visual": "Patient receiving care instructions from nurse, modern clinic, warm lighting, photorealistic, professional medical photography, caring atmosphere",
            },
            {
                "text": "Qual desses momentos\nsua clinica mais erra?",
                "cta": "Comenta aqui",
                "visual": "Empty clinic hallway with warm light at the end, photorealistic, cinematic, metaphorical composition, professional photography, dark tones with green accent",
            },
        ],
    },
    4: {
        "name": "Equipamento vs Processo",
        "slides": [
            {
                "text": "Voce comprou o melhor\nOCT do mercado.",
                "visual": "Latest generation OCT ophthalmology machine, sleek modern design, dramatic studio lighting, photorealistic, product photography, dark background, editorial style",
            },
            {
                "text": "E sua agenda\ncontinua vazia.",
                "visual": "Empty appointment book on modern desk, morning light, photorealistic, minimal composition, melancholic mood, professional photography",
            },
            {
                "text": "Sabe por que?\nPaciente nao compra equipamento.",
                "visual": "Patient's perspective view of clinic entrance, welcoming atmosphere, photorealistic, professional photography, warm tones, shallow depth of field",
            },
            {
                "text": "Paciente compra confianca,\nclareza e resultado.",
                "visual": "Happy patient leaving modern clinic, confident smile, natural light, photorealistic, professional photography, warm and positive atmosphere",
            },
            {
                "text": "Processo > Equipamento",
                "visual": "Split composition: expensive equipment on one side fading to shadow, organized process flowchart on the other side in light, photorealistic, conceptual photography",
            },
            {
                "text": "Concorda ou discorda?",
                "cta": "Debate aqui embaixo",
                "visual": "Modern debate/conversation setting, two chairs facing each other, warm lighting, photorealistic, professional photography, inviting atmosphere",
            },
        ],
    },
    5: {
        "name": "Matematica",
        "slides": [
            {
                "text": "Consulta = R$350.\n20 pacientes/dia.\nQuanto voce fatura?",
                "visual": "Calculator on modern doctor's desk next to appointment book, warm desk lamp light, photorealistic, professional photography, dark moody atmosphere",
            },
            {
                "text": "Se respondeu R$7.000/dia...\nerrou.",
                "visual": "Red X mark on financial spreadsheet, dramatic lighting, photorealistic, close-up, shallow depth of field, dark tones, editorial photography",
            },
            {
                "text": "20% dos pacientes\nnao pagam particular.",
                "visual": "Health insurance card next to cash on desk, dramatic lighting, photorealistic, professional photography, dark moody atmosphere",
            },
            {
                "text": "15% dos horarios\nficam vazios.",
                "visual": "Calendar with highlighted empty slots, modern desk, natural light, photorealistic, minimal composition, professional photography",
            },
            {
                "text": "10% dos pacientes\nfaltam sem avisar.",
                "visual": "Empty patient chair in examination room, single spotlight, photorealistic, cinematic, dark moody atmosphere, professional medical photography",
            },
            {
                "text": "R$3.5-4.5k",
                "subtext": "por dia e o numero real.\nNao R$7.000.",
                "visual": "Financial report with highlighted numbers, modern desk, dramatic lighting, photorealistic, professional photography, dark tones with green accent",
            },
            {
                "text": "Quer que eu faca essa conta\npra sua clinica?",
                "cta": "Comenta MINHA CONTA",
                "visual": "Professional ophthalmologist with tablet showing financial dashboard, modern office, warm lighting, photorealistic, professional photography, confident expression",
            },
        ],
    },
}


def get_client():
    """Cria cliente Gemini com OAuth (usa credenciais salvas localmente)."""
    try:
        client = genai.Client()
        # Testa conexao
        client.models.list()
        return client
    except Exception as e:
        print(f"ERRO ao conectar com Gemini: {e}")
        print()
        print("Voce precisa configurar o OAuth do Gemini primeiro.")
        print("Rode: python setup_gemini_oauth.py")
        print()
        print("Ou defina GOOGLE_API_KEY como alternativa:")
        print("  setx GOOGLE_API_KEY sua_chave")
        return None


def get_font(size, bold=False):
    """Carrega fonte do sistema com fallback."""
    font_paths = [
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/calibribd.ttf" if bold else "C:/Windows/Fonts/calibri.ttf",
        "C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf",
    ]
    for path in font_paths:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def generate_background_gemini(client, prompt, output_path):
    """Gera imagem de fundo com Nano Banana 2 via Gemini API (OAuth)."""
    print(f"  [Gemini Nano Banana 2] Gerando fundo: {output_path.name}")

    try:
        response = client.models.generate_image(
            model="gemini-2.0-flash-exp-image-generation",
            prompt=prompt,
            config=types.GenerateImageConfig(
                aspect_ratio="1:1",
                number_of_images=1,
            ),
        )

        if response.generated_images and len(response.generated_images) > 0:
            image_data = response.generated_images[0].image.image_bytes
            with open(output_path, "wb") as f:
                f.write(image_data)
            print(f"  [Gemini] OK -> {output_path.name}")
            return True
        else:
            print(f"  [Gemini] Sem imagem no resultado")
            return False

    except Exception as e:
        print(f"  [Gemini] ERRO: {e}")
        return False


def compose_slide(background_path, text, subtext=None, cta=None, slide_num=1, total=8, checklist_items=None):
    """Compoe slide final: fundo Gemini + texto Konig."""
    bg = Image.open(background_path).convert("RGB")
    bg = bg.resize((SLIDE_SIZE, SLIDE_SIZE), Image.LANCZOS)

    # Overlay escuro para legibilidade do texto
    overlay = Image.new("RGBA", (SLIDE_SIZE, SLIDE_SIZE), (0, 0, 0, 140))
    bg.paste(overlay, (0, 0), overlay)
    bg = bg.convert("RGB")

    draw = ImageDraw.Draw(bg)

    # Borda sutil
    draw.rectangle([16, 16, SLIDE_SIZE-16, SLIDE_SIZE-16], outline=ACCENT, width=2)

    # Numero do slide
    font_num = get_font(24)
    draw.text((40, 40), f"{slide_num}/{total}", fill=MUTED, font=font_num)

    # Texto principal
    font_main = get_font(56, bold=True)
    lines = textwrap.wrap(text, width=28)
    line_h = font_main.size * 1.25

    # Calcular altura total para centralizar
    total_h = len(lines) * line_h
    if subtext:
        font_sub = get_font(32)
        sub_lines = textwrap.wrap(subtext, width=35)
        total_h += len(sub_lines) * font_sub.size * 1.25 + 20
    if cta:
        font_cta = get_font(30)
        cta_lines = textwrap.wrap(cta, width=35)
        total_h += len(cta_lines) * font_cta.size * 1.25 + 30
    if checklist_items:
        font_item = get_font(28)
        total_h += len(checklist_items) * font_item.size * 1.5 + 10

    start_y = (SLIDE_SIZE - total_h) / 2

    y = start_y
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font_main)
        text_w = bbox[2] - bbox[0]
        x = (SLIDE_SIZE - text_w) / 2
        draw.text((x, y), line, fill=TEXT_WHITE, font=font_main)
        y += line_h

    if subtext:
        y += 10
        font_sub = get_font(32)
        sub_line_h = font_sub.size * 1.25
        for line in textwrap.wrap(subtext, width=35):
            bbox = draw.textbbox((0, 0), line, font=font_sub)
            text_w = bbox[2] - bbox[0]
            x = (SLIDE_SIZE - text_w) / 2
            draw.text((x, y), line, fill="#b0a898", font=font_sub)
            y += sub_line_h

    if checklist_items:
        y += 10
        font_item = get_font(28)
        item_h = font_item.size * 1.5
        for item in checklist_items:
            draw.ellipse([70, y+4, 92, y+26], fill=ACCENT)
            check_draw = ImageDraw.Draw(bg)
            check_draw.text((75, y+6), "✓", fill=TEXT_WHITE, font=get_font(16, bold=True))
            draw.text((105, y), item, fill=TEXT_WHITE, font=font_item)
            y += item_h

    if cta:
        y += 20
        font_cta = get_font(30)
        cta_line_h = font_cta.size * 1.25
        for line in textwrap.wrap(cta, width=35):
            bbox = draw.textbbox((0, 0), line, font=font_cta)
            text_w = bbox[2] - bbox[0]
            x = (SLIDE_SIZE - text_w) / 2
            draw.text((x, y), line, fill=ACCENT_LIGHT, font=font_cta)
            y += cta_line_h

    # Barra de accent
    bar_h = 4
    draw.rectangle([50, SLIDE_SIZE-70, SLIDE_SIZE-50, SLIDE_SIZE-70+bar_h], fill=ACCENT)

    # Logo Konig
    font_logo = get_font(22, bold=True)
    logo_text = "KONIG"
    bbox = draw.textbbox((0, 0), logo_text, font=font_logo)
    logo_w = bbox[2] - bbox[0]
    draw.text(((SLIDE_SIZE - logo_w)/2, SLIDE_SIZE-55), logo_text, fill=ACCENT, font=font_logo)

    return bg


def generate_carousel(carousel_num, client=None):
    """Gera um carousel completo."""
    data = CAROUSEL_PROMPTS[carousel_num]
    name = data["name"]
    slides = data["slides"]
    total = len(slides)

    out_dir = OUTPUT_BASE / f"carousel-{carousel_num}-{name.lower().replace(' ', '-')}-nano"
    out_dir.mkdir(parents=True, exist_ok=True)

    bg_dir = out_dir / "backgrounds"
    bg_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n{'='*50}")
    print(f"CAROUSEL {carousel_num}: {name}")
    print(f"{'='*50}")

    use_gemini = client is not None

    for i, slide_data in enumerate(slides):
        slide_num = i + 1
        bg_path = bg_dir / f"bg-{slide_num:02d}.png"
        final_path = out_dir / f"slide-{slide_num:02d}.png"

        # Gerar fundo com Gemini Nano Banana 2
        if use_gemini:
            if not bg_path.exists():
                success = generate_background_gemini(client, slide_data["visual"], bg_path)
                if not success:
                    print(f"  [FALLBACK] Usando fundo escuro padrao")
                    bg_path = None
                time.sleep(2)  # Rate limit entre chamadas
            else:
                print(f"  [CACHE] Fundo ja existe: {bg_path.name}")
        else:
            bg_path = None

        # Compor slide final
        if bg_path and bg_path.exists():
            img = compose_slide(
                bg_path,
                slide_data["text"],
                slide_data.get("subtext"),
                slide_data.get("cta"),
                slide_num,
                total,
                slide_data.get("checklist_items"),
            )
        else:
            # Fallback: fundo escuro solido
            img = Image.new("RGB", (SLIDE_SIZE, SLIDE_SIZE), BG_DARK)
            draw = ImageDraw.Draw(img)
            draw.rectangle([16, 16, SLIDE_SIZE-16, SLIDE_SIZE-16], outline=ACCENT, width=2)
            font_num = get_font(24)
            draw.text((40, 40), f"{slide_num}/{total}", fill=MUTED, font=font_num)
            font_main = get_font(56, bold=True)
            lines = textwrap.wrap(slide_data["text"], width=28)
            line_h = font_main.size * 1.25
            total_h = len(lines) * line_h
            start_y = (SLIDE_SIZE - total_h) / 2
            y = start_y
            for line in lines:
                bbox = draw.textbbox((0, 0), line, font=font_main)
                text_w = bbox[2] - bbox[0]
                x = (SLIDE_SIZE - text_w) / 2
                draw.text((x, y), line, fill=TEXT_WHITE, font=font_main)
                y += line_h
            bar_h = 4
            draw.rectangle([50, SLIDE_SIZE-70, SLIDE_SIZE-50, SLIDE_SIZE-70+bar_h], fill=ACCENT)
            font_logo = get_font(22, bold=True)
            logo_text = "KONIG"
            bbox = draw.textbbox((0, 0), logo_text, font=font_logo)
            logo_w = bbox[2] - bbox[0]
            draw.text(((SLIDE_SIZE - logo_w)/2, SLIDE_SIZE-55), logo_text, fill=ACCENT, font=font_logo)

        img.save(final_path, "PNG")
        print(f"  [SLIDE] {final_path.name}")

    print(f"  -> {total} slides gerados em {out_dir}")


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--post", type=int, default=0, help="Numero do post (1-5), 0 = todos")
    parser.add_argument("--skip-bg", action="store_true", help="Pular geracao de fundo (usa fallback)")
    args = parser.parse_args()

    print("=" * 60)
    print("KONIG SYSTEMS — Nano Banana 2 via Gemini (OAuth)")
    print("=" * 60)
    print()

    client = None
    if not args.skip_bg:
        client = get_client()
        if client:
            print("[OK] Conectado ao Gemini via OAuth")
        else:
            print("[WARN] Nao foi possivel conectar ao Gemini")
            print("Gerando com fundos solidos como fallback...")
            print()

    if args.post > 0:
        generate_carousel(args.post, client=client)
    else:
        for i in range(1, 6):
            generate_carousel(i, client=client)

    print("\n" + "=" * 60)
    print("TODOS OS CARROSSEIS GERADOS!")
    print("=" * 60)


if __name__ == "__main__":
    main()
