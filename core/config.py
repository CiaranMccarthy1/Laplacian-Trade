"""
Configuration for the Topological Arbitrage System.
"""

# --- Tickers ---
TICKERS = [
    'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA',
    'JPM', 'BAC', 'GS', 'MS',
    'XOM', 'CVX',
    'JNJ', 'PFE',
]

# --- Data ---
TIMEFRAME = '1d'
BACKTEST_PERIOD = '5y'
LOOKBACK_WINDOW = 80

# --- Spatial Graph ---
ALPHA = 0.3
CORRELATION_THRESHOLD = 0.7

# --- Topological ---
MAX_DIMENSION = 3

# --- Trading ---
NET_EXPOSURE = 0.7
TRANSACTION_COST_BPS = 0.0010
REBALANCE_FREQUENCY = 10

# --- Risk ---
STOP_LOSS_PCT = 0.02
MAX_DRAWDOWN_LIMIT = 0.05
LEVERAGE_MULTIPLIER = 1.0

# --- Monte Carlo ---
MC_SIMULATIONS = 1000
MC_HORIZON_DAYS = 252 * int(BACKTEST_PERIOD[:-1])
MC_CONFIDENCE_LEVEL = 0.95
