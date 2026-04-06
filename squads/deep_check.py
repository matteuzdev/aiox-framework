import httpx, json
token = open('C:/Users/hiant/aiox-framework/squads/konig-orchestration-engine/.env').readlines()[0].split('=')[1].strip()
page_id = open('C:/Users/hiant/aiox-framework/squads/konig-orchestration-engine/.env').readlines()[1].split('=')[1].strip().replace('-', '')
headers = {'Authorization': f'Bearer {token}', 'Notion-Version': '2022-06-28', 'Content-Type': 'application/json'}

r = httpx.get(f'https://api.notion.com/v1/blocks/{page_id}/children?page_size=100', headers=headers)
blocks = r.json().get('results', [])
print('Total blocos:', len(blocks))
for i, b in enumerate(blocks):
    btype = b.get('type', '')
    bid = b.get('id', '')
    archived = b.get('archived', False)
    if btype == 'child_database':
        title = b.get('child_database', {}).get('title', '')
        print(f'  {i+1}. DATABASE: {title} | archived={archived}')
    elif btype == 'child_page':
        title = b.get('child_page', {}).get('title', '')
        print(f'  {i+1}. PAGE: {title} | archived={archived}')
    elif btype == 'heading_1':
        text = b.get('heading_1', {}).get('rich_text', [{}])
        t = text[0].get('plain_text', '') if text else ''
        print(f'  {i+1}. H1: {t} | archived={archived}')
    elif btype == 'heading_2':
        text = b.get('heading_2', {}).get('rich_text', [{}])
        t = text[0].get('plain_text', '') if text else ''
        print(f'  {i+1}. H2: {t} | archived={archived}')
    elif btype == 'paragraph':
        text = b.get('paragraph', {}).get('rich_text', [{}])
        t = text[0].get('plain_text', '') if text else ''
        print(f'  {i+1}. PARA: {t[:50]} | archived={archived}')
    elif btype == 'callout':
        text = b.get('callout', {}).get('rich_text', [{}])
        t = text[0].get('plain_text', '') if text else ''
        print(f'  {i+1}. CALLOUT: {t[:50]} | archived={archived}')
    elif btype == 'divider':
        print(f'  {i+1}. DIVIDER | archived={archived}')
    elif btype == 'bulleted_list_item':
        text = b.get('bulleted_list_item', {}).get('rich_text', [{}])
        t = text[0].get('plain_text', '') if text else ''
        print(f'  {i+1}. BULLET: {t} | archived={archived}')
    else:
        print(f'  {i+1}. {btype} | archived={archived}')

config = json.loads(open('C:/Users/hiant/aiox-framework/squads/konig-orchestration-engine/.crm-config.json').read())
print()
print('Registros nos databases:')
for key, db_id in config.items():
    if 'dashboard' in key:
        continue
    r2 = httpx.post(f'https://api.notion.com/v1/databases/{db_id}/query', headers=headers, json={'page_size': 10})
    results = r2.json().get('results', [])
    print(f'  {key}: {len(results)} registros')
