import httpx
import json

TOKEN = 'ntn_c735562228178mKoCWkntIoCiDsCNkbTo01NeGmcR0cgOw'
HEADERS = {'Authorization': f'Bearer {TOKEN}', 'Notion-Version': '2022-06-28', 'Content-Type': 'application/json'}

# Query squads database with correct title field
r = httpx.post('https://api.notion.com/v1/databases/3391b66d-e389-81d7-984c-e1025669ee23/query', headers=HEADERS, json={'page_size': 100})
if r.status_code == 200:
    results = r.json()['results']
    print(f'Found {len(results)} squads in database:')
    for p in results:
        name = p['properties'].get('Squad', {}).get('title', [{}])[0].get('plain_text', 'NO NAME')
        print(f'{p["id"]} | {name}')
else:
    print(f'Error: {r.status_code}')
    print(r.text[:500])
