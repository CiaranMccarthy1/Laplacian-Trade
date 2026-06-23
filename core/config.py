"""
Configuration for the Topological Arbitrage System.
"""

# --- Tickers ---
TICKERS = [
    'XLE',
    'XOM',
    'VLO',
    'UNG',
    'GLD',
    'SLV',
    'FCX',
    'NEM',
    'DBA',
    'ADM',
    'NTR',
    'CAT',
    'DE',
    'NVDA',
    'MSFT',
    'AAPL',
    'TSLA'
]

# --- Data ---
TIMEFRAME = '1d'
BACKTEST_PERIOD = '10y'
LOOKBACK_WINDOW = 80

# --- Spatial Graph ---
ALPHA = 0.3
CORRELATION_THRESHOLD = 0.45

# --- Topological ---
MAX_DIMENSION = 3

# --- Trading ---
TRANSACTION_COST_BPS = 0.0003
REBALANCE_FREQUENCY = 10

# --- Risk ---
LEVERAGE_MULTIPLIER = 1.0
