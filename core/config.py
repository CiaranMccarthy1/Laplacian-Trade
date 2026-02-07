"""
Global configuration for the Topological Arbitrage Trading System.

Defines ticker sets (optimized allocation tiers plus individual GICS sectors),
backtest parameters, risk profiles, and Monte Carlo simulation settings.
All values are derived from 20-year Monte Carlo risk analysis and
grid-search parameter optimization.
"""

import os
from dotenv import load_dotenv

load_dotenv()

DATA_SOURCE = 'YFINANCE'

TICKER_SETS = {
    'DEFAULT_MIXED': [
        'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA',
        'JPM', 'BAC', 'GS', 'MS',
        'XOM', 'CVX',
        'JNJ', 'PFE',
    ],

    'DEFENSIVE_CORE_45PCT': [
        'NEE', 'SO', 'DUK', 'CEG', 'AEP', 'SRE', 'D', 'EXC',
        'CAT', 'GE', 'UNP', 'HON', 'BA', 'UPS', 'RTX', 'DE', 'LMT', 'ETN'
    ],

    'GROWTH_ENGINE_30PCT': [
        'MSFT', 'AAPL', 'NVDA', 'AVGO', 'ORCL', 'ADBE', 'CRM', 'AMD',
        'LIN', 'SHW', 'FCX', 'CTVA', 'ECL', 'APD', 'NEM', 'DOW'
    ],

    'TACTICAL_REGIME_25PCT': [
        'BRK-B', 'JPM', 'V', 'MA', 'BAC', 'WFC', 'MS', 'GS',
        'XOM', 'CVX', 'COP', 'SLB', 'EOG', 'MPC'
    ],

    'OPTIMIZED_PORTFOLIO_100PCT': [
        'NEE', 'SO', 'DUK', 'CEG', 'AEP', 'SRE', 'D', 'EXC',
        'CAT', 'GE', 'UNP', 'HON', 'BA', 'UPS', 'RTX', 'DE', 'LMT', 'ETN',
        'MSFT', 'AAPL', 'NVDA', 'AVGO', 'ORCL', 'ADBE', 'CRM', 'AMD',
        'LIN', 'SHW', 'FCX', 'CTVA', 'ECL', 'APD', 'NEM', 'DOW',
        'BRK-B', 'JPM', 'V', 'MA', 'BAC', 'WFC', 'MS', 'GS',
        'XOM', 'CVX', 'COP', 'SLB', 'EOG', 'MPC'
    ],

    'SECTOR_UTILITIES': ['NEE', 'SO', 'DUK', 'CEG', 'AEP', 'SRE', 'D', 'EXC', 'XEL', 'PEG', 'ED', 'PCG', 'VST', 'FE', 'ETR'],
    'SECTOR_INDUSTRIALS': ['CAT', 'GE', 'UNP', 'HON', 'BA', 'UPS', 'RTX', 'DE', 'LMT', 'ETN', 'FDX', 'MMM', 'NSC', 'WM', 'EMR'],
    'SECTOR_TECHNOLOGY': ['MSFT', 'AAPL', 'NVDA', 'AVGO', 'ORCL', 'ADBE', 'CRM', 'AMD', 'QCOM', 'TXN', 'INTC', 'IBM', 'NOW', 'AMAT', 'LRCX'],
    'SECTOR_COMMUNICATION': ['GOOGL', 'META', 'NFLX', 'DIS', 'CMCSA', 'TMUS', 'VZ', 'T', 'CHTR', 'WBD', 'PARA', 'LYV', 'FOXA'],
    'SECTOR_MATERIALS': ['LIN', 'SHW', 'FCX', 'CTVA', 'ECL', 'APD', 'NEM', 'DOW', 'PPG', 'NUE', 'ALB', 'MLM', 'VMC', 'NEM'],
    'SECTOR_ENERGY': ['XOM', 'CVX', 'COP', 'SLB', 'EOG', 'MPC', 'PSX', 'VLO', 'OXY', 'HES', 'HAL', 'DVN', 'KMI', 'WMB'],
    'SECTOR_FINANCIALS': ['BRK-B', 'JPM', 'V', 'MA', 'BAC', 'WFC', 'MS', 'GS', 'BLK', 'C', 'AXP', 'PYPL', 'SCHW', 'PGR', 'CB'],
    'SECTOR_HEALTHCARE': ['LLY', 'UNH', 'JNJ', 'MRK', 'ABBV', 'TMO', 'AMGN', 'PFE', 'ISRG', 'DHR', 'BMY', 'GILD', 'VRTX', 'SYK', 'ELV'],
    'SECTOR_CONSUMER_STAPLES': ['PG', 'COST', 'PEP', 'KO', 'WMT', 'PM', 'MO', 'CL', 'KDP', 'GIS', 'SYY', 'STZ', 'EL', 'ADM'],
    'SECTOR_REAL_ESTATE': ['PLD', 'AMT', 'EQIX', 'WELL', 'PSA', 'CCI', 'DLR', 'SPG', 'O', 'VICI', 'SBAC', 'CBRE', 'WY', 'AVB', 'ARE'],
    'SECTOR_CONSUMER_DISCRETIONARY': ['AMZN', 'TSLA', 'HD', 'MCD', 'NKE', 'LOW', 'BKNG', 'SBUX', 'TJX', 'TGT', 'ORLY', 'MAR', 'F', 'GM'],

    'SP500_FULL_UNIVERSE': [],
}

