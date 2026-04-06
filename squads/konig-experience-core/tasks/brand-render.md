# brand-render Task

## Description

Renderiza documentos PDF/PNG ou apresentações PPTX com design system aplicado.

## Steps

1. **Load Template** - Carrega template da marca
2. **Generate Images** - Gera imagens AI (se necessário)
3. **Render Document** - Renderiza para PDF/PPTX
4. **Validate Quality** - Valida consistência

## Usage

```
*render-pdf --content=./content.md --format=report-a4
*render-png --content=./card.md
*create-pptx --content=./deck.md
```

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| content | file | Yes | Arquivo de conteúdo |
| format | string | No | Formato (report-a4, slides-16x9, carousel, social-card) |
| template | string | Yes | Nome do template |

## Supported Formats

### Documents
- `report-a4` - PDF A4 (210x297mm)
- `slides-16x9` - PDF 16:9
- `carousel` - Instagram 1080x1080
- `social-card` - 1200x630

### Presentations
- `pptx` - PowerPoint 16:9
