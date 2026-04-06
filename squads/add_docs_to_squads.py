"""Add documentation as sub-blocks inside existing squad pages in Notion.

Instead of creating separate pages, this script adds all MD documentation
as children blocks inside each squad's existing page.
"""

import httpx
import json
import os
from pathlib import Path

TOKEN = 'ntn_c735562228178mKoCWkntIoCiDsCNkbTo01NeGmcR0cgOw'
HEADERS = {'Authorization': f'Bearer {TOKEN}', 'Notion-Version': '2022-06-28', 'Content-Type': 'application/json'}
SQUADS_DIR = Path('C:/Users/hiant/aiox-framework/squads')

# Skip dirs
SKIP_DIRS = {'agents', 'tasks', 'workflows', 'checklists', 'config', 'node_modules', '.git', '__pycache__', '.playwright-mcp', '.vscode'}
SKIP_FILES = {'sdr_stress_test_report.md'}
SKIP_SQUADS = {'pixel-agents', 'agent-ajuda'}

# Map squad name to page ID from Notion
SQUAD_PAGE_IDS = {
    'company-strategic-core': '3391b66d-e389-811f-83b9-ee242166146b',
    'konig-growth-core': '3391b66d-e389-8148-9893-cf167752584a',
    'konig-context-core': '3391b66d-e389-814b-9141-f0b7c80f43f6',
    'konig-research-intel-core': '3391b66d-e389-814b-bc55-fd9eff3c8ee3',
    'konig-planning-core': '3391b66d-e389-8152-a75b-d15fa285466f',
    'konig-ops-core': '3391b66d-e389-8156-8a58-ded04d983868',
    'konig-delivery-factory-core': '3391b66d-e389-8168-b6a7-ef6b96325446',
    'konig-prospecting-core': '3391b66d-e389-818a-b53d-c2e8cd9afb21',
    'konig-revenue-core': '3391b66d-e389-8192-a1e1-e279823e9cfe',
    'konig-engineering-core': '3391b66d-e389-819a-8473-e767048b59fe',
    'konig-experience-core': '3391b66d-e389-81a1-b59b-c9674be57f7c',
    'konig-orchestration-core': '3391b66d-e389-81a4-8f86-cca9fb78c7ba',
    'konig-product-core': '3391b66d-e389-81be-815f-da77f71fcfda',
    'konig-media-authority-core': '3391b66d-e389-81c5-b70c-f6ed97e6486d',
    'konig-governance-core': '3391b66d-e389-81e0-8006-f0a5fd2668c0',
    'konig-athenaeum-core': '3391b66d-e389-81eb-bb74-c3aea096bcbf',
    'konig-instagram-intelligence-core': '3391b66d-e389-81f4-a41a-dca7a85124ab',
}


def find_md_files(squad_dir):
    """Find all non-structural .md files in a squad directory."""
    files = []
    for root, dirs, filenames in os.walk(squad_dir):
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
            pass
        elif line.startswith('```'):
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
            text = line.strip()[:2000]
            if text:
                blocks.append({
                    'object': 'block',
                    'type': 'paragraph',
                    'paragraph': {'rich_text': [{'text': {'content': text}}]},
                })
    
    if not blocks:
        blocks.append({
            'object': 'block',
            'type': 'paragraph',
            'paragraph': {'rich_text': [{'text': {'content': content[:2000]}}]},
        })
    
    return blocks


def add_docs_to_squad_page(squad_name, squad_dir, files, page_id):
    """Add all doc files as sub-blocks to existing squad page."""
    print(f"\n[{squad_name}] Adding {len(files)} files to page {page_id}...")
    
    # First, add a section header
    header_blocks = [
        {'object': 'block', 'type': 'divider', 'divider': {}},
        {'object': 'block', 'type': 'heading_2', 'heading_2': {'rich_text': [{'text': {'content': '[DOCUMENTACAO]'}}]}},
        {'object': 'block', 'type': 'paragraph', 'paragraph': {'rich_text': [{'text': {'content': f'{len(files)} arquivos de documentacao importados.'}}]}},
    ]
    
    r = httpx.patch(
        f'https://api.notion.com/v1/blocks/{page_id}/children',
        headers=HEADERS,
        json={'children': header_blocks},
        timeout=60,
    )
    if r.status_code != 200:
        print(f'  ERRO adding header: {r.status_code} - {r.text[:200]}')
        return False
    
    print(f'  Header added OK')
    
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
            {'object': 'block', 'type': 'heading_3', 'heading_3': {'rich_text': [{'text': {'content': '[FILE] ' + file_title}}]}},
        ] + blocks + [
            {'object': 'block', 'type': 'divider', 'divider': {}},
        ]
        
        # Batch blocks (max 80 per request)
        for i in range(0, len(file_blocks), 80):
            batch = file_blocks[i:i+80]
            try:
                r = httpx.patch(
                    f'https://api.notion.com/v1/blocks/{page_id}/children',
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
    
    return True


def main():
    print("=" * 60)
    print("ADD DOCS TO EXISTING SQUAD PAGES")
    print("=" * 60)
    
    squads_processed = 0
    files_added = 0
    
    for squad_dir in sorted(SQUADS_DIR.iterdir()):
        if not squad_dir.is_dir():
            continue
        if squad_dir.name.startswith('.'):
            continue
        if squad_dir.name in SKIP_SQUADS:
            continue
        
        if squad_dir.name not in SQUAD_PAGE_IDS:
            print(f"\n[SKIP] {squad_dir.name} - no page ID mapping")
            continue
        
        files = find_md_files(squad_dir)
        if not files:
            print(f"\n[SKIP] {squad_dir.name} - no doc files found")
            continue
        
        print(f"\n{'='*40}")
        print(f"Squad: {squad_dir.name} ({len(files)} arquivos)")
        
        page_id = SQUAD_PAGE_IDS[squad_dir.name]
        success = add_docs_to_squad_page(squad_dir.name, squad_dir, files, page_id)
        
        if success:
            squads_processed += 1
            files_added += len(files)
    
    print(f"\n{'='*60}")
    print(f"CONCLUIDO!")
    print(f"Squads processados: {squads_processed}")
    print(f"Arquivos adicionados: {files_added}")
    print(f"{'='*60}")


if __name__ == '__main__':
    main()
