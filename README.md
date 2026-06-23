# Laplacian Trade

A Python backtesting engine that builds trading signals using graph theory and topological data analysis across 17 assets.

---

## What it does

Most trading strategies look at assets in isolation. This project models the *relationships* between assets as a graph and trades the gaps — if an asset drifts away from where the graph says it should be, bet on it reverting.

There's also a regime filter using persistent homology that detects when the correlation structure between assets is breaking down. When it does, the engine steps back to neutral rather than trading into noise.

---

## Architecture

**Graph Laplacian signal** — builds a correlation graph across all assets, computes each asset's "implied" return from its neighbours, and generates a signal from the residual.

**Topological regime filter** — runs a Vietoris-Rips filtration on the same correlation data to measure how structurally stable the market is. Unstable → flat exposure.

**Decision engine** — combines both signals, sizes positions accordingly, and hard-stops at a -12% drawdown.

---

## Backtest results (2016–2026)

> Simulation only — not tested live.

| Metric | Value |
| :--- | :--- |
| Cumulative return | +63.9% |
| Sharpe (2022–2026) | 2.52 |
| Sortino | 0.61 |
| 2022 return | +11.89% |

The Sortino being low relative to the Sharpe is a known weakness — the upside volatility is flattering the Sharpe more than the downside protection justifies.

Monte Carlo across 10,000 paths gives a median final value of ~$44k vs a mean of ~$52k, so the return distribution is right-skewed.

---

## Limitations

- Thresholds were tuned on the same data used for evaluation — overfitting risk is real
- 3bps transaction cost assumption is optimistic for some of the commodity tickers
- No live testing, no order book impact modelling

---

## Stack

Python · NumPy · pandas · yfinance · gudhi · scipy · matplotlib

---

## Run it

```bash
pip install -r requirements.txt
python simulation/backtest.py
python simulation/monte_carlo.py
```

---

## License

MIT
