"""
Configuration for the Topological Arbitrage System.
"""

# --- Tickers ---
TICKERS = [
    'CVX', 
    'NEE', 
    'DUK',
    'SO',
    'AAPL',
    'MSFT', 
    'NVDA', 
    'AMD',
    'JPM', 
    'GS',
    'JNJ',
    'PFE', 
    'UNH',
    'AMZN', 
    'MCD',
    'PG', 
    'CAT',
    'GOOGL', 
    'META'
]


# --- Data ---
TIMEFRAME = '1d'
BACKTEST_PERIOD = '20y'
LOOKBACK_WINDOW = 80

# --- Spatial Graph ---
ALPHA = 0.3
CORRELATION_THRESHOLD = 0.45

# --- Topological ---
MAX_DIMENSION = 3

# --- Trading ---
TRANSACTION_COST_BPS = 0.001
REBALANCE_FREQUENCY = 20

MONTE_CARLO_SAMPLES = 100

# --- Risk ---
LEVERAGE_MULTIPLIER = 1
STOP_LOSS_PCT = 0.05
MAX_DRAWDOWN_LIMIT = 0.15

