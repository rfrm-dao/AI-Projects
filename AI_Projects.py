import requests
import pandas as pd
import time
import sys
import os

# --- CONFIGURATION ---
CG_API_KEY = os.environ.get("CG_API_KEY")  # GitHub Secret value
API_BASE_URL = 'https://pro-api.coingecko.com/api/v3'
CATEGORY_ID = 'artificial-intelligence'
OUTPUT_FILENAME = 'AI_Projects.csv'

HEADERS = {
    'User-Agent': 'Mozilla/5.0',
    'x-cg-pro-api-key': CG_API_KEY,
}
# ---------------------


def fetch_twitter_handle(coin_id):
    """Returns the twitter handle for a given CoinGecko ID"""
    url = f'{API_BASE_URL}/coins/{coin_id}'
    time.sleep(0.25)

    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        r.raise_for_status()
        details = r.json()

        tw = details.get('links', {}).get('twitter_screen_name')
        if tw:
            return f'@{tw}'
        else:
            return 'N/A'

    except Exception as e:
        print(f"Error fetching details for {coin_id}: {e}")
        return "ERROR"


def main():
    if not CG_API_KEY:
        print("❌ ERROR: No CoinGecko API key found. Define CG_API_KEY in system or GitHub Secrets.")
        sys.exit(1)

    print("🚀 Fetching AI category coins from CoinGecko...")

    url = f"{API_BASE_URL}/coins/markets"
    params = {
        "vs_currency": "usd",
        "category": CATEGORY_ID,
        "per_page": 250,
        "page": 1,
    }

    try:
        r = requests.get(url, headers=HEADERS, params=params, timeout=10)
        r.raise_for_status()
        coins = r.json()

    except Exception as e:
        print(f"❌ API error requesting category list: {e}")
        sys.exit(1)

    print(f"✅ Found {len(coins)} AI coins\n")

    final = []
    for idx, c in enumerate(coins):
        coin_id = c.get('id')
        coin_name = c.get('name')
        coin_symbol = c.get('symbol').upper()

        print(f"[{idx+1}/{len(coins)}] {coin_name} ({coin_symbol})")

        twitter = fetch_twitter_handle(coin_id)

        final.append({
            "Project": coin_name,
            "Ticker": coin_symbol,
            "Twitter": twitter,
            "CoinGecko ID": coin_id
        })

    df = pd.DataFrame(final)
    df.to_csv(OUTPUT_FILENAME, index=False)

    print(f"\n🎉 Done! Saved {len(df)} entries to {OUTPUT_FILENAME}")


if __name__ == "__main__":
    main()
