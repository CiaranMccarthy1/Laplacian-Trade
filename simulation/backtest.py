import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from datetime import datetime
from typing import Tuple, Dict, List, Optional
import yfinance as yf

from core import config
from data.fetcher import DataFetcher
from spatial.laplacian import SpatialGraph
from topological.homology import TopologicalFeatureExtractor
from integration.decision_engine import IntegrationEngine


def run_single_simulation(
    returns: pd.DataFrame,
    window: int,
    rebal: int,
    cost_bps: float,
    stop_loss_pct: float,
    verbose: bool = False
) -> Tuple[np.ndarray, np.ndarray]:
    """Core simulation: returns equity curve and daily PnL as arrays."""
    spatial = SpatialGraph()
    topo = TopologicalFeatureExtractor()
    engine = IntegrationEngine()

    n_bars = len(returns)
    portfolio_values = [1.0]
    daily_pnl = []
    prev_weights = pd.Series(0.0, index=returns.columns)

    for i in range(window - 1, n_bars - 1):
        window_returns = returns.iloc[i - window + 1: i + 1]
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

            lookback_slice = portfolio_values[-252:] if len(portfolio_values) > 252 else portfolio_values
            rolling_peak = max(lookback_slice)
            current_dd = (portfolio_values[-1] / rolling_peak) - 1
            history_series = pd.Series(daily_pnl)

            signals = engine.generate_signals(
                residuals,
                regime_metrics,
                current_drawdown=current_dd,
                returns_history=history_series
            )

            current_weights = pd.Series(0.0, index=returns.columns)
            active = signals[signals['Signal'] != 0]['Signal']
            current_weights.loc[active.index] = active
        else:
            current_weights = prev_weights.copy()

        current_weights[(current_weights * returns.iloc[i]) < -stop_loss_pct] = 0.0
        turnover = np.sum(np.abs(current_weights - prev_weights))
        step_cost = turnover * cost_bps
        prev_weights = current_weights

        step_pnl = np.sum(current_weights * returns.iloc[i + 1]) - step_cost
        daily_pnl.append(step_pnl)
        portfolio_values.append(portfolio_values[-1] * (1 + step_pnl))

        if verbose and i % 100 == 0:
            print(f"  Step {i}/{n_bars} | Equity: {portfolio_values[-1]:.4f}")

    return np.array(portfolio_values), np.array(daily_pnl)


def compute_metrics(equity: np.ndarray, daily_ret: np.ndarray, returns_index: pd.DatetimeIndex, window: int) -> Dict:
    """Compute Sharpe, Sortino, and annual returns from a single run."""
    equity_series = pd.Series(equity, index=returns_index[window - 1:])
    daily_series = pd.Series(daily_ret, index=returns_index[window: window + len(daily_ret)])

    sharpe = np.sqrt(252) * (daily_ret.mean() / daily_ret.std()) if daily_ret.std() > 0 else 0.0
    downside = daily_ret[daily_ret < 0]
    downside_std = downside.std() if len(downside) > 0 else 0.0
    sortino = np.sqrt(252) * (daily_ret.mean() / downside_std) if downside_std > 0 else 0.0

    annual_returns = {}
    for year, yr in daily_series.groupby(daily_series.index.year):
        yr_ret = yr.values
        yr_sharpe = np.sqrt(252) * yr_ret.mean() / yr_ret.std() if yr_ret.std() > 0 else 0.0
        annual_returns[year] = {'return': yr_ret.sum(), 'sharpe': yr_sharpe}

    return {
        'equity_series': equity_series,
        'daily_series': daily_series,
        'final_equity': equity[-1],
        'sharpe': sharpe,
        'sortino': sortino,
        'annual_returns': annual_returns
    }


def plot_deterministic(metrics: Dict, save_path: str):
    """Plot equity curve for deterministic run."""
    fig, ax = plt.subplots(figsize=(12, 6))
    metrics['equity_series'].plot(ax=ax, label='Equity Curve', color='#1f77b4', lw=2)
    ax.set_title(f"Topological Strategy Performance (Sharpe: {metrics['sharpe']:.2f})", fontsize=14)
    ax.set_ylabel('Portfolio Value (Normalized)', fontsize=12)
    ax.grid(True, linestyle='--', alpha=0.5)
    plt.savefig(save_path)
    plt.close()


