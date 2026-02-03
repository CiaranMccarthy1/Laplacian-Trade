import pandas as pd
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt
import config
from datetime import datetime, timedelta, timezone
from spatial.laplacian import SpatialGraph
from topological.homology import TopologicalFeatureExtractor
from integration.decision_engine import IntegrationEngine
import sys
import os

import hashlib

def fetch_historical_data(tickers, period='10y', interval='1d'):
    """
    Fetch a larger chunk of historical data for backtesting.
    Defaults to 5 years of 1d data (hourly data limited to ~2y).
    Checks local cache first.
    """
    cache_dir = "data_cache"
    os.makedirs(cache_dir, exist_ok=True)
    
    safe_period = period.replace(" ", "")
    safe_interval = interval.replace(" ", "")
    
    if config.ACTIVE_TICKER_SET == 'S_AND_P_FULL' and not tickers:
        from data.fetcher import DataFetcher
        tickers = DataFetcher.fetch_sp500_tickers()
        print(f"Fetched {len(tickers)} tickers for S&P 500 List.")
            
    if not tickers:
        print("No tickers to fetch.")
        return pd.DataFrame()

    ticker_hash = hashlib.md5(str(sorted(tickers)).encode()).hexdigest()[:8]
    cache_file = os.path.join(cache_dir, f"market_data_{safe_period}_{safe_interval}_{ticker_hash}.pkl")

    if os.path.exists(cache_file):
        print(f"Loading cached data from {cache_file}...")
        return pd.read_pickle(cache_file)

    data = yf.download(tickers, period=period, interval=interval, group_by='ticker', threads=True, progress=False, auto_adjust=True)
    
    close_data = {}
    for ticker in tickers:
        try:
            if isinstance(data.columns, pd.MultiIndex):
                if (ticker, 'Close') in data.columns:
                    close_data[ticker] = data[(ticker, 'Close')]
                elif ticker in data.columns.levels[0]:
                    close_data[ticker] = data[ticker]['Close']
            elif f"Close_{ticker}" in data.columns:
                    close_data[ticker] = data[f"Close_{ticker}"]
            elif ticker in data.columns: 
                   if 'Close' in data.columns: 
                       try:
                           close_data[ticker] = data[(ticker, 'Close')]
                       except:
                           pass
        except KeyError:
            pass
            
    if close_data:
        df_close = pd.concat(close_data, axis=1)
    else:
        df_close = pd.DataFrame()

    df_close = df_close.ffill().dropna(axis=1, how='all').dropna(how='all') 
    
    if not df_close.empty:
        df_close.to_pickle(cache_file)
        print(f"Data cached to {cache_file}")

    return df_close

