import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Optional
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core import config

class DataFetcher:
    def __init__(self, tickers: List[str] = config.TICKERS, interval: str = config.TIMEFRAME):
        self.interval = interval
        self.buffer = pd.DataFrame()
        
        if not tickers and config.ACTIVE_TICKER_SET == 'S_AND_P_FULL':
            self.tickers = self.fetch_sp500_tickers()
            print(f"DataFetcher: Loaded {len(self.tickers)} S&P 500 tickers (lazy load).")
        else:
            self.tickers = tickers

    @staticmethod
    def fetch_sp500_tickers() -> List[str]:
        """
        Returns a hardcoded list of S&P 500 tickers relative to early 2024.
        This ensures stability for backtesting without relying on external scraping or API filtering.
        """
        tickers = [
            'FRCB', 'SBNY', 'SIVBQ', 
            'AIG', 'C', 'BAC', 
            'MMM', 'AOS', 'ABT', 'ABBV', 'ACN', 'ADBE', 'AMD', 'AES', 'AFL', 'A', 'APD', 'ABNB', 'AKAM', 'ALB', 'ARE', 'ALGN', 'ALLE', 'LNT', 'ALL', 'GOOGL', 'GOOG', 'MO', 'AMZN', 'AMCR', 'AEE', 'AAL', 'AEP', 'AXP', 'AIG', 'AMT', 'AWK', 'AMP', 'AME', 'AMGN', 'APH', 'ADI', 'AON', 'APA', 'AAPL', 'AMAT', 'APTV', 'ACGL', 'ADM', 'ANET', 'AJG', 'AIZ', 'T', 'ATO', 'ADSK', 'ADP', 'AZO', 'AVB', 'AVY', 'AXON', 'BKR', 'BALL', 'BAC', 'BK', 'BBWI', 'BAX', 'BDX', 'BRK.B', 'BBY', 'BIO', 'TECH', 'BIIB', 'BLK', 'BX', 'BA', 'BKNG', 'BWA', 'BXP', 'BSX', 'BMY', 'AVGO', 'BR', 'BRO', 'BF.B', 'BG', 'BLDR', 'CHRW', 'CDNS', 'CZR', 'CPT', 'CPB', 'COF', 'CAH', 'KMX', 'CCL', 'CARR', 'CAT', 'CBOE', 'CBRE', 'CDW', 'CE', 'COR', 'CNC', 'CNP', 'CF', 'CHTR', 'CVX', 'CMG', 'CB', 'CHD', 'CI', 'CINF', 'CTAS', 'CSCO', 'C', 'CFG', 'CLX', 'CME', 'CMS', 'KO', 'CTSH', 'CL', 'CMCSA', 'CMA', 'CAG', 'COP', 'ED', 'STZ', 'CEG', 'COO', 'CPRT', 'GLW', 'CTVA', 'CSGP', 'COST', 'CTRA', 'CCI', 'CSX', 'CMI', 'CVS', 'DHI', 'DAN', 'DAR', 'DRI', 'DVA', 'DE', 'DAL', 'XRAY', 'DVN', 'DXCM', 'FANG', 'DLR', 'DG', 'DLTR', 'D', 'DPZ', 'DOV', 'DOW', 'DTE', 'DUK', 'DD', 'EMN', 'ETN', 'EBAY', 'ECL', 'EIX', 'EW', 'EA', 'ELV', 'LLY', 'EMR', 'ENPH', 'ETR', 'EOG', 'EPAM', 'EQT', 'EFX', 'EQIX', 'EQR', 'ESS', 'EL', 'ETSY', 'EG', 'EVRG', 'ES', 'EXC', 'EXPE', 'EXPD', 'EXR', 'XOM', 'FFIV', 'F', 'FAST', 'FRT', 'FDX', 'FIS', 'FITB', 'FSLR', 'FE', 'FMC', 'FTNT', 'FTV', 'FOXA', 'FOX', 'BEN', 'FCX', 'GRMN', 'IT', 'GE', 'GEHC', 'GEN', 'GNRC', 'GD', 'GIS', 'GM', 'GPC', 'GILD', 'GPN', 'GL', 'GS', 'HAL', 'HIG', 'HAS', 'HCA', 'HSIC', 'HSY', 'HPE', 'HLT', 'HOLX', 'HD', 'HON', 'HRL', 'HST', 'HWM', 'HPQ', 'HUBB', 'HUM', 'HBAN', 'HII', 'IBM', 'IEX', 'IDXX', 'ITW', 'ILMN', 'INCY', 'IR', 'INTC', 'ICE', 'IP', 'IFF', 'INTU', 'ISRG', 'IVZ', 'INVH', 'IQV', 'IRM', 'JBHT', 'JBL', 'JKHY', 'J', 'JNJ', 'JCI', 'JPM', 'K', 'KVUE', 'KDP', 'KEY', 'KEYS', 'KMB', 'KIM', 'KMI', 'KLAC', 'KHC', 'KR', 'LHX', 'LH', 'LRCX', 'LW', 'LVS', 'LDOS', 'LEN', 'LIN', 'LYV', 'LKQ', 'LMT', 'L', 'LOW', 'LULU', 'LYB', 'MTB', 'MPC', 'MKTX', 'MAR', 'MMC', 'MLM', 'MAS', 'MA', 'MTCH', 'MKC', 'MCD', 'MCK', 'MDT', 'MRK', 'META', 'MET', 'MTD', 'MGM', 'MCHP', 'MU', 'MSFT', 'MAA', 'MRNA', 'MHK', 'MOH', 'TAP', 'MDLZ', 'MPWR', 'MNST', 'MCO', 'MS', 'MOS', 'MSI', 'MSCI', 'NDAQ', 'NTAP', 'NFLX', 'NEM', 'NWSA', 'NWS', 'NEE', 'NKE', 'NI', 'NDSN', 'NSC', 'NTRS', 'NOC', 'NCLH', 'NRG', 'NUE', 'NVDA', 'NVR', 'NXPI', 'ORLY', 'OXY', 'ODFL', 'OMC', 'ON', 'OKE', 'ORCL', 'OTIS', 'PCAR', 'PKG', 'PANW', 'PH', 'PAYX', 'PAYC', 'PYPL', 'PNR', 'PEP', 'PFE', 'PCG', 'PM', 'PSX', 'PNW', 'PNC', 'POOL', 'PPG', 'PPL', 'PFG', 'PG', 'PGR', 'PLD', 'PRU', 'PEG', 'PTC', 'PSA', 'PHM', 'QRVO', 'PWR', 'QCOM', 'DGX', 'RL', 'RJF', 'RTX', 'O', 'REG', 'REGN', 'RF', 'RSG', 'RMD', 'RVTY', 'RHI', 'ROK', 'ROL', 'ROP', 'ROST', 'RCL', 'SPGI', 'CRM', 'SBAC', 'SLB', 'STX', 'SEE', 'SRE', 'NOW', 'SHW', 'SPG', 'SWKS', 'SJM', 'SNA', 'SEDG', 'SO', 'LUV', 'SWK', 'SBUX', 'STT', 'STLD', 'STE', 'SYK', 'SYF', 'SNPS', 'SYY', 'TMUS', 'TROW', 'TTWO', 'TPR', 'TRGP', 'TGT', 'TEL', 'TDY', 'TFX', 'TER', 'TSLA', 'TXN', 'TXT', 'TMO', 'TJX', 'TSCO', 'TT', 'TDG', 'TRV', 'TRMB', 'TFC', 'TYL', 'TSN', 'USB', 'UBER', 'UDR', 'ULTA', 'UNP', 'UAL', 'UPS', 'URI', 'UNH', 'UHS', 'VLO', 'VTR', 'VRSN', 'VRSK', 'VZ', 'VRTX', 'VFC', 'VTRS', 'VICI', 'V', 'VMC', 'WAB', 'WMT', 'DIS', 'WBD', 'WM', 'WAT', 'WEC', 'WFC', 'WELL', 'WST', 'WDC', 'WY', 'WHR', 'WMB', 'WTW', 'GWW', 'WYNN', 'XEL', 'XYL', 'YUM', 'ZBRA', 'ZBH', 'ZION', 'ZTS'
        ]
        
        if config.DATA_SOURCE == 'ALPACA':
             tickers = [t.replace('-', '.') for t in tickers]
        else:
             tickers = [t.replace('.', '-') for t in tickers]
             
        return tickers

    def is_market_open(self) -> bool:
        """
        Checks if markets are open.
        """
        if config.DATA_SOURCE == 'ALPACA' and self.alpaca:
            try:
                clock = self.alpaca.get_clock()
                return clock.is_open
            except Exception as e:
                print(f"Alpaca Clock Error: {e}")
                return True
                
        try:
            from datetime import timezone
            import pytz
            utc_now = datetime.now(timezone.utc)
            eastern = pytz.timezone('US/Eastern')
            et_now = utc_now.astimezone(eastern)
            
            if et_now.weekday() > 4:
                return False
                
            current_time = et_now.time()
            market_open = datetime.strptime("09:30", "%H:%M").time()
            market_close = datetime.strptime("16:00", "%H:%M").time()
            
            if market_open <= current_time <= market_close:
                return True
            return False
        except:
             return True

    def fetch_data(self, lookback_minutes: int = config.LOOKBACK_WINDOW) -> pd.DataFrame:
        """
        Fetches the last N minutes of data for all tickers.
        """
        market_open = self.is_market_open()
        
        end_time = datetime.now()
        start_time = end_time - timedelta(minutes=lookback_minutes * 2) 
        
        try:
            data = pd.DataFrame()
            
            if market_open:
                data = yf.download(
                    tickers=self.tickers,
                    start=start_time,
                    end=end_time,
                    interval=self.interval,
                    group_by='ticker',
                    threads=True,
                    progress=False
                )
            else:
                 print("\n[Market Closed] Skipping live fetch. Fetching historical context (5d)...")
            
            if data.empty:
                if market_open:
                     print("Warning: No data found for specified window. Attempting fallback.")
                
                data = yf.download(
                    tickers=self.tickers,
                    period="5d",
                    interval=self.interval,
                    group_by='ticker',
                    threads=True,
                    progress=False
                )

            if data.empty:
                return pd.DataFrame()

            df_close = pd.DataFrame()
            
            if len(self.tickers) == 1:
                df_close[self.tickers[0]] = data['Close']
            else:
                for ticker in self.tickers:
                    try:
                        if isinstance(data.columns, pd.MultiIndex):
                            if (ticker, 'Close') in data.columns:
                                df_close[ticker] = data[(ticker, 'Close')]
                            elif ticker in data.columns.levels[0]:
                                try:
                                    df_close[ticker] = data[ticker]['Close']
                                except: pass
                        elif f"Close_{ticker}" in data.columns:
                             df_close[ticker] = data[f"Close_{ticker}"]
                    except KeyError:
                        print(f"Warning: Could not extract data for {ticker}")

            df_close = df_close.ffill().dropna()
            
            if len(df_close) > lookback_minutes:
                df_close = df_close.iloc[-lookback_minutes:]
                
            self.buffer = df_close
            return df_close

        except Exception as e:
            print(f"Error fetching data: {e}")
            return pd.DataFrame()

    def get_returns(self) -> pd.DataFrame:
        """
        Calculates log returns from the current buffer.
        """
        if self.buffer.empty:
            return pd.DataFrame()
        
        return np.log(self.buffer / self.buffer.shift(1)).dropna()

    def fetch_historical_data(self, period: str = '2y') -> pd.DataFrame:
        """
        Fetches historical data for a specified period (e.g., '1y', '2y', '5y')
        independent of the live trading lookback window.
        """
        try:
            print(f"Fetching historical data for period: {period}...")
            data = yf.download(
                tickers=self.tickers,
                period=period,
                interval='1d',
                group_by='ticker',
                threads=True,
                progress=False
            )
            
            if data.empty:
                print("Warning: No historical data returned.")
                return pd.DataFrame()

            df_close = pd.DataFrame()
            
            # Handle single ticker vs multiple tickers
            if len(self.tickers) == 1:
                # For single ticker, data columns are 'Open', 'High', etc.
                # 'Close' is just a series/column
                if 'Close' in data.columns:
                    df_close[self.tickers[0]] = data['Close']
            else:
                for ticker in self.tickers:
                    try:
                        # yfinance structure varies by version and request
                        # MultiIndex (Ticker, OHLC)
                        if isinstance(data.columns, pd.MultiIndex):
                            if (ticker, 'Close') in data.columns:
                                df_close[ticker] = data[(ticker, 'Close')]
                        # Flat columns 'Close_TICKER' (less common now but possible)
                        elif f"Close_{ticker}" in data.columns:
                             df_close[ticker] = data[f"Close_{ticker}"]
                    except KeyError:
                        pass

            # Drop tickers with no data
            df_close = df_close.dropna(axis=1, how='all')
            # Fill forward then backward to handle different start dates or holidays
            df_close = df_close.ffill().bfill()
            
            self.buffer = df_close
            return df_close

        except Exception as e:
            print(f"Error fetching historical data: {e}")
            return pd.DataFrame()

if __name__ == "__main__":
    fetcher = DataFetcher()
    df = fetcher.fetch_data(lookback_minutes=60)
    print("Data Shape:", df.shape)
    print(df.head())
    returns = fetcher.get_returns()
    print("Returns Shape:", returns.shape)
