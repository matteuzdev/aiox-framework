# brand-video Task

## Description

Cria vídeos programáticos (Reels, motion graphics, carousels animados) com Remotion.

## Steps

1. **Load Template** - Carrega design tokens para vídeo
2. **Configure Composition** - Configura composição Remotion
3. **Generate Assets** - Gera assets visuais
4. **Render Video** - Renderiza MP4

## Usage

```
*create-reel --content=" produto" --duration=15
*create-motion --theme="tech"
*render-video --compositionId=main
```

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| content | string | Yes | Tema/conteúdo do vídeo |
| duration | number | No | Duração em segundos (default: 15) |
| format | string | No | reel, story, landscape, square |

## Supported Formats

| Format | Dimensions | FPS |
|--------|------------|-----|
| reel | 1080x1920 | 30 |
| story | 1080x1920 | 30 |
| landscape | 1920x1080 | 30 |
| square | 1080x1080 | 30 |