def run_backtest(override_params=None):
    """
    Execute the backtest simulation based on configuration.
    
    This function:
    1. Sets up parameters (tickers, alpha, exposure, etc.).
    2. Fetches and prepares historical data.
    3. Iterates through the data window by window:
       - Builds a spatial graph and computes the Laplacian.
       - Extracts topological features (persistence entropy) to adapt alpha.
       - computes diffusion signals and residuals.
       - Generates trading signals via the IntegrationEngine.
       - Calculates transaction costs and Portfolio PnL.
    4. Aggregates and prints performance metrics (Sharpe, Annual Returns).
    5. Generates and saves performance plots.
    """
    tickers = config.TICKERS
    
    alpha = config.ALPHA
    exposure = config.NET_EXPOSURE
    lookback = config.LOOKBACK_WINDOW
    rebal_freq = config.REBALANCE_FREQUENCY
    
    if override_params:
        alpha = override_params.get('ALPHA', alpha)
        exposure = override_params.get('NET_EXPOSURE', exposure)
        lookback = override_params.get('LOOKBACK_WINDOW', lookback)
        rebal_freq = override_params.get('REBALANCE_FREQUENCY', rebal_freq)
        
    prices = fetch_historical_data(tickers, period=config.BACKTEST_PERIOD, interval=config.TIMEFRAME)
    
    if prices.empty:
        print("No data captured for backtest.")
        return

    all_returns = np.log(prices / prices.shift(1)).fillna(0.0)
    
    spatial = SpatialGraph(alpha=alpha, correlation_threshold=config.CORRELATION_THRESHOLD)
    topo = TopologicalFeatureExtractor(max_dimension=config.MAX_DIMENSION)
    engine = IntegrationEngine(risk_mode=config.RISK_MODE)

    config.NET_EXPOSURE = exposure 
    
    portfolio_values = [1.0]
    pnl_history = []
    
    window_size = lookback
    
    print(f"\nRunning backtest on {len(all_returns)} bars with window={window_size}...")
    
    indices = all_returns.index
    
    daily_returns = []
    
    last_regime_metrics = {}
    smoothed_residuals = None
    
    cost_bps = config.TRANSACTION_COST_BPS
    prev_signals = pd.Series(0, index=all_returns.columns)
    
    for i in range(window_size - 1, len(indices) - 1):
        window_returns = all_returns.iloc[i - window_size + 1 : i + 1]
        
        current_return_vector = window_returns.iloc[-1]
        
        if i % rebal_freq == 0:
            try:
                G = spatial.build_graph(window_returns)
                spatial.compute_laplacian(G)
                
                dynamic_alpha = alpha
                
                if hasattr(spatial, 'adjacency_matrix'):
                    dist_matrix = topo.create_point_cloud(spatial.adjacency_matrix)
                    diagrams = topo.compute_persistence_diagrams(dist_matrix)
                    regime_metrics = topo.get_regime_metrics(diagrams)
                    last_regime_metrics = regime_metrics 
                    
                    h_entropy = regime_metrics.get('persistence_entropy_h1', 0.0)
                    
                    if h_entropy > 0.5:
                         dynamic_alpha = 0.05
                    else:
                         dynamic_alpha = alpha
                else:
                    regime_metrics = last_regime_metrics
                    
                diffusion_signal = spatial.compute_diffusion_signal(current_return_vector, override_alpha=dynamic_alpha)
                current_raw_residuals = spatial.get_residuals(current_return_vector, diffusion_signal)
                
                if smoothed_residuals is None:
                    smoothed_residuals = current_raw_residuals
                else:
                    smoothed_residuals = 0.2 * current_raw_residuals + 0.8 * smoothed_residuals
                    
                residuals = smoothed_residuals
                
            except Exception as e:
                residuals = pd.Series(0, index=current_return_vector.index)
                regime_metrics = last_regime_metrics

            signals = engine.generate_signals(residuals, regime_metrics)
            
            current_weights = pd.Series(0.0, index=all_returns.columns)
            if not signals.empty:
                active = signals[signals['Signal'] != 0]['Signal']
                current_weights.loc[active.index] = active
        else:
            current_weights = prev_signals
            
        turnover = np.sum(np.abs(current_weights - prev_signals))
        step_cost = turnover * cost_bps
        
        prev_signals = current_weights
        
        realized_next_return = all_returns.iloc[i+1]
        
        step_pnl_gross = np.sum(current_weights * realized_next_return)
        
        step_pnl = step_pnl_gross - step_cost
            
        daily_returns.append(step_pnl)
        portfolio_values.append(portfolio_values[-1] * (1 + step_pnl))
        
        if i % 50 == 0:
            print(f"Step {i}/{len(indices)} | Cum PnL: {portfolio_values[-1]:.4f} | Cost: {step_cost:.5f}")

    portfolio_values = pd.Series(portfolio_values, index=indices[window_size-1:])
    print("\nBacktest Complete.")
    print(f"Final Portfolio Value: {portfolio_values.iloc[-1]:.4f}")
    
    date_index = indices[window_size:]
    if len(daily_returns) != len(date_index):
        print(f"Warning: Returns length {len(daily_returns)} vs Dates {len(date_index)}")
        min_len = min(len(daily_returns), len(date_index))
        daily_returns = daily_returns[:min_len]
        date_index = date_index[:min_len]

    rets = pd.Series(daily_returns, index=date_index)
    
    sharpe = np.sqrt(252) * (rets.mean() / rets.std())
    print(f"Sharpe Ratio (Approx): {sharpe:.2f}")

    print("\n--- Annual Performance ---")
    annual_stats = []
    
    years = rets.groupby(rets.index.year)
    for year, year_rets in years:
        net_pnl = year_rets.sum()
        annual_stats.append(net_pnl)
        
        if year_rets.std() > 0:
            year_sharpe = np.sqrt(252) * (year_rets.mean() / year_rets.std())
        else:
            year_sharpe = 0.0
            
        print(f"Year {year} | Return: {net_pnl:.2%} | Sharpe: {year_sharpe:.2f}")

    if annual_stats:
        avg_return = np.mean(annual_stats)
        print(f"Average Annual Return: {avg_return:.2%}")
    print("--------------------------\n")
    
    try:
        plt.figure(figsize=(12, 6))
        
        plt.subplot(2, 1, 1)
        portfolio_values.plot(label='Strategy Equity Curve')
        plt.title(f'Backtest Performance (Sharpe: {sharpe:.2f})')
        plt.ylabel('Portfolio Value')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        plt.subplot(2, 1, 2)
        rets.plot(label='Daily Returns', alpha=0.6)
        plt.ylabel('Returns')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.tight_layout()
        
        os.makedirs("results", exist_ok=True)
        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join("results", f'backtest_performance_sharpe_{sharpe:.2f}_{timestamp_str}.png')
        
        plt.savefig(filename)
        print(f"Performance chart saved to '{filename}'")
    except Exception as e:
        print(f"Could not generate plot: {e}")

    return {
        'Sharpe': sharpe,
        'Return': (portfolio_values.iloc[-1] - 1)
    }

if __name__ == "__main__":
    run_backtest()
