"""
Configuration for the Topological Arbitrage System.
"""

# --- Tickers ---
TICKERS = [
    'NEE',      # NextEra Energy (largest US utility)
    'D',        # Dominion Energy
    'DUK',      # Duke Energy
    'SO',       # Southern Company
    'AEP',      # American Electric Power
    'XEL',      # Xcel Energy
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
TRANSACTION_COST_BPS = 0.0003
REBALANCE_FREQUENCY = 10

# --- Risk ---
LEVERAGE_MULTIPLIER = 1.0
STOP_LOSS_PCT = 0.05
MAX_DRAWDOWN_LIMIT = 0.15

