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
| Cumulative return | +151.5% |
| Sharpe ratio | 0.42 |
| Sortino ratio | 0.48 |
| Best year | 2017 (+48.49%) |
| Worst year | 2022 (−13.08%) |
| Strategy vs SPY | 0.30x (30% of SPY's raw return) |

The strategy delivered positive risk-adjusted returns over 20 years, with strong performance in trending years (2013, 2017, 2021, 2024) and controlled drawdowns in crisis years.

## Monte Carlo Validation

| Metric | Value |
|--------|-------|
| Mean final equity | 2.49 |
| Median final equity | 2.17 |
| VaR (95%) | 0.83 |
| CVaR (95%) | 0.71 |
| Probability of loss | 10.0% |
| Upside potential (95%) | 398.19% |

The distribution is right-skewed — most outcomes cluster around the median (2.17x), with a small number of high-return paths pulling the mean higher (2.49x). The 10% probability of loss and 95% VaR of 0.83 demonstrate robust risk management.


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
