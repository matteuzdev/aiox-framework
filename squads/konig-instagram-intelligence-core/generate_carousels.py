"""Gerador de imagens de carrossel para Instagram.

Gera slides de carrossel como PNGs prontos para publicacao.
Usa Pillow para renderizacao direta.

Uso: python generate_carousels.py
"""

from PIL import Image, ImageDraw, ImageFont
import os
import textwrap

# --- Config ---
WIDTH = 1080
HEIGHT = 1080
OUTPUT_BASE = os.path.join(os.path.dirname(__file__), "output")

# Cores Konig
BG_DARK = "#0a0f0d"
BG_LIGHT = "#f7f2e9"
ACCENT = "#0a4b41"
ACCENT_LIGHT = "#1a7b6b"
TEXT_WHITE = "#f0ece4"
TEXT_DARK = "#152025"
MUTED = "#5f6a70"
GOLD = "#9e6731"

def get_font(size, bold=False):
    """Tenta carregar fonte, fallback para padrao."""
    font_paths = [
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/calibribd.ttf" if bold else "C:/Windows/Fonts/calibri.ttf",
        "C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf",
    ]
    for path in font_paths:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()

def draw_text_centered(draw, text, y, font, fill, max_width=900):
    """Desenha texto centralizado com word wrap."""
    lines = textwrap.wrap(text, width=35)
    line_height = font.size * 1.3
    total_height = len(lines) * line_height
    start_y = y - total_height / 2 + line_height / 2

    for i, line in enumerate(lines):
        bbox = draw.textbbox((0, 0), line, font=font)
        text_w = bbox[2] - bbox[0]
        x = (WIDTH - text_w) / 2
        draw.text((x, start_y + i * line_height), line, fill=fill, font=font)

def create_slide_dark(text, slide_num, total, accent_color=ACCENT):
    """Slide com fundo escuro (padrao Konig)."""
    img = Image.new("RGB", (WIDTH, HEIGHT), BG_DARK)
    draw = ImageDraw.Draw(img)

    # Borda sutil
    draw.rectangle([20, 20, WIDTH-20, HEIGHT-20], outline=accent_color, width=2)

    # Numero do slide
    font_num = get_font(28)
    draw.text((50, 50), f"{slide_num}/{total}", fill=MUTED, font=font_num)

    # Texto principal
    font_main = get_font(52, bold=True)
    draw_text_centered(draw, text, HEIGHT/2 - 40, font_main, TEXT_WHITE)

    # Barra de accent no fundo
    bar_h = 4
    draw.rectangle([60, HEIGHT-80, WIDTH-60, HEIGHT-80+bar_h], fill=accent_color)

    # Logo Konig
    font_logo = get_font(24, bold=True)
    draw.text((WIDTH/2 - 60, HEIGHT-60), "KONIG", fill=accent_color, font=font_logo)

    return img

def create_slide_light(text, slide_num, total, accent_color=ACCENT):
    """Slide com fundo claro."""
    img = Image.new("RGB", (WIDTH, HEIGHT), BG_LIGHT)
    draw = ImageDraw.Draw(img)

    # Borda sutil
    draw.rectangle([20, 20, WIDTH-20, HEIGHT-20], outline=accent_color, width=2)

    # Numero do slide
    font_num = get_font(28)
    draw.text((50, 50), f"{slide_num}/{total}", fill=MUTED, font=font_num)

    # Texto principal
    font_main = get_font(52, bold=True)
    draw_text_centered(draw, text, HEIGHT/2 - 40, font_main, TEXT_DARK)

    # Barra de accent no fundo
    bar_h = 4
    draw.rectangle([60, HEIGHT-80, WIDTH-60, HEIGHT-80+bar_h], fill=accent_color)

    # Logo Konig
    font_logo = get_font(24, bold=True)
    draw.text((WIDTH/2 - 60, HEIGHT-60), "KONIG", fill=accent_color, font=font_logo)

    return img

def create_slide_number(text, number, slide_num, total, accent_color=ACCENT_LIGHT):
    """Slide com numero de destaque."""
    img = Image.new("RGB", (WIDTH, HEIGHT), BG_DARK)
    draw = ImageDraw.Draw(img)

    # Borda
    draw.rectangle([20, 20, WIDTH-20, HEIGHT-20], outline=accent_color, width=2)

    # Numero do slide
    font_num = get_font(28)
    draw.text((50, 50), f"{slide_num}/{total}", fill=MUTED, font=font_num)

    # Numero grande
    font_big = get_font(120, bold=True)
    bbox = draw.textbbox((0, 0), number, font=font_big)
    num_w = bbox[2] - bbox[0]
    draw.text(((WIDTH - num_w)/2, HEIGHT/2 - 140), number, fill=accent_color, font=font_big)

    # Texto explicativo
    font_main = get_font(40)
    draw_text_centered(draw, text, HEIGHT/2 + 40, font_main, TEXT_WHITE)

    # Barra
    bar_h = 4
    draw.rectangle([60, HEIGHT-80, WIDTH-60, HEIGHT-80+bar_h], fill=accent_color)

    # Logo
    font_logo = get_font(24, bold=True)
    draw.text((WIDTH/2 - 60, HEIGHT-60), "KONIG", fill=accent_color, font=font_logo)

    return img