def plot_monte_carlo(equities: List[np.ndarray], final_equities: np.ndarray, annual_returns: np.ndarray, save_path: str):
    """Plot distribution, QQ, and sample paths for Monte Carlo."""
    from scipy import stats
    var_95 = np.percentile(final_equities, 5)
    median_eq = np.median(final_equities)

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    axes[0, 0].hist(final_equities, bins=50, color='#1f77b4', alpha=0.7, edgecolor='black', linewidth=0.5)
    axes[0, 0].axvline(var_95, color='red', linestyle='--', linewidth=2, label=f'VaR (95%): {var_95:.2f}')
    axes[0, 0].axvline(1.0, color='black', linestyle='-', linewidth=1, label='Breakeven')
    axes[0, 0].axvline(median_eq, color='green', linestyle='--', linewidth=2, label=f'Median: {median_eq:.2f}')
    axes[0, 0].set_title('Distribution of Final Equity')
    axes[0, 0].set_xlabel('Final Equity')
    axes[0, 0].set_ylabel('Frequency')
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3)

    axes[0, 1].hist(annual_returns, bins=50, color='#2ca02c', alpha=0.7, edgecolor='black', linewidth=0.5)
    axes[0, 1].axvline(0, color='black', linestyle='-', linewidth=1, label='Breakeven')
    axes[0, 1].axvline(np.mean(annual_returns), color='red', linestyle='--', linewidth=2,
                       label=f"Mean: {np.mean(annual_returns):.2%}")
    axes[0, 1].set_title('Distribution of Annual Returns')
    axes[0, 1].set_xlabel('Annual Return')
    axes[0, 1].set_ylabel('Frequency')
    axes[0, 1].legend()
    axes[0, 1].grid(True, alpha=0.3)

    sample_idx = np.random.choice(len(equities), min(100, len(equities)), replace=False)
    for idx in sample_idx:
        axes[1, 0].plot(equities[idx], color='#1f77b4', alpha=0.1, linewidth=0.5)
    max_len = max(len(c) for c in equities)
    padded = np.array([np.pad(c, (0, max_len - len(c)), constant_values=c[-1]) for c in equities])
    median_path = np.median(padded, axis=0)
    axes[1, 0].plot(median_path, color='red', linewidth=2, label='Median Path')
    axes[1, 0].axhline(1.0, color='black', linestyle='--', linewidth=1, label='Breakeven')
    axes[1, 0].set_title('Sample Equity Curves (100 random paths)')
    axes[1, 0].set_xlabel('Time Steps')
    axes[1, 0].set_ylabel('Equity')
    axes[1, 0].legend()
    axes[1, 0].grid(True, alpha=0.3)

    stats.probplot(final_equities, dist="norm", plot=axes[1, 1])
    axes[1, 1].set_title('QQ Plot: Final Equity Distribution')
    axes[1, 1].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(save_path)
    plt.close()


def buy_and_hold_returns(tickers: List[str], period: str = config.BACKTEST_PERIOD) -> pd.DataFrame:
    """
    Returns the cumulative return for each ticker and the equal‑weight portfolio.
    """
    fetcher = DataFetcher()
    prices = fetcher.fetch_historical_data(period=period)
    if prices.empty:
        return pd.DataFrame()
    
    # Keep only tickers that exist in the data
    available = [t for t in tickers if t in prices.columns]
    if not available:
        return pd.DataFrame()
    
    prices = prices[available]
    
    # First and last prices
    start = prices.iloc[0]
    end = prices.iloc[-1]
    returns = (end / start) - 1
    
    # Equal‑weight portfolio return
    port_return = returns.mean()
    
    # Build result DataFrame
    df = pd.DataFrame({
        'Start Price': start,
        'End Price': end,
        'Return': returns
    })
    
    # Append portfolio row
    df.loc['Equal-Weight Portfolio'] = [1.0, 1.0 + port_return, port_return]
    
    return df

def snp500_returns(period: str = config.BACKTEST_PERIOD) -> pd.Series:
    """Fetch SPY cumulative return using yfinance directly."""
    try:
        data = yf.download('SPY', period=period, interval='1d', progress=False)
        if data.empty:
            return pd.Series(dtype=float)
        start = data['Close'].iloc[0]
        end = data['Close'].iloc[-1]
        return pd.Series({
            'Start Price': start,
            'End Price': end,
            'Return': (end / start) - 1
        })
    except Exception as e:
        print(f"SPY fetch error: {e}")
        return pd.Series(dtype=float)

