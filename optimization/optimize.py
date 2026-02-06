
import importlib
import core.config as config
import pandas as pd
import numpy as np
from itertools import product
from simulation import backtest

def optimize():
    """
    Perform a grid search optimization over strategy parameters.
    
    Iterates through combinations of alpha, net exposure, and lookback windows,
    executing backtests for each configuration. Collects and compares performance
    metrics (Sharpe Ratio, Return) to identify the optimal parameter set.
    """
    alphas = [0.1, 0.3, 0.5] 
    exposures = [0.2, 0.4, 0.6] 
    lookback_windows = [60, 100, 120]
    
    print("Fetching data for optimization (20y)...")
    backtest.fetch_historical_data(config.TICKERS, period='20y', interval='1d')
    
    results = []
    
    count = 0
    total_runs = len(alphas) * len(exposures) * len(lookback_windows)
    
    for alpha, exposure, lookback in product(alphas, exposures, lookback_windows):
        count += 1
        print(f"\n--- [{count}/{total_runs}] Testing Alpha={alpha}, Exposure={exposure}, Lookback={lookback} ---")
        
        try:
            metrics = backtest.run_backtest({
                'ALPHA': alpha,
                'NET_EXPOSURE': exposure,
                'LOOKBACK_WINDOW': lookback,
                'REBALANCE_FREQUENCY': 5 
            })
            
            if metrics:
                print(f"-> Sharpe: {metrics['Sharpe']:.2f}, Return: {metrics['Return']:.2%}")
                
                results.append({
                    'Alpha': alpha,
                    'Exposure': exposure,
                    'Lookback': lookback,
                    'Sharpe': metrics['Sharpe'],
                    'Return': metrics['Return']
                })
                
        except Exception as e:
            print(f"Error in optimization step: {e}")
            continue

    if not results:
        print("No results.")
        return

    df_res = pd.DataFrame(results)
    print("\nOptimization Results:")
    print(df_res.sort_values(by='Sharpe', ascending=False))
    
    best = df_res.sort_values(by='Sharpe', ascending=False).iloc[0]
    print(f"\nOptimal Config for Max Sharpe: Alpha={best['Alpha']}, Exposure={best['Exposure']}, Lookback={best['Lookback']}")
    
if __name__ == "__main__":
    optimize()
