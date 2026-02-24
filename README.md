# Laplacian Trade

A quantitative trading system that uses **Graph Laplacian diffusion** and **Topological Data Analysis (TDA)** to detect market regimes and generate arbitrage signals.

## How It Works

1. **Spatial Graph** (`spatial/laplacian.py`) — Builds a correlation graph of assets, computes the normalised Graph Laplacian, and solves for an equilibrium "diffusion" state. Residuals from this equilibrium highlight mean-reversion candidates.

2. **Persistent Homology** (`topological/homology.py`) — Converts the correlation matrix into a distance matrix and runs Vietoris-Rips filtration. Persistence entropy of H1 features gauges whether the market is in a stable or chaotic regime.

3. **Decision Engine** (`integration/decision_engine.py`) — Merges spatial residuals with topological regime stability to produce sized long/short signals with configurable risk parameters.

## Project Structure

```
main.py                        # Single-pass entry point
core/config.py                 # All tuneable parameters
data/fetcher.py                # Market data via yfinance
spatial/laplacian.py           # Graph Laplacian & diffusion
topological/homology.py        # TDA / persistent homology
integration/decision_engine.py # Signal generation
simulation/backtest.py         # Historical backtesting
simulation/monte_carlo.py      # Monte Carlo risk analysis
tests/test_components.py       # Unit tests
```

## Quick Start

```bash
# Clone & install
git clone https://github.com/CiaranMccarthy1/trading-algo
cd trading-algo
python -m venv venv
.\venv\Scripts\activate   # Windows
pip install -r requirements.txt

# Run a single pass
python main.py

# Backtest
python -m simulation.backtest

# Monte Carlo simulation
python -m simulation.monte_carlo

# Tests
pytest tests
```

## Configuration

Edit `core/config.py` to change tickers, lookback window, alpha, risk limits, etc.

| Parameter | Default | Description |
|-----------|---------|-------------|
| `TICKERS` | 15 large-caps | Assets to trade |
| `ALPHA` | 0.3 | Diffusion strength |
| `CORRELATION_THRESHOLD` | 0.7 | Min edge weight for graph |
| `LOOKBACK_WINDOW` | 80 | Rolling window size (bars) |
| `NET_EXPOSURE` | 0.7 | Long bias (0 = neutral, 1 = long-only) |
| `STOP_LOSS_PCT` | 0.02 | Per-position stop loss |
| `MAX_DRAWDOWN_LIMIT` | 0.05 | Portfolio drawdown cap |

## License

[MIT](LICENSE)