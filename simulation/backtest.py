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
    Topological Backtest 
    --------------------
    Orchestrates the walk-forward simulation of the Graph-based Alpha Engine.
    Handles data ingestion, topological feature extraction, signal integration,
    and rigorous transaction cost accounting.
    """
    fetcher = DataFetcher()
    prices = fetcher.fetch_historical_data(period=config.BACKTEST_PERIOD)
    if prices.empty:
        print("No data for backtest.")
        return

    # Utilize Log-Returns for time-series additivity and statistical stability.
    all_returns = np.log(prices / prices.shift(1)).fillna(0.0)

    # Initialize Core Quantitative Modules.
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

    # Main Simulation Loop (Walk-Forward Causality).
    for i in range(window - 1, len(indices) - 1):
        window_returns = all_returns.iloc[i - window + 1: i + 1]
        current_vec = window_returns.iloc[-1]

        # Conditional Rebalancing Logic to minimize Turnover/Slippage.
        if i % rebal == 0:
            try:
                # 1. Spatial Domain: Construct Graph and Compute Laplacian Residuals.
                G = spatial.build_graph(window_returns)
                spatial.compute_laplacian(G)

                # 2. Topological Domain: Extract H1 Persistence (Structural Stability).
                dist = topo.create_point_cloud(spatial.adjacency_matrix)
                diagrams = topo.compute_persistence_diagrams(dist)
                regime_metrics = topo.get_regime_metrics(diagrams)

                # 3. Signal Generation: Compute outliers relative to the diffusion signal.
                diffusion = spatial.compute_diffusion_signal(current_vec)
                residuals = spatial.get_residuals(current_vec, diffusion)
            except Exception:
                # Fault tolerance for singular matrices or topological noise.
                residuals = pd.Series(0, index=current_vec.index)
                regime_metrics = {'max_persistence_h1': 0.0}

            # Calculate state variables for the Integration Engine's Risk Management.
            lookback_slice = portfolio_values[-252:] if len(portfolio_values) > 252 else portfolio_values
            rolling_peak = max(lookback_slice)
            current_dd = (portfolio_values[-1] / rolling_peak) - 1
            history_series = pd.Series(daily_returns)

            # 4. Integration: Decision Engine synthesizes signals and applies Risk Shields.
            signals = engine.generate_signals(
                residuals, 
                regime_metrics, 
                current_drawdown=current_dd,
                returns_history=history_series
            )
            
            current_weights = pd.Series(0.0, index=all_returns.columns)
            active = signals[signals['Signal'] != 0]['Signal']
            current_weights.loc[active.index] = active
        else:
            # Maintain stationary weights between rebalance periods.
            current_weights = prev_weights

        # Transaction Cost Impact: Turnover-based slippage calculation.
        turnover = np.sum(np.abs(current_weights - prev_weights))
        step_cost = turnover * cost_bps
        prev_weights = current_weights

        # Execute PnL step (Exposure * Next Day Return - Costs).
        step_pnl = np.sum(current_weights * all_returns.iloc[i + 1]) - step_cost
        daily_returns.append(step_pnl)
        portfolio_values.append(portfolio_values[-1] * (1 + step_pnl))

        if i % 100 == 0:
            print(f"  Step {i}/{len(indices)} | Equity: {portfolio_values[-1]:.4f}")

    # Compute Standard Performance Metrics.
    port = pd.Series(portfolio_values, index=indices[window - 1:])
    rets = pd.Series(daily_returns, index=indices[window: window + len(daily_returns)])
    
    # Sharpe Ratio: Risk-adjusted return relative to portfolio volatility.
    sharpe = np.sqrt(252) * (rets.mean() / rets.std()) if rets.std() > 0 else 0.0

    # Sortino Ratio: Risk-adjusted return focusing on downside deviation (Left-tail risk).
    downside_rets = rets[rets < 0]
    downside_std = downside_rets.std() if not downside_rets.empty else 0.0
    sortino = np.sqrt(252) * (rets.mean() / downside_std) if downside_std > 0 else 0.0

    print("\nBacktest complete")  
    print(f"Final equity: {port.iloc[-1]:.4f}")
    print(f"Sharpe ratio: {sharpe:.2f}")
    print(f"Sortino ratio: {sortino:.2f}")

    # Yearly Performance Attribution (Regime Analysis).
    for year, yr in rets.groupby(rets.index.year):
        yr_sharpe = np.sqrt(252) * yr.mean() / yr.std() if yr.std() > 0 else 0.0
        print(f"  {year}  Return: {yr.sum():.2%}  Sharpe: {yr_sharpe:.2f}")

    # Visual Reporting: Export equity curve to the /results directory.
    try:
        os.makedirs("results", exist_ok=True)
        fig, ax1 = plt.subplots(figsize=(12, 6))
        port.plot(ax=ax1, label='Equity Curve', color='#1f77b4', lw=2)
        ax1.set_title(f'Topological Strategy Performance (Sharpe: {sharpe:.2f})', fontsize=14)
        ax1.set_ylabel('Portfolio Value (Normalized)', fontsize=12)
        ax1.grid(True, linestyle='--', alpha=0.5)
        plt.savefig(f"results/backtest_{datetime.now().strftime('%H%M%S')}.png")
        plt.close()
    except Exception:
        pass

if __name__ == "__main__":
    run_backtest()