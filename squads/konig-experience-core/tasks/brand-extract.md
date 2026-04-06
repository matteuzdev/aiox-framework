# brand-extract Task

## Description

Extrai design system de qualquer URL e salva como template reutilizável.

## Steps

1. **Analyze URL** - Recebe URL e executa análise
2. **Extract Tokens** - Extrai cores, tipografia, espaçamento, logos
3. **Save Template** - Salva template versionado

## Usage

```
*brand-extract --url=https://empresa.com
*extract-tokens
*save-template --name="empresa"
```

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| url | string | Yes | URL do website |
| template_name | string | No | Nome do template |

## Output

- Template salvo em `templates/`
- Tokens em formato YAML com frontmatter
