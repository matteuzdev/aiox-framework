"""Quick update to Notion squads page with current status."""

import httpx
import json
from pathlib import Path

TOKEN = "ntn_c735562228178mKoCWkntIoCiDsCNkbTo01NeGmcR0cgOw"
PAGE_ID = "3391b66de389803eb8b3f5de0fea3b1a"

def update_notion():
    """Update Notion page."""
    squads = get_squads()
    blocks = create_blocks(squads)
    
    # Debug
    print(f"Page ID: {PAGE_ID}")
    print(f"Blocks: {len(blocks)}")
    
    # Append blocks to page - use blocks endpoint
    url = f"https://api.notion.com/v1/blocks/{PAGE_ID}/children"
    print(f"URL: {url}")
    
    # Add blocks one by one to test
    for i, block in enumerate(blocks[:5]):  # Test first 5
        single_url = f"https://api.notion.com/v1/blocks/{PAGE_ID}/children"
        response = httpx.post(
            single_url,
            headers=HEADERS,
            json={"children": [block]},
            timeout=30
        )
        print(f"Block {i}: {response.status_code}")
    
    if response.status_code == 200:
        print(f"Updated! {len(squads)} squads listed.")
    else:
        print(f"Error: {response.status_code}")
        print(response.text[:500])

if __name__ == "__main__":
    update_notion()