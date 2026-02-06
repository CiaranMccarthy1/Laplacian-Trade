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
    # 11 Major GICS Sectors - Commented out lower-performing sectors
    'SECTOR_COMMUNICATION': ['GOOGL', 'META', 'NFLX', 'DIS', 'CMCSA', 'TMUS', 'VZ', 'T', 'CHTR', 'WBD', 'PARA', 'LYV', 'FOXA'], 
    'SECTOR_CONSUMER_DISC': ['AMZN', 'TSLA', 'HD', 'MCD', 'NKE', 'LOW', 'BKNG', 'SBUX', 'TJX', 'TGT', 'ORLY', 'MAR', 'F', 'GM'],
    'SECTOR_CONSUMER_STAPLES': ['PG', 'COST', 'PEP', 'KO', 'WMT', 'PM', 'MO', 'CL', 'KDP', 'GIS', 'SYY', 'STZ', 'EL', 'ADM'],
    'SECTOR_ENERGY': ['XOM', 'CVX', 'COP', 'SLB', 'EOG', 'MPC', 'PSX', 'VLO', 'OXY', 'HES', 'HAL', 'DVN', 'KMI', 'WMB'],
    'SECTOR_FINANCIALS': ['BRK-B', 'JPM', 'V', 'MA', 'BAC', 'WFC', 'MS', 'GS', 'BLK', 'C', 'AXP', 'PYPL', 'SCHW', 'PGR', 'CB'],
    'SECTOR_HEALTHCARE': ['LLY', 'UNH', 'JNJ', 'MRK', 'ABBV', 'TMO', 'AMGN', 'PFE', 'ISRG', 'DHR', 'BMY', 'GILD', 'VRTX', 'SYK', 'ELV'], 
    'SECTOR_INDUSTRIALS': ['CAT', 'GE', 'UNP', 'HON', 'BA', 'UPS', 'RTX', 'DE', 'LMT', 'ETN', 'FDX', 'MMM', 'NSC', 'WM', 'EMR'],
    'SECTOR_X_TECH': ['MSFT', 'AAPL', 'NVDA', 'AVGO', 'ORCL', 'ADBE', 'CRM', 'AMD', 'QCOM', 'TXN', 'INTC', 'IBM', 'NOW', 'AMAT', 'LRCX'],
    # 'SECTOR_MATERIALS': ['LIN', 'SHW', 'FCX', 'CTVA', 'ECL', 'APD', 'NEM', 'DOW', 'PPG', 'NUE', 'ALB', 'MLM', 'VMC', 'NEM'],  # Often cyclical/volatile
    # 'SECTOR_REAL_ESTATE': ['PLD', 'AMT', 'EQIX', 'WELL', 'PSA', 'CCI', 'DLR', 'SPG', 'O', 'VICI', 'SBAC', 'CBRE', 'WY', 'AVB', 'ARE'],  # Interest rate sensitive
    # 'SECTOR_UTILITIES': ['NEE', 'SO', 'DUK', 'CEG', 'AEP', 'SRE', 'D', 'EXC', 'XEL', 'PEG', 'ED', 'PCG', 'VST', 'FE', 'ETR'],  # Low growth/defensive

    # full s&p 500 
    # filled dynamically
    'S_AND_P_FULL': [],
}

ACTIVE_TICKER_SET = 'DEFAULT'
TICKERS = TICKER_SETS[ACTIVE_TICKER_SET]

BACKTEST_PERIOD = '5y'
TIMEFRAME = '1d'
LOOKBACK_WINDOW = 160

ALPHA = 0.65    
CORRELATION_THRESHOLD = 0.7

MAX_DIMENSION = 2
REGIME_WINDOW = 10

NET_EXPOSURE = 0.7

TRANSACTION_COST_BPS = 0.0010
REBALANCE_FREQUENCY = 10

RISK_MODE = 'STANDARD'

RISK_PROFILES = {
    'HYPER_AGGRESSIVE': {    # For high-risk proprietary trading / very short-term leverage strategies
        'STOP_LOSS_PCT': 0.15,
        'MAX_DRAWDOWN_LIMIT': 0.50,
        'LEVERAGE_MULTIPLIER': 3.0,
    },
    'AGGRESSIVE': {          # Aggressive behaviour
        'STOP_LOSS_PCT': 0.05,
        'MAX_DRAWDOWN_LIMIT': 0.25,
        'LEVERAGE_MULTIPLIER': 1.5,
    },
    'GROWTH': {              # Growth-oriented retail investors
        'STOP_LOSS_PCT': 0.07,
        'MAX_DRAWDOWN_LIMIT': 0.30,
        'LEVERAGE_MULTIPLIER': 2.0,
    },
    'STANDARD': {            # Default balanced retail
        'STOP_LOSS_PCT': 0.02,
        'MAX_DRAWDOWN_LIMIT': 0.05,
        'LEVERAGE_MULTIPLIER': 1.0,
    },
    'BALANCED': {            # Slightly more conservative than standard
        'STOP_LOSS_PCT': 0.03,
        'MAX_DRAWDOWN_LIMIT': 0.08,
        'LEVERAGE_MULTIPLIER': 1.0,
    },
    'INSTITUTIONAL': {       # Endowments / institutions with longer horizons
        'STOP_LOSS_PCT': 0.03,
        'MAX_DRAWDOWN_LIMIT': 0.15,
        'LEVERAGE_MULTIPLIER': 1.2,
    },
    'PENSION_FUND': {        # Very conservative, capital preservation focussed
        'STOP_LOSS_PCT': 0.01,
        'MAX_DRAWDOWN_LIMIT': 0.10,
        'LEVERAGE_MULTIPLIER': 0.25,
    },
    'CONSERVATIVE': {        # Conservative retail / near-retiree
        'STOP_LOSS_PCT': 0.01,
        'MAX_DRAWDOWN_LIMIT': 0.03,
        'LEVERAGE_MULTIPLIER': 0.25,
    },
    'ULTRA_CONSERVATIVE': {  # Capital preservation, no leverage
        'STOP_LOSS_PCT': 0.005,
        'MAX_DRAWDOWN_LIMIT': 0.01,
        'LEVERAGE_MULTIPLIER': 0.0,
    },
    'CAUTIOUS': {            # Cautious
        'STOP_LOSS_PCT': 0.01,
        'MAX_DRAWDOWN_LIMIT': 0.02,
        'LEVERAGE_MULTIPLIER': 0.5,
    }
}

STOP_LOSS_PCT = RISK_PROFILES[RISK_MODE]['STOP_LOSS_PCT']
MAX_DRAWDOWN_LIMIT = RISK_PROFILES[RISK_MODE]['MAX_DRAWDOWN_LIMIT']

# Monte Carlo Simulation Parameters
MC_SIMULATIONS = 1000
MC_HORIZON_DAYS = 252
MC_CONFIDENCE_LEVEL = 0.95
