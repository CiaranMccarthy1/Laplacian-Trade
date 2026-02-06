import yfinance as yf
import pandas as pd

tickers = ['BBBYQ', 'SHLDQ', 'SIVBQ', 'FRCB', 'CS', 'TWTR', 'SBNY', 'LEH', 'ENE']
print(f"Testing fetch for: {tickers}")

data = yf.download(tickers, period='5y', group_by='ticker', progress=False)

for t in tickers:
    if t in data.columns.levels[0]:
        df = data[t]['Close'].dropna()
        if not df.empty:
            print(f"{t}: Found {len(df)} rows. Last: {df.index[-1]}")
        else:
            print(f"{t}: Empty")
    else:
        print(f"{t}: Not in columns")
