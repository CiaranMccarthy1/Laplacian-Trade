import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from datetime import datetime

from core import config
from data.fetcher import DataFetcher
from spatial.laplacian import SpatialGraph
from topological.homology import TopologicalFeatureExtractor
from integration.decision_engine import IntegrationEngine


def run_backtest():
    """
    Run a historical backtest of the strategy.

    Steps:
      1. Fetch daily close prices.
      2. Roll a window through the data, rebuilding the graph / TDA
         every REBALANCE_FREQUENCY bars.
      3. Generate signals and track portfolio PnL (including transaction costs).
      4. Print performance metrics and save an equity-curve chart.
    """
    fetcher = DataFetcher()
    prices = fetcher.fetch_historical_data(period=config.BACKTEST_PERIOD)
    if prices.empty:
        print("No data for backtest.")
        return

    all_returns = np.log(prices / prices.shift(1)).fillna(0.0)

    spatial = SpatialGraph()
    topo = TopologicalFeatureExtractor()
    engine = IntegrationEngine()

    window = config.LOOKBACK_WINDOW
    rebal = config.REBALANCE_FREQUENCY
    cost_bps = config.TRANSACTION_COST_BPS

    portfolio_values = [1.0]
    daily_returns = []
    prev_weights = pd.Series(0.0, index=all_returns.columns)

    indices = all_returns.index
    print(f"Running backtest on {len(indices)} bars (window={window})...")

    for i in range(window - 1, len(indices) - 1):
        window_returns = all_returns.iloc[i - window + 1: i + 1]
        current_vec = window_returns.iloc[-1]

        if i % rebal == 0:
            try:
                G = spatial.build_graph(window_returns)
                spatial.compute_laplacian(G)

                dist = topo.create_point_cloud(spatial.adjacency_matrix)
                diagrams = topo.compute_persistence_diagrams(dist)
                regime_metrics = topo.get_regime_metrics(diagrams)

                diffusion = spatial.compute_diffusion_signal(current_vec)
                residuals = spatial.get_residuals(current_vec, diffusion)
            except Exception:
                residuals = pd.Series(0, index=current_vec.index)
                regime_metrics = {'max_persistence_h1': 0.0}

            signals = engine.generate_signals(residuals, regime_metrics)
            current_weights = pd.Series(0.0, index=all_returns.columns)
            active = signals[signals['Signal'] != 0]['Signal']
            current_weights.loc[active.index] = active
        else:
            current_weights = prev_weights

        turnover = np.sum(np.abs(current_weights - prev_weights))
        step_cost = turnover * cost_bps
        prev_weights = current_weights

        step_pnl = np.sum(current_weights * all_returns.iloc[i + 1]) - step_cost
        daily_returns.append(step_pnl)
        portfolio_values.append(portfolio_values[-1] * (1 + step_pnl))

        if i % 50 == 0:
            print(f"  Step {i}/{len(indices)} | Equity: {portfolio_values[-1]:.4f}")

    # --- Metrics ---
    port = pd.Series(portfolio_values, index=indices[window - 1:])
    rets = pd.Series(daily_returns, index=indices[window: window + len(daily_returns)])
    sharpe = np.sqrt(252) * (rets.mean() / rets.std()) if rets.std() > 0 else 0.0

    print(f"\nBacktest complete.  Final equity: {port.iloc[-1]:.4f}")
    print(f"Sharpe ratio: {sharpe:.2f}")

    # --- Annual breakdown ---
    for year, yr in rets.groupby(rets.index.year):
        yr_sharpe = np.sqrt(252) * yr.mean() / yr.std() if yr.std() > 0 else 0.0
        print(f"  {year}  Return: {yr.sum():.2%}  Sharpe: {yr_sharpe:.2f}")

    # --- Plot ---
    try:
        os.makedirs("results", exist_ok=True)
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 6))
        port.plot(ax=ax1, label='Equity Curve')
        ax1.set_title(f'Backtest (Sharpe: {sharpe:.2f})')
        ax1.set_ylabel('Portfolio Value')
        ax1.legend()
        ax1.grid(True, alpha=0.3)

        rets.plot(ax=ax2, alpha=0.6, label='Daily Returns')
        ax2.set_ylabel('Returns')
        ax2.legend()
        ax2.grid(True, alpha=0.3)

        plt.tight_layout()
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        fname = f"results/backtest_{ts}.png"
        plt.savefig(fname)
        plt.close()
        print(f"Chart saved to {fname}")
    except Exception as e:
        print(f"Could not generate plot: {e}")


if __name__ == "__main__":
    run_backtest()