def create_slide_checklist(items, slide_num, total):
    """Slide de checklist."""
    img = Image.new("RGB", (WIDTH, HEIGHT), BG_LIGHT)
    draw = ImageDraw.Draw(img)

    # Borda
    draw.rectangle([20, 20, WIDTH-20, HEIGHT-20], outline=ACCENT, width=2)

    # Numero do slide
    font_num = get_font(28)
    draw.text((50, 50), f"{slide_num}/{total}", fill=MUTED, font=font_num)

    # Items
    font_item = get_font(32)
    y_start = 180
    line_h = 60

    for i, item in enumerate(items):
        y = y_start + i * line_h
        # Check icon
        draw.ellipse([80, y+5, 100, y+25], fill=ACCENT)
        draw.text((85, y+7), "✓", fill=TEXT_WHITE, font=get_font(18, bold=True))
        # Text
        draw.text((120, y), item, fill=TEXT_DARK, font=font_item)

    # Barra
    draw.rectangle([60, HEIGHT-80, WIDTH-60, HEIGHT-80+4], fill=ACCENT)

    # Logo
    font_logo = get_font(24, bold=True)
    draw.text((WIDTH/2 - 60, HEIGHT-60), "KONIG", fill=ACCENT, font=font_logo)

    return img

def create_slide_cta(text, slide_num, total, cta_text=""):
    """Slide de CTA (ultimo slide)."""
    img = Image.new("RGB", (WIDTH, HEIGHT), ACCENT)
    draw = ImageDraw.Draw(img)

    # Borda
    draw.rectangle([20, 20, WIDTH-20, HEIGHT-20], outline=TEXT_WHITE, width=2)

    # Texto principal
    font_main = get_font(48, bold=True)
    draw_text_centered(draw, text, HEIGHT/2 - 60, font_main, TEXT_WHITE)

    # CTA
    if cta_text:
        font_cta = get_font(36)
        draw_text_centered(draw, cta_text, HEIGHT/2 + 60, font_cta, BG_LIGHT)

    # Logo
    font_logo = get_font(28, bold=True)
    draw.text((WIDTH/2 - 60, HEIGHT-60), "KONIG", fill=BG_LIGHT, font=font_logo)

    return img


# --- CAROUSEL 1: Perda Mensal ---
def generate_carousel_1():
    out = os.path.join(OUTPUT_BASE, "carousel-1-perda-mensal")
    os.makedirs(out, exist_ok=True)
    total = 8

    slides = [
        create_slide_dark("Sua clinica de oftalmo\nperde R$15-40k por mes.", 1, total),
        create_slide_dark("E nao e com equipamento.\nNao e com equipe.", 2, total),
        create_slide_dark("E com agenda vazia\nque voce nem percebe.", 3, total),
        create_slide_number("20%", "dos horarios ficam sem\npreenchimento todo mes", 4, total),
        create_slide_dark("Cada vaga vazia = R$350\nque nao volta.", 5, total),
        create_slide_number("R$154k", "perdidos por ano\nem horarios nao preenchidos", 6, total),
        create_slide_dark("Isso sem contar no-show,\ncancelamento e retorno\nnao agendado.", 7, total),
        create_slide_cta("Quer saber quanto a SUA\nclinica perde?", 8, total, "Comenta CALCULO"),
    ]

    for i, slide in enumerate(slides):
        path = os.path.join(out, f"slide-{i+1:02d}.png")
        slide.save(path, "PNG")
        print(f"  Carousel 1: {path}")

