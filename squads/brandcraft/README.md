# BrandCraft

### The Visual Content Factory with Perfect Branding

**9 specialized AI agents. 11 output formats. 1 command.**

---

## O que é

BrandCraft é uma fábrica inteligente de conteúdo visual. Ele:

1. **Extrai** a identidade visual de qualquer website automaticamente
2. **Salva** como template reutilizável para sempre
3. **Gera** qualquer material — de relatórios A4 a Reels animados — com branding perfeito
4. **Valida** cada pixel antes da entrega, com scoring objetivo de qualidade

## Agentes (9)

| Agent | Nome | Função |
|-------|------|--------|
| 🎯 | Maestro | Orquestra pipelines |
| 🔍 | Prober | Extrai design system |
| 📚 | Vault | Gerencia templates |
| 🔥 | Forge | Renderiza PDF/PNG |
| 🎨 | Canvas | Cria PPTX |
| 🖌️ | Brush | Gera imagens AI |
| 🎬 | Director | Comõe vídeos |
| ✏️ | Scribe | Lê PDFs |
| ✅ | Gauge | Valida qualidade |

## Workflows (5)

1. `bc-extract-and-save` — URL → Template
2. `bc-create-document` — Content → PDF/PNG
3. `bc-create-pptx` — Content → PPTX
4. `bc-create-video` — Content → MP4/WebM
5. `bc-improve-document` — Old PDF → New PDF

## Formatos de Output (11)

### Documentos
- PDF Report A4 (210x297mm)
- PDF Slides 16:9
- Instagram Carousel (1080x1080 / 1080x1350)
- Social Card (1200x630)
- PPTX Widescreen

### Vídeos
- Reel/Short (1080x1920, 30fps)
- Story (1080x1920, 30fps)
- Landscape (1920x1080, 30fps)
- Square (1080x1080, 30fps)
- Animated Carousel (1080x1350, 30fps)

## Quick Commands

### Extração
- `*analyze-url --url=https://...`
- `*extract-tokens`
- `*save-template --name="..."`

### Documentos
- `*create-html --format=report-a4`
- `*render-pdf --content=./content.md`

### PPTX
- `*create-pptx --content=./deck.md`

### Vídeos
- `*create-reel --duration=15`
- `*create-motion-graphics`

### Validação
- `*validate-layout --document=./doc.pdf`
- `*generate-report`

## Requisitos

- Node.js 18+
- AIOS 2.1+
- Claude Code com MCP

## Instalação

```bash
cd squads/brandcraft
npm install
```

Configure o MCP nano-banana-pro:
```bash
export GEMINI_API_KEY="your_key"
```

## Tech Stack

- **Puppeteer** — HTML→PDF/PNG
- **PptxGenJS** — PPTX generation
- **Remotion** — React→Video
- **pdf-parse** — PDF reading
- **marked** — Markdown parsing

## Autoria

Original: [gutomec](https://squads.sh/u/gutomec)

---

*Made with precision by AI agents that understand branding.*
