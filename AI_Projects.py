import requests
import pandas as pd
from bs4 import BeautifulSoup
import time
import sys

# --- CONFIGURATION ---
CATEGORY_ID = 'artificial-intelligence'
API_URL = f'https://api.coingecko.com/api/v3/coins/markets'
API_PARAMS = {
    'vs_currency': 'usd',
    'category': CATEGORY_ID,
    'per_page': 250,  # Max number of coins to fetch
    'page': 1,
    'order': 'market_cap_desc'
}
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
}
OUTPUT_FILENAME = 'ai_crypto_social_data.csv'
# ---------------------

def get_x_username(coin_id):
    """Fetches the specific CoinGecko page and extracts the X (Twitter) username."""
    detail_url = f'https://www.coingecko.com/en/coins/{coin_id}'
    
    # Be polite to the server
    time.sleep(1) 
    
    try:
        detail_response = requests.get(detail_url, headers=HEADERS, timeout=10)
        detail_response.raise_for_status()
        
        soup = BeautifulSoup(detail_response.text, 'html.parser')
        
        # Target the Twitter link based on common structure near social links
        # Look for links that contain 'twitter.com'
        x_link_tag = soup.find('a', href=lambda href: href and 'twitter.com' in href)
        
        if x_link_tag and x_link_tag.get('href'):
            # The URL is typically 'https://twitter.com/username'
            x_url = x_link_tag['href']
            # Extract the username (the path segment after the domain)
            username = x_url.split('/')[-1]
            return username
        
        return 'N/A'
        
    except requests.exceptions.RequestException as e:
        # 404, 429, or other request errors
        print(f"  [Error] Failed to fetch {coin_id}: {e}")
        return 'FETCH_ERROR'

def main_scraper():
    print("--- 🚀 Starting CoinGecko AI Category Scraper ---")
    
    # 1. Fetch main list of coins via CoinGecko API
    try:
        print(f"1/2: Fetching list of projects from the API...")
        response = requests.get(API_URL, headers=HEADERS, params=API_PARAMS, timeout=20)
        response.raise_for_status()
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
                'X Username': None # Placeholder for scraping
            })
            
        print(f"✅ Found {len(projects)} projects.")

    except requests.exceptions.RequestException as e:
        print(f"❌ Critical API Error: Could not fetch initial project list. {e}")
        sys.exit(1)
    
    # 2. Iterate and scrape X (Twitter) username for each project
    print("2/2: Scraping X username for each project...")
    
    for i, project in enumerate(projects):
        # Calculate progress and print status
        progress = f"[{i+1}/{len(projects)}]"
        print(f"{progress} Scraping: {project['Project Name']} ({project['Ticker']})", end='\r', flush=True)
        
        # Pass the unique coin ID (e.g., 'render-token') to the helper function
        username = get_x_username(project['ID'])
        
        # Save the result
        project['X Username'] = f'@{username}' if username not in ('N/A', 'FETCH_ERROR') else username
    
    print("\n✅ Scraping complete.")
    
    # 3. Save to CSV
    df = pd.DataFrame(projects)
    # Remove the internal CoinGecko ID from the final output
    df.drop(columns=['ID'], inplace=True) 
    
    df.to_csv(OUTPUT_FILENAME, index=False)
    print(f"\n🎉 Success! Data saved to **{OUTPUT_FILENAME}**")


if __name__ == "__main__":
    main_scraper()