# --- CAROUSEL 2: Checklist Pre-Op ---
def generate_carousel_2():
    out = os.path.join(OUTPUT_BASE, "carousel-2-checklist")
    os.makedirs(out, exist_ok=True)
    total = 10

    slides = [
        create_slide_dark("90% das complicacoes\ncomecam ANTES da cirurgia.", 1, total),
        create_slide_dark("Nao e no centro cirurgico.\nE na consulta.", 2, total),
        create_slide_checklist([
            "Exames completos com 7 dias de antecedencia",
            "Suspensao correta dos 5 medicamentos principais",
        ], 3, total),
        create_slide_checklist([
            "Conversa sobre expectativas reais do paciente",
            "Checklist de comorbidades (diabetes, hipertensao)",
        ], 4, total),
        create_slide_checklist([
            "Confirmacao de jejum e instrucoes pre-cirurgia",
            "Termo de consentimento especifico (nao generico)",
        ], 5, total),
        create_slide_checklist([
            "Contato de emergencia disponivel 24h pre e pos",
        ], 6, total),
        create_slide_dark("Se sua clinica nao tem isso\nformalizado, voce esta\ndependendo da sorte.", 7, total),
        create_slide_dark("E sorte nao e processo.", 8, total),
        create_slide_cta("Checklist que todo oftalmo\ndeveria ter na gaveta.", 9, total, "Salva pra consultar antes"),
        create_slide_cta("Konig Systems\nAutoridade Operacional", 10, total, "Siga para mais"),
    ]

    for i, slide in enumerate(slides):
        path = os.path.join(out, f"slide-{i+1:02d}.png")
        slide.save(path, "PNG")
        print(f"  Carousel 2: {path}")

# --- CAROUSEL 3: 5 Momentos ---
def generate_carousel_3():
    out = os.path.join(OUTPUT_BASE, "carousel-3-5-momentos")
    os.makedirs(out, exist_ok=True)
    total = 7

    slides = [
        create_slide_dark("O paciente nao volta\npelo equipamento.", 1, total),
        create_slide_dark("Ele volta por como se sentiu\nnesses 5 momentos:", 2, total),
        create_slide_light("1. Quando ligou para agendar\n(atendeu rapido? foi claro?)", 3, total),
        create_slide_light("2. Quando chegou na recepcao\n(esperou 5 min ou 45?)", 4, total),
        create_slide_light("3. Quando o medico explicou\n(entendeu ou ficou com duvida?)", 5, total),
        create_slide_light("4. Quando recebeu o pos-consulta\n(teve suporte ou foi abandonado?)", 6, total),
        create_slide_cta("Qual desses momentos\nsua clinica mais erra?", 7, total, "Comenta aqui"),
    ]

    for i, slide in enumerate(slides):
        path = os.path.join(out, f"slide-{i+1:02d}.png")
        slide.save(path, "PNG")
        print(f"  Carousel 3: {path}")

# --- CAROUSEL 4: Equipamento vs Processo ---
def generate_carousel_4():
    out = os.path.join(OUTPUT_BASE, "carousel-4-equipamento")
    os.makedirs(out, exist_ok=True)
    total = 6

    slides = [
        create_slide_dark("Voce comprou o melhor\nOCT do mercado.", 1, total),
        create_slide_dark("E sua agenda\ncontinua vazia.", 2, total),
        create_slide_dark("Sabe por que?\nPaciente nao compra equipamento.", 3, total),
        create_slide_dark("Paciente compra confianca,\nclareza e resultado.", 4, total),
        create_slide_number(">", "Processo > Equipamento.\nSempre.", 5, total, GOLD),
        create_slide_cta("Concorda ou discorda?", 6, total, "Debate aqui embaixo"),
    ]

    for i, slide in enumerate(slides):
        path = os.path.join(out, f"slide-{i+1:02d}.png")
        slide.save(path, "PNG")
        print(f"  Carousel 4: {path}")

# --- CAROUSEL 5: Matematica ---
def generate_carousel_5():
    out = os.path.join(OUTPUT_BASE, "carousel-5-matematica")
    os.makedirs(out, exist_ok=True)
    total = 7

    slides = [
        create_slide_dark("Consulta = R$350.\n20 pacientes/dia.\nQuanto voce fatura?", 1, total),
        create_slide_dark("Se respondeu R$7.000/dia...\nerrou.", 2, total),
        create_slide_dark("20% dos pacientes\nnao pagam particular.", 3, total),
        create_slide_dark("15% dos horarios\nficam vazios.", 4, total),
        create_slide_dark("10% dos pacientes\nfaltam sem avisar.", 5, total),
        create_slide_number("R$3.5-4.5k", "por dia e o numero real.\nNao R$7.000.", 6, total),
        create_slide_cta("Quer que eu faca essa conta\npra sua clinica?", 7, total, "Comenta MINHA CONTA"),
    ]

    for i, slide in enumerate(slides):
        path = os.path.join(out, f"slide-{i+1:02d}.png")
        slide.save(path, "PNG")
        print(f"  Carousel 5: {path}")


if __name__ == "__main__":
    print("Gerando carrosseis Konig x Oftalmo...\n")
    generate_carousel_1()
    generate_carousel_2()
    generate_carousel_3()
    generate_carousel_4()
    generate_carousel_5()
    print("\nTodos os carrosseis gerados!")
