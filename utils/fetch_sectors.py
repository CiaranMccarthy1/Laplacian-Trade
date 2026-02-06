
import pandas as pd
import requests
from io import StringIO
import ssl

# Handle SSL certificate verification issues
ssl._create_default_https_context = ssl._create_unverified_context

def fetch_sector_map():
    url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        # Parse HTML from response content
        tables = pd.read_html(StringIO(response.text))
        df = tables[0]
        
        # Verify columns exist
        if 'Symbol' not in df.columns or 'GICS Sector' not in df.columns:
            print("Error: Table structure changed. Columns found:", df.columns)
            return

        sector_map = {}
        for sector, group in df.groupby('GICS Sector'):
            sector_key = f"SECTOR_{sector.upper().replace(' ', '_').replace('INFORMATION_TECHNOLOGY', 'X_TECH')}"
            tickers = group['Symbol'].tolist()
            # Clean tickers (replace . with -)
            tickers = [t.replace('.', '-') for t in tickers]
            sector_map[sector_key] = tickers
            
        return sector_map

    except Exception as e:
        print(f"Error fetching data: {e}")
        return None

if __name__ == "__main__":
    sectors = fetch_sector_map()
    if sectors:
        print("Scraping successful. Generated config entries:")
        print("-" * 20)
        for sector, tickers in sectors.items():
            print(f"    '{sector}': {tickers},")
    else:
        print("Failed to scrape sectors.")
