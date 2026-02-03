import os
from dotenv import load_dotenv

load_dotenv()

DATA_SOURCE = 'YFINANCE'

TICKER_SETS = {
    'DEFAULT': [
        'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA',
        'JPM', 'BAC', 'GS', 'MS',
        'XOM', 'CVX',
        'JNJ', 'PFE',
    ],
    'TECH': 
    ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA', 'AMD', 'INTC', 'CRM'],
    'FINANCE': 
    ['JPM', 'BAC', 'GS', 'MS', 'WFC', 'C', 'BLK', 'AXP'],
    'ENERGY': 
    ['XOM', 'CVX', 'COP', 'SLB', 'EOG', 'MPC', 'PSX'],
    'S_AND_P_SAMPLE': [
        'AAPL', 'MSFT', 'AMZN', 'NVDA', 'GOOGL', 'META', 'TSLA', 'BRK-B', 'LLY', 'V',
        'UNH', 'AVGO', 'JPM', 'XOM', 'MA', 'JNJ', 'PG', 'HD', 'COST', 'ABBV'
    ],
    'S_AND_P_FULL': [],
    'S_AND_P_SURVIVOR_FREE': [
        'FRCB', 'SBNY',
        'AAPL', 'MSFT', 'AMZN', 'NVDA', 'GOOGL', 'META', 'TSLA', 'BRK-B', 'LLY', 'V',
        'UNH', 'AVGO', 'JPM', 'XOM', 'MA', 'JNJ', 'PG', 'HD', 'COST', 'ABBV',
        'C', 'BAC', 'AIG',
    ]
}

ACTIVE_TICKER_SET = 'S_AND_P_SURVIVOR_FREE'
TICKERS = TICKER_SETS[ACTIVE_TICKER_SET]

BACKTEST_PERIOD = '10y'
TIMEFRAME = '1d'
LOOKBACK_WINDOW = 120

ALPHA = 0.5
CORRELATION_THRESHOLD = 0.6

MAX_DIMENSION = 2
REGIME_WINDOW = 10

NET_EXPOSURE = 0.5

TRANSACTION_COST_BPS = 0.0010
REBALANCE_FREQUENCY = 5

RISK_MODE = 'AGGRESSIVE'

RISK_PROFILES = {
    'AGGRESSIVE': {
        'STOP_LOSS_PCT': 0.05,
        'MAX_DRAWDOWN_LIMIT': 0.25,
        'LEVERAGE_MULTIPLIER': 1.5,
    },
    'STANDARD': {
        'STOP_LOSS_PCT': 0.02,
        'MAX_DRAWDOWN_LIMIT': 0.05,
        'LEVERAGE_MULTIPLIER': 1.0,
    },
    'CAUTIOUS': {
        'STOP_LOSS_PCT': 0.01,
        'MAX_DRAWDOWN_LIMIT': 0.02,
        'LEVERAGE_MULTIPLIER': 0.5,
    }
}

STOP_LOSS_PCT = RISK_PROFILES[RISK_MODE]['STOP_LOSS_PCT']
MAX_DRAWDOWN_LIMIT = RISK_PROFILES[RISK_MODE]['MAX_DRAWDOWN_LIMIT']
