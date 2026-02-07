# Topological Arbitrage Trading System

An advanced quantitative trading system leveraging **Spatial Graph Theory** and **Topological Data Analysis (TDA)** to detect market regimes and generate arbitrage signals.

## Optimized Portfolio Allocation Strategy

Based on comprehensive Monte Carlo analysis and sector optimization, the system employs a **Three-Tier Capital Allocation** approach:

### Portfolio Architecture

| Tier | Ticker Set | Allocation | Sectors |
|------|-----------|------------|---------|
| Defensive Core | `DEFENSIVE_CORE_45PCT` | 45% | Utilities (35.6), Industrials (30.8) |
| Growth Engine | `GROWTH_ENGINE_30PCT` | 30% | Technology (19.6), Materials (21.8) |
| Tactical Regime | `TACTICAL_REGIME_25PCT` | 25% | Financials (12.4), Energy (4.1) |

### Monte Carlo Risk Analysis (10-Year, $10k initial)

| Sector | VaR (95%) | CVaR (95%) | Expected Return | Risk-Adj Score |
|--------|-----------|------------|-----------------|----------------|
| Utilities | $1,191 | $1,949 | 424.1% | **35.6** |
| Materials | $2,428 | $4,696 | 529.0% | **21.8** |
| Industrials | $2,605 | $1,315 | 801.9% | **30.8** |
| Technology | $10,559 | $3,418 | **2072.5%** | 19.6 |
| Communication | $5,423 | $1,808 | 834.0% | 15.4 |

### Current Parameters

| Parameter | Value | Notes |
|-----------|-------|-------|
| Alpha | 0.3 | Dominated 7 of 8 top configurations |
| Net Exposure | 0.7 | Long-biased |
| Lookback Window | 80 | Fast response for stable manifolds |
| Risk Profile | STANDARD | 2% stop-loss, 5% max drawdown, 1.0x leverage |
| Backtest Period | 10y | |

---

## Overview

This project implements a novel trading strategy that models the market as a dynamic spatial graph. It uses the Graph Laplacian to measure diffusion and structural discrepancies between assets, while simultaneously applying Persistent Homology (TDA) to gauge market stability (regime detection).

### Key Concepts

1.  **Spatial Layer (`spatial/`)**:
    *   Constructs a correlation-based graph of assets.
    *   Computes the **Graph Laplacian** and solves for the equilibrium "diffusion" state.
    *   Identifies residuals (price deviations) from this theoretical equilibrium to find mean-reversion candidates.

2.  **Topological Layer (`topological/`)**:
    *   Converts correlation matrices into point clouds.
    *   Uses **Persistent Homology** (Vietoris-Rips filtration) to extract topological features (H0, H1).
    *   Calculates **Persistence Entropy** to quantify market noise vs. signal (Stability Regime).

3.  **Integration Engine (`integration/`)**:
    *   Combines spatial residuals with topological regime stability.
    *   Dynamic alpha and leverage: Reduces both during high-entropy (chaotic) regimes.
    *   Generates Long/Short signals with configurable risk management (Stop Loss, Max Drawdown).

## Project Structure

```
├── main.py               # Live/single-step execution entry point
├── core/
│   └── config.py         # Global configuration (tickers, risk, params)
├── simulation/
│   ├── backtest.py       # Historical backtesting engine
│   ├── monte_carlo.py    # Monte Carlo simulation engine
│   └── run_sectors.py    # Cross-sector comparative analysis
├── optimization/
│   └── optimize.py       # Grid search parameter optimization
├── data/
│   └── fetcher.py        # Data ingestion (YFinance)
├── spatial/
│   └── laplacian.py      # Graph theory & diffusion logic
├── topological/
│   └── homology.py       # TDA & Persistence Entropy logic
├── integration/
│   └── decision_engine.py # Signal generation & risk rules
├── utils/
│   └── check_delisted.py # Utility to check for delisted/survivor-bias tickers
└── tests/                # Unit tests
```

## Installation

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/CiaranMccarthy1/trading-algo
    cd trading-algo
    ```

2.  **Create a virtual environment** (recommended):
    ```bash
    python -m venv venv
    .\venv\Scripts\activate  # Windows
    ```

3.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

All scripts other than `main.py` should be run as modules from the project root.

### Backtest

```bash
python -m simulation.backtest
```

### Monte Carlo Simulation

```bash
python -m simulation.monte_carlo
```

### Sector Analysis

```bash
python -m simulation.run_sectors
```

### Parameter Optimization

```bash
python -m optimization.optimize
```

### Live / Single Step

```bash
python main.py
```

## Configuration

Edit `core/config.py` to switch ticker sets or adjust parameters:

```python
ACTIVE_TICKER_SET = 'OPTIMIZED_PORTFOLIO_100PCT'  # Full strategy (default)
ACTIVE_TICKER_SET = 'DEFENSIVE_CORE_45PCT'         # 45% defensive core
ACTIVE_TICKER_SET = 'GROWTH_ENGINE_30PCT'          # 30% growth engine
ACTIVE_TICKER_SET = 'TACTICAL_REGIME_25PCT'        # 25% tactical regime

ACTIVE_TICKER_SET = 'SECTOR_UTILITIES'             # Individual sector
ACTIVE_TICKER_SET = 'SECTOR_TECHNOLOGY'            # Individual sector
```

Available risk modes: `HYPER_AGGRESSIVE`, `AGGRESSIVE`, `GROWTH`, `STANDARD`, `BALANCED`, `INSTITUTIONAL`, `PENSION_FUND`, `CONSERVATIVE`, `ULTRA_CONSERVATIVE`, `CAUTIOUS`.

## Testing

```bash
pytest tests
```

## License

[MIT](LICENSE)