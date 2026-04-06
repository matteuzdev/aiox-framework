"""Upload all non-structural MD files from squads to Notion.

Scans all squad directories, finds .md files outside agents/, tasks/, workflows/,
checklists/, config/ and creates Notion pages with the content.
"""

import httpx, json, os
from pathlib import Path
from datetime import datetime

TOKEN = open('C:/Users/hiant/aiox-framework/squads/konig-orchestration-engine/.env').readlines()[0].split('=')[1].strip()
PAGE_ID = open('C:/Users/hiant/aiox-framework/squads/konig-orchestration-engine/.env').readlines()[1].split('=')[1].strip().replace('-', '')
HEADERS = {'Authorization': f'Bearer {TOKEN}', 'Notion-Version': '2022-06-28', 'Content-Type': 'application/json'}
SQUADS_DIR = Path('C:/Users/hiant/aiox-framework/squads')

# Dirs to skip (structural)
SKIP_DIRS = {'agents', 'tasks', 'workflows', 'checklists', 'config', 'node_modules', '.git', '__pycache__', '.playwright-mcp', '.vscode'}
SKIP_FILES = {'sdr_stress_test_report.md'}

# Squads to skip entirely
SKIP_SQUADS = {'pixel-agents', 'agent-ajuda'}


def find_md_files(squad_dir):
    """Find all non-structural .md files in a squad directory."""
    files = []
    for root, dirs, filenames in os.walk(squad_dir):
        # Skip excluded dirs
        rel_root = Path(root).relative_to(squad_dir)
        if any(part in SKIP_DIRS for part in rel_root.parts):
            continue
        
        for fn in filenames:
            if not fn.endswith('.md'):
                continue
            if fn in SKIP_FILES:
                continue
            
            full_path = Path(root) / fn
            rel_path = full_path.relative_to(squad_dir)
            files.append((rel_path, full_path))
    
    return sorted(files, key=lambda x: str(x[0]))


def md_to_notion_blocks(content, max_blocks=80):
    """Convert markdown content to Notion blocks."""
    blocks = []
    lines = content.split('\n')
    
    for line in lines:
        if len(blocks) >= max_blocks:
            blocks.append({
                'object': 'block',
                'type': 'paragraph',
                'paragraph': {'rich_text': [{'text': {'content': '... (conteudo truncado)'}}]},
            })
            break
        
        # Headings
        if line.startswith('### ') and line.strip():
            blocks.append({
                'object': 'block',
                'type': 'heading_3',
                'heading_3': {'rich_text': [{'text': {'content': line[4:].strip()}}]},
            })
        elif line.startswith('## ') and line.strip():
            blocks.append({
                'object': 'block',
                'type': 'heading_2',
                'heading_2': {'rich_text': [{'text': {'content': line[3:].strip()}}]},
            })
        elif line.startswith('# ') and line.strip():
            blocks.append({
                'object': 'block',
                'type': 'heading_1',
                'heading_1': {'rich_text': [{'text': {'content': line[2:].strip()}}]},
            })
        elif line.startswith('- ') or line.startswith('* '):
            text = line[2:].strip()
            if text:
                blocks.append({
                    'object': 'block',
                    'type': 'bulleted_list_item',
                    'bulleted_list_item': {'rich_text': [{'text': {'content': text[:2000]}}]},
                })
        elif line.startswith('1. ') or (line[0:1].isdigit() and line[1:3] == '. '):
            text = line[3:].strip()
            if text:
                blocks.append({
                    'object': 'block',
                    'type': 'numbered_list_item',
                    'numbered_list_item': {'rich_text': [{'text': {'content': text[:2000]}}]},
                })
        elif line.strip() == '':
            # Skip empty lines but add spacing via empty paragraph if needed
            pass
        elif line.startswith('```'):
            # Code block - just show as paragraph for simplicity
            pass
        elif line.startswith('> '):
            text = line[2:].strip()
            if text:
                blocks.append({
                    'object': 'block',
                    'type': 'quote',
                    'quote': {'rich_text': [{'text': {'content': text[:2000]}}]},
                })
        elif line.strip():
            # Regular paragraph
            text = line.strip()[:2000]
            if text:
                blocks.append({
                    'object': 'block',
                    'type': 'paragraph',
                    'paragraph': {'rich_text': [{'text': {'content': text}}]},
                })
    
    # Ensure at least one block
    if not blocks:
        blocks.append({
            'object': 'block',
            'type': 'paragraph',
            'paragraph': {'rich_text': [{'text': {'content': content[:2000]}}]},
        })
    
    return blocks


