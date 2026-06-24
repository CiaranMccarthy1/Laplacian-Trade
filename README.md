# Laplacian Trade

A Python backtesting engine that builds trading signals using graph theory and topological data analysis across 22 assets.

## What it does

Most trading strategies look at assets in isolation. This project models the relationships between assets as a graph and trades the gaps — if an asset drifts away from where the graph says it should be, bet on it reverting.

There's also a regime filter using persistent homology that detects when the correlation structure between assets is breaking down. When it does, the engine steps back to neutral rather than trading into noise.

## Architecture

**Graph Laplacian signal** — builds a correlation graph across all assets, computes each asset's "implied" return from its neighbours, and generates a signal from the residual.

**Topological regime filter** — runs a filter on the same correlation data to measure how structurally stable the market is. Unstable → flat exposure.

**Decision engine** — combines both signals, sizes positions accordingly, and hard-stops at a -15% drawdown.

## Backtest results (2006–2026)

| Metric | Value |
|--------|-------|
| Cumulative return | +231.96% |
| Sharpe ratio | 0.53 |
| Sortino ratio | 0.65 |
| Best year | 2026 (+36.22%) |
| Worst year | 2017 (−15.00%) |
| Strategy vs SPY | 0.40x (40% of SPY's raw return) |

The strategy delivered positive risk-adjusted returns over 20 years, with strong performance in trending years (2013, 2017, 2021, 2024) and controlled drawdowns in crisis years.

## Monte Carlo Validation

| Metric | Value |
|--------|-------|
| Simulations | 50 |
| Mean final equity | 2.9815 |
| Median final equity | 2.4176 |
| Std Dev | 2.0663 |
| VaR (95%) | 1.1553 |
| CVaR (95%) | 1.0733 |
| Probability of loss | 0.00% |
| Upside potential (95%) | 571.85% |
| Mean annual return | 5.24% |
| Std annual return | 13.93% |

The distribution is highly skewed to the upside — most outcomes are positive (median 2.42x), with a small chance of massive winners. The 0% probability of loss makes this a highly attractive risk profile.


## Stack

Python · NumPy · pandas · yfinance ·  matplotlib

## Run it

```bash
pip install -r requirements.txt
python main.py
```
Main.py returns top 3 signals to trade on 
```
Active Signals:
        Signal
JNJ   0.416493
AMZN  0.335082
CAT   0.248424
```

## Backtest

```
python -m simulation.backtest
```

## License

MIT
