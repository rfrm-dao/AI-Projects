import requests
import pandas as pd
import time
import sys
import os

# === CONFIG ===
CG_API_KEY_VALUE = os.environ.get("CG_API_KEY")
API_BASE_URL = 'https://pro-api.coingecko.com/api/v3'
CATEGORY_ID = 'artificial-intelligence'
OUTPUT_FILENAME = 'AI_Projects.csv'

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
    'x-cg-pro-api-key': CG_API_KEY_VALUE,
}

def fetch_coin_details(coin_id):
    url = f'{API_BASE_URL}/coins/{coin_id}'
    time.sleep(0.3)

    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        r.raise_for_status()
        data = r.json()
        twitter = data.get("links", {}).get("twitter_screen_name")

        return f"@{twitter}" if twitter else "N/A"
    
    except:
        return "FETCH_ERROR"

def fetch_full_ai_list():
    print(f"🚀 Fetching full list of AI category coins (no limit)")

    all_projects = []
    page = 1

    while True:
        params = {
            'vs_currency': 'usd',
            'category': CATEGORY_ID,
            'per_page': 250,
            'page': page,
            'order': 'market_cap_desc'
        }

        try:
            r = requests.get(f"{API_BASE_URL}/coins/markets", headers=HEADERS, params=params)
            r.raise_for_status()
            data = r.json()

        except Exception as e:
            print(f"⚠️ Error on page {page}: {e}")
            break

        # If API returns no more data → stop
        if not data:
            break

        for item in data:
            all_projects.append({
                'ID': item.get('id'),
                'Project Name': item.get('name'),
                'Ticker': item.get('symbol').upper(),
            })

        print(f"📦 Page {page} fetched → +{len(data)} tokens (Total: {len(all_projects)})")

        page += 1
        time.sleep(0.25)

    print(f"✔️ Completed pagination — total {len(all_projects)} AI tokens found\n")
    return all_projects


def main_scraper():
    if not CG_API_KEY_VALUE:
        print("❌ ERROR: Missing CG API key")
        sys.exit(1)

    print("--- STARTING AI SCRAPER ---")

    # Step 1: fetch all pages
    projects = fetch_full_ai_list()

    # Step 2: fetch twitter handles
    final = []
    for i, project in enumerate(projects):
        print(f"[{i+1}/{len(projects)}] {project['Project Name']}   ", end="\r")

        twitter = fetch_coin_details(project["ID"])

        final.append({
            "Project Name": project["Project Name"],
            "Ticker": project["Ticker"],
            "X Username": twitter
        })

    print("\n✔️ Twitter scraping finished")

    # Step 3: save
    df = pd.DataFrame(final)
    df.to_csv(OUTPUT_FILENAME, index=False)
    print(f"💾 Saved → {OUTPUT_FILENAME}")


if __name__ == "__main__":
    main_scraper()