ACTIVE_TICKER_SET = 'OPTIMIZED_PORTFOLIO_100PCT'
TICKERS = TICKER_SETS[ACTIVE_TICKER_SET]

BACKTEST_PERIOD = '10y'
TIMEFRAME = '1d'
LOOKBACK_WINDOW = 80
ALPHA = 0.3
CORRELATION_THRESHOLD = 0.7
MAX_DIMENSION = 3
REGIME_WINDOW = 10
NET_EXPOSURE = 0.7
TRANSACTION_COST_BPS = 0.0010
REBALANCE_FREQUENCY = 10
RISK_MODE = 'STANDARD'

RISK_PROFILES = {
    'HYPER_AGGRESSIVE': {
        'STOP_LOSS_PCT': 0.15,
        'MAX_DRAWDOWN_LIMIT': 0.50,
        'LEVERAGE_MULTIPLIER': 3.0,
    },
    'AGGRESSIVE': {
        'STOP_LOSS_PCT': 0.05,
        'MAX_DRAWDOWN_LIMIT': 0.25,
        'LEVERAGE_MULTIPLIER': 1.5,
    },
    'GROWTH': {
        'STOP_LOSS_PCT': 0.07,
        'MAX_DRAWDOWN_LIMIT': 0.30,
        'LEVERAGE_MULTIPLIER': 2.0,
    },
    'STANDARD': {
        'STOP_LOSS_PCT': 0.02,
        'MAX_DRAWDOWN_LIMIT': 0.05,
        'LEVERAGE_MULTIPLIER': 1.0,
    },
    'BALANCED': {
        'STOP_LOSS_PCT': 0.03,
        'MAX_DRAWDOWN_LIMIT': 0.08,
        'LEVERAGE_MULTIPLIER': 1.0,
    },
    'INSTITUTIONAL': {
        'STOP_LOSS_PCT': 0.03,
        'MAX_DRAWDOWN_LIMIT': 0.15,
        'LEVERAGE_MULTIPLIER': 1.2,
    },
    'PENSION_FUND': {
        'STOP_LOSS_PCT': 0.01,
        'MAX_DRAWDOWN_LIMIT': 0.10,
        'LEVERAGE_MULTIPLIER': 0.25,
    },
    'CONSERVATIVE': {
        'STOP_LOSS_PCT': 0.01,
        'MAX_DRAWDOWN_LIMIT': 0.03,
        'LEVERAGE_MULTIPLIER': 0.25,
    },
    'ULTRA_CONSERVATIVE': {
        'STOP_LOSS_PCT': 0.005,
        'MAX_DRAWDOWN_LIMIT': 0.01,
        'LEVERAGE_MULTIPLIER': 0.0,
    },
    'CAUTIOUS': {
        'STOP_LOSS_PCT': 0.01,
        'MAX_DRAWDOWN_LIMIT': 0.02,
        'LEVERAGE_MULTIPLIER': 0.5,
    }
}

STOP_LOSS_PCT = RISK_PROFILES[RISK_MODE]['STOP_LOSS_PCT']
MAX_DRAWDOWN_LIMIT = RISK_PROFILES[RISK_MODE]['MAX_DRAWDOWN_LIMIT']

MC_SIMULATIONS = 1000
MC_HORIZON_DAYS = 252 * int(BACKTEST_PERIOD[:-1])
MC_CONFIDENCE_LEVEL = 0.95