def create_squad_doc_page(squad_name, squad_dir, files):
    """Create a Notion page for a squad with all its docs."""
    print(f"\n[{squad_name}] Creating doc page with {len(files)} files...")
    
    # Create main squad doc page
    payload = {
        'parent': {'type': 'page_id', 'page_id': PAGE_ID},
        'properties': {'title': {'title': [{'text': {'content': f'{squad_name} - Documentacao'}}]}},
        'icon': {'type': 'emoji', 'emoji': '📚'},
        'children': [
            {'object': 'block', 'type': 'heading_1', 'heading_1': {'rich_text': [{'text': {'content': f'{squad_name} - Documentacao'}}]}},
            {'object': 'block', 'type': 'paragraph', 'paragraph': {'rich_text': [{'text': {'content': f'Documentos e artefatos do squad {squad_name}. {len(files)} arquivos importados.'}}]}},
            {'object': 'block', 'type': 'divider', 'divider': {}},
        ],
    }
    
    r = httpx.post('https://api.notion.com/v1/pages', headers=HEADERS, json=payload)
    if r.status_code != 200:
        print(f'  ERRO ao criar pagina: {r.text[:200]}')
        return None
    
    squad_page_id = r.json()['id']
    print(f'  Pagina criada: {squad_page_id}')
    
    # Add each file as a sub-section
    for rel_path, full_path in files:
        try:
            content = full_path.read_text(encoding='utf-8', errors='replace')
        except Exception as e:
            print(f'  ERRO lendo {rel_path}: {e}')
            continue
        
        # Skip frontmatter-only files
        if content.strip().startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3 and not parts[2].strip():
                continue
        
        file_title = str(rel_path).replace('/', ' / ').replace('\\', ' / ')
        blocks = md_to_notion_blocks(content)
        
        # Add heading + blocks for this file
        file_blocks = [
            {'object': 'block', 'type': 'heading_2', 'heading_2': {'rich_text': [{'text': {'content': f'📄 {file_title}'}}]}},
        ] + blocks + [
            {'object': 'block', 'type': 'divider', 'divider': {}},
        ]
        
        # Notion has a limit of 100 blocks per request, so batch them
        for i in range(0, len(file_blocks), 80):
            batch = file_blocks[i:i+80]
            try:
                r = httpx.patch(
                    f'https://api.notion.com/v1/blocks/{squad_page_id}/children',
                    headers=HEADERS,
                    json={'children': batch},
                    timeout=60,
                )
                if r.status_code != 200:
                    print(f'  ERRO adicionando {rel_path}: {r.status_code}')
                    break
            except Exception as e:
                print(f'  TIMEOUT/ERRO em {rel_path}: {e}')
                break
        
        print(f'  OK: {rel_path}')
    
    return squad_page_id


def main():
    print("=" * 60)
    print("UPLOAD DOCUMENTOS DOS SQUADS PARA NOTION")
    print("=" * 60)
    
    squads_processed = 0
    files_uploaded = 0
    
    for squad_dir in sorted(SQUADS_DIR.iterdir()):
        if not squad_dir.is_dir():
            continue
        if squad_dir.name.startswith('.'):
            continue
        if squad_dir.name in SKIP_SQUADS:
            continue
        
        files = find_md_files(squad_dir)
        if not files:
            continue
        
        print(f"\n{'='*40}")
        print(f"Squad: {squad_dir.name} ({len(files)} arquivos)")
        
        page_id = create_squad_doc_page(squad_dir.name, squad_dir, files)
        if page_id:
            squads_processed += 1
            files_uploaded += len(files)
    
    print(f"\n{'='*60}")
    print(f"CONCLUIDO!")
    print(f"Squads processados: {squads_processed}")
    print(f"Arquivos uploadados: {files_uploaded}")
    print(f"{'='*60}")


if __name__ == '__main__':
    main()
