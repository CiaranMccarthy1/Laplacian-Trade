# Topological Arbitrage Trading System

An advanced quantitative trading system leveraging **Spatial Graph Theory** and **Topological Data Analysis (TDA)** to detect market regimes and generate arbitrage signals.

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
    *   Calculates **Persistence Entropy** to quantity market noise vs. signal (Stability Regime).

3.  **Integration Engine (`integration/`)**:
    *   Combines spatial residuals with topological regime stability.
    *   Dynamic sizing: Reduces exposure during high-entropy (chaotic) regimes.
    *   Generates Long/Short signals with configurable risk management (Stop Loss, Max Drawdown).

## Project Structure

```
├── backtest.py           # Historical backtesting engine
├── config.py             # Global configuration (Tickers, Risk, Params)
├── main.py               # Live/Single-step execution entry point
├── optimize.py           # Grid search parameter optimization
├── check_delisted.py     # Utility to check for delisted/survivor-bias tickers
├── data/
│   └── fetcher.py        # Data ingestion (YFinance)
├── spatial/
│   └── laplacian.py      # Graph theory & diffusion logic
├── topological/
│   └── homology.py       # TDA & Persistence Entropy logic
├── integration/
│   └── decision_engine.py # Signal generation & Risk rules
└── tests/                # Unit tests
```

## Installation

1.  **Clone the repository**:
    ```bash
    git clone <https://github.com/CiaranMccarthy1/Laplacian-Trade>
    cd trading-algo
    ```

2.  **Create a virtual environment** (recommended):
    ```bash
    python -m venv venv
    .\venv\Scripts\activate  # Windows
    # source venv/bin/activate # Linux/Mac
    ```

3.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

### Running a Backtest

To test the strategy over historical data (configured in `config.py`):

```bash
python backtest.py
```

Results (performance metrics and charts) will be saved to the `results/` directory.

### Current Performance (10-Year Backtest)

*Configuration: Aggressive Mode, 1.5x Leverage, Daily Interval*

```text
Final Portfolio Value: 2.3808
Sharpe Ratio (Approx): 0.73
Average Annual Return: 8.71% 
```

**Annual Breakdown:**
| Year | Return | Sharpe |
|------|--------|--------|
| 2016 | -1.56% | -0.55  |
| 2017 | 6.83%  | 1.12   |
| 2018 | 8.88%  | 0.71   |
| 2019 | 11.16% | 0.83   |
| 2020 | 38.99% | 1.58   |
| 2021 | 3.45%  | 0.42   |
| 2022 | -3.68% | -0.36  |
| 2023 | 8.59%  | 1.06   |
| 2024 | 20.07% | 1.15   |
| 2025 | 0.37%  | 0.02   |
| 2026 | 2.71%  | 2.31   |

### Parameter Optimization

To find optimal parameters (Alpha, Lookback, Exposure) via grid search:

```bash
python optimize.py
```

### Live/Single Step

To run a single iteration (e.g., for Cron jobs or live trading loops):

```bash
python main.py
```

## Configuration

Edit `config.py` to adjust:
*   **TICKERS**: List of assets to trade (default: S&P 500 subset).
*   **RISK_MODE**: 'AGGRESSIVE', 'STANDARD', or 'CAUTIOUS'.
*   **NET_EXPOSURE**: Strategy bias (0.0 = Market Neutral, 1.0 = Long Only).
*   **ALPHA**: Diffusion coefficient for the spatial graph.

## Testing

Run unit tests to ensure all components are functioning correctly:

```bash
pytest tests
```

## License

[MIT](LICENSE)