def run_backtest(progress_interval: int = 100, save_plots: bool = True):
    """
    Run both deterministic and Monte Carlo backtests.
    This is the single entry point for the entire backtest suite.
    """
    # Fetch data once
    fetcher = DataFetcher() 
    prices = fetcher.fetch_historical_data(period=config.BACKTEST_PERIOD)
    if prices.empty:
        print("No data available.")
        return

    all_returns = np.log(prices / prices.shift(1)).fillna(0.0)
    n_bars = len(all_returns)
    print(f"Data: {n_bars} bars, {len(all_returns.columns)} assets")

    # ==============================
    # 1. DETERMINISTIC BACKTEST
    # ==============================
    print(f"\nRunning deterministic backtest (window={config.LOOKBACK_WINDOW})...")
    equity_det, daily_det = run_single_simulation(
        all_returns,
        window=config.LOOKBACK_WINDOW,
        rebal=config.REBALANCE_FREQUENCY,
        cost_bps=config.TRANSACTION_COST_BPS,
        stop_loss_pct=config.STOP_LOSS_PCT,
        verbose=True
    )
    det_metrics = compute_metrics(equity_det, daily_det, all_returns.index, config.LOOKBACK_WINDOW)
    bh_returns = buy_and_hold_returns(config.TICKERS)

    print("\nDeterministic Backtest complete")
    print(f"  Final equity: {det_metrics['final_equity']:.4f}")
    print(f"  Sharpe ratio: {det_metrics['sharpe']:.2f}")
    print(f"  Sortino ratio: {det_metrics['sortino']:.2f}")
    for year, data in det_metrics['annual_returns'].items():
        print(f"  {year}  Return: {data['return']:.2%}  Sharpe: {data['sharpe']:.2f}")
    print("\nBuy-and-Hold Returns:")
    print(bh_returns)
    snp = snp500_returns()
    if not snp.empty:
        spy_return = snp['Return'].iloc[0]  # Extract scalar
        print(f"\nS&P 500 (SPY) return: {spy_return:.2%}")
        print(f"Strategy vs SPY: {det_metrics['final_equity'] / (1 + spy_return):.2f}x")
    else:
        print("\nS&P 500 data not available – skipping benchmark.")

    if save_plots: 
        os.makedirs("results", exist_ok=True)
        plot_path = f"results/backtest_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        plot_deterministic(det_metrics, plot_path)
        print(f"  Deterministic plot saved to: {plot_path}")

    # ==============================
    # 2. MONTE CARLO
    # ==============================
    print("\n" + "="*60)
    print("MONTE CARLO SIMULATION")
    print(f"Simulations: {config.MONTE_CARLO_SAMPLES}")
    print(f"Lookback: {config.LOOKBACK_WINDOW}, Rebalance: {config.REBALANCE_FREQUENCY}")
    print(f"Transaction cost: {config.TRANSACTION_COST_BPS * 10000:.1f} bps")
    print("="*60)

    final_equities = []
    equity_curves = []
    all_annual_returns = []

    for sim in range(config.MONTE_CARLO_SAMPLES):
        if sim % progress_interval == 0:
            print(f"  Simulation {sim}/{config.MONTE_CARLO_SAMPLES}...")

        idx = np.random.choice(n_bars, size=n_bars, replace=True)
        boot_returns = all_returns.iloc[idx].reset_index(drop=True)
        boot_returns.index = all_returns.index

        equity, daily_ret = run_single_simulation(
            boot_returns,
            window=config.LOOKBACK_WINDOW,
            rebal=config.REBALANCE_FREQUENCY,
            cost_bps=config.TRANSACTION_COST_BPS,
            stop_loss_pct=config.STOP_LOSS_PCT,
            verbose=False
        )
        final_equities.append(equity[-1])
        equity_curves.append(equity)

        daily_series = pd.Series(daily_ret, index=boot_returns.index[config.LOOKBACK_WINDOW:
                                                                     config.LOOKBACK_WINDOW + len(daily_ret)])
        annual_ret = daily_series.groupby(daily_series.index.year).sum()
        all_annual_returns.extend(annual_ret.values)

    final_equities = np.array(final_equities)
    annual_returns = np.array(all_annual_returns)

    var_95 = np.percentile(final_equities, 5)
    cvar_95 = final_equities[final_equities <= var_95].mean()
    prob_loss = np.mean(final_equities < 1.0)

    print("\nMonte Carlo Results")
    print(f"  Mean final equity:   {np.mean(final_equities):.4f}")
    print(f"  Median final equity: {np.median(final_equities):.4f}")
    print(f"  Std Dev:             {np.std(final_equities):.4f}")
    print(f"  VaR (95%):           {var_95:.4f}  (5% chance below this)")
    print(f"  CVaR (95%):          {cvar_95:.4f}  (avg loss in worst 5%)")
    print(f"  Probability of loss: {prob_loss:.2%}")
    print(f"  Expected loss (VaR): {(1 - var_95) * 100:.2f}%")
    print(f"  Upside potential (95%): {(np.percentile(final_equities, 95) - 1) * 100:.2f}%")
    print(f"  Mean annual return:  {np.mean(annual_returns):.2%}")
    print(f"  Std annual return:   {np.std(annual_returns):.2%}")

    if save_plots:
        plot_path_mc = f"results/monte_carlo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        plot_monte_carlo(equity_curves, final_equities, annual_returns, plot_path_mc)
        print(f"  Monte Carlo plot saved to: {plot_path_mc}")
    
    


if __name__ == "__main__":
    run_backtest()