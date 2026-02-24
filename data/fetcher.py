import yfinance as yf
import pandas as pd
import numpy as np
from typing import List
from core import config


class DataFetcher:
    def __init__(self, tickers: List[str] = None, interval: str = config.TIMEFRAME):
        self.tickers = tickers or config.TICKERS
        self.interval = interval
        self.buffer = pd.DataFrame()

    def fetch_data(self, lookback_minutes: int = config.LOOKBACK_WINDOW) -> pd.DataFrame:
        """Fetch recent price data for all tickers via yfinance."""
        try:
            data = yf.download(
                tickers=self.tickers,
                period='5d',
                interval=self.interval,
                group_by='ticker',
                threads=True,
                progress=False,
            )

            if data.empty:
                return pd.DataFrame()

            df_close = self._extract_close(data)
            df_close = df_close.ffill().dropna()

            if len(df_close) > lookback_minutes:
                df_close = df_close.iloc[-lookback_minutes:]

            self.buffer = df_close
            return df_close

        except Exception as e:
            print(f"Error fetching data: {e}")
            return pd.DataFrame()

    def fetch_historical_data(self, period: str = config.BACKTEST_PERIOD) -> pd.DataFrame:
        """Fetch longer-term historical daily close prices."""
        try:
            data = yf.download(
                tickers=self.tickers,
                period=period,
                interval='1d',
                group_by='ticker',
                threads=True,
                progress=False,
            )

            if data.empty:
                return pd.DataFrame()

            df_close = self._extract_close(data)
            df_close = df_close.dropna(axis=1, how='all').ffill().bfill()
            self.buffer = df_close
            return df_close

        except Exception as e:
            print(f"Error fetching historical data: {e}")
            return pd.DataFrame()

    def get_returns(self) -> pd.DataFrame:
        """Calculate log returns from the current buffer."""
        if self.buffer.empty:
            return pd.DataFrame()
        return np.log(self.buffer / self.buffer.shift(1)).dropna()

    # ------------------------------------------------------------------
    def _extract_close(self, data: pd.DataFrame) -> pd.DataFrame:
        """Pull 'Close' prices out of a yfinance download DataFrame."""
        df_close = pd.DataFrame()

        if len(self.tickers) == 1:
            if 'Close' in data.columns:
                df_close[self.tickers[0]] = data['Close']
            return df_close

        for ticker in self.tickers:
            try:
                if isinstance(data.columns, pd.MultiIndex):
                    if (ticker, 'Close') in data.columns:
                        df_close[ticker] = data[(ticker, 'Close')]
                elif f"Close_{ticker}" in data.columns:
                    df_close[ticker] = data[f"Close_{ticker}"]
            except KeyError:
                pass

        return df_close

if __name__ == "__main__":
    fetcher = DataFetcher()
    df = fetcher.fetch_data(lookback_minutes=60)
    print("Data Shape:", df.shape)
    print(df.head())
    returns = fetcher.get_returns()
    print("Returns Shape:", returns.shape)
