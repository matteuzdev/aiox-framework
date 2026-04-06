import httpx
import json

TOKEN = 'ntn_c735562228178mKoCWkntIoCiDsCNkbTo01NeGmcR0cgOw'
HEADERS = {'Authorization': f'Bearer {TOKEN}', 'Notion-Version': '2022-06-28', 'Content-Type': 'application/json'}

# Get database schema
r = httpx.get('https://api.notion.com/v1/databases/3391b66d-e389-81d7-984c-e1025669ee23', headers=HEADERS)
if r.status_code == 200:
    db = r.json()
    print('Database properties:')
    for name, prop in db['properties'].items():
        print(f'  {name}: {prop["type"]}')
else:
    print(f'Error: {r.status_code}')
    print(r.text[:500])
