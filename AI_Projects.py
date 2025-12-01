import requests
import pandas as pd
import time
import sys
import os

# --- CONFIGURATION ---
# 1. FIX: Read the value into a more descriptive local variable name
CG_API_KEY_VALUE = os.environ.get("CG_API_KEY") # Reads directly from GitHub Secret

# The base URL for the CoinGecko Pro API
API_BASE_URL = 'https://pro-api.coingecko.com/api/v3'
CATEGORY_ID = 'artificial-intelligence'
OUTPUT_FILENAME = 'AI_Projects.csv'

# API headers for authentication
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
    # 2. FIX: Use the new variable name in the header
    'x-cg-pro-api-key': CG_API_KEY_VALUE, 
}
# ---------------------

def fetch_coin_details(coin_id):
    """Fetches full coin details, including the official X (Twitter) handle, using the API."""
    detail_url = f'{API_BASE_URL}/coins/{coin_id}'
    
    time.sleep(0.3) 
    
    try:
        response = requests.get(detail_url, headers=HEADERS, timeout=15)
        response.raise_for_status()
        details = response.json()

        twitter_handle = details.get('links', {}).get('twitter_screen_name', None)
        
        return f'@{twitter_handle}' if twitter_handle else 'N/A'
        
    except requests.exceptions.RequestException as e:
        print(f"  [Error] Failed to fetch details for {coin_id} via API: {e}")
        return 'FETCH_ERROR'

def main_scraper():
    # 3. FIX: Check if the key is actually missing (None or empty string)
    if not CG_API_KEY_VALUE:
        print("❌ ERROR: CG_API_KEY environment variable is missing or empty. Please check your GitHub Secrets.")
        sys.exit(1)
        
    print("--- 🚀 Starting CoinGecko AI Social Data Scraper (PAID API) ---")
    
    # 1. Get List of Coins in the Category (using Pro API markets endpoint)
    api_markets_url = f'{API_BASE_URL}/coins/markets'
    api_params = {
        'vs_currency': 'usd',
        'category': CATEGORY_ID,
        'per_page': 250,
        'page': 1,
        'order': 'market_cap_desc'
    }

    try:
        print("1/2: Fetching list of all project IDs in the category...")
        response = requests.get(api_markets_url, headers=HEADERS, params=api_params, timeout=20)
        response.raise_for_status() # This is where the 401 error originates if the key is bad/missing
        data = response.json()
        
        if not data:
            print("❌ API returned empty data list.")
            return

        projects = []
        for item in data:
            projects.append({
                'ID': item.get('id'),
                'Project Name': item.get('name'),
                'Ticker': item.get('symbol').upper(),
            })
            
        print(f"✅ Found {len(projects)} projects.")

    except requests.exceptions.RequestException as e:
        print(f"❌ Critical API Error while fetching market list: {e}")
        sys.exit(1)
    
    # 2. Iterate and fetch details (X username) for each project (API calls)
    final_data = []
    print("2/2: Fetching X username for each project...")
    
    for i, project in enumerate(projects):
        
        progress = f"[{i+1}/{len(projects)}]"
        print(f"{progress} Processing: {project['Project Name']} ({project['Ticker']})", end='\r', flush=True)
        
        x_username = fetch_coin_details(project['ID'])
        
        final_data.append({
            'Project Name': project['Project Name'],
            'Ticker': project['Ticker'],
            'X Username': x_username
        })
    
    print("\n✅ Detail fetching complete.")
    
    # 3. Save to CSV
    df = pd.DataFrame(final_data)
    
    df.to_csv(OUTPUT_FILENAME, index=False)
    print(f"\n🎉 Success! Data saved to **{OUTPUT_FILENAME}**")


if __name__ == "__main__":
    main_scraper()
