
import importlib
import core.config as config
import pandas as pd
import numpy as np
from itertools import product
from simulation import backtest

def optimize():
    """
    Perform a grid search optimization over strategy parameters across all sectors.

    Iterates through all sector ticker sets and combinations of alpha, net exposure, 
    and lookback windows, executing backtests for each configuration. Collects and 
    compares performance metrics (Sharpe Ratio, Return) to identify the optimal 
    parameter set for each sector and overall.
    """

    alphas = [0.3, 0.6]
    exposures = [0.4, 0.7, 0.9]
    lookback_windows = [80, 120]

    sector_sets = {
        name: tickers for name, tickers in config.TICKER_SETS.items() 
        if name.startswith('SECTOR_') and len(tickers) > 0
    }

    if config.TICKER_SETS['SP500_FULL_UNIVERSE']:
        sector_sets['SP500_FULL_UNIVERSE'] = config.TICKER_SETS['SP500_FULL_UNIVERSE']

    print(f"Found {len(sector_sets)} ticker sets to optimize: {list(sector_sets.keys())}")
    print(f"Parameter combinations per sector: {len(alphas) * len(exposures) * len(lookback_windows)}")

    all_results = []

    total_runs = len(sector_sets) * len(alphas) * len(exposures) * len(lookback_windows)
    count = 0

    for sector_name, sector_tickers in sector_sets.items():
        print(f"\n{'='*60}")
        print(f"OPTIMIZING SECTOR: {sector_name} ({len(sector_tickers)} tickers)")
        print(f"{'='*60}")

        print(f"Fetching data for {sector_name} (20y)...")
        try:
            backtest.fetch_historical_data(sector_tickers, period='20y', interval='1d')
        except Exception as e:
            print(f"Error fetching data for {sector_name}: {e}")
            continue

        sector_results = []

        for alpha, exposure, lookback in product(alphas, exposures, lookback_windows):
            count += 1
            print(f"\n--- [{count}/{total_runs}] {sector_name}: Alpha={alpha}, Exposure={exposure}, Lookback={lookback} ---")

            try:
                original_tickers = config.TICKERS
                config.TICKERS = sector_tickers

                metrics = backtest.run_backtest({
                    'ALPHA': alpha,
                    'NET_EXPOSURE': exposure,
                    'LOOKBACK_WINDOW': lookback,
                    'REBALANCE_FREQUENCY': 5 
                })

                config.TICKERS = original_tickers

                if metrics:
                    print(f"-> Sharpe: {metrics['Sharpe']:.2f}, Return: {metrics['Return']:.2%}")

                    result = {
                        'Sector': sector_name,
                        'Alpha': alpha,
                        'Exposure': exposure,
                        'Lookback': lookback,
                        'Sharpe': metrics['Sharpe'],
                        'Return': metrics['Return']
                    }
                    sector_results.append(result)
                    all_results.append(result)

            except Exception as e:
                print(f"Error in optimization step: {e}")
                config.TICKERS = original_tickers
                continue

        if sector_results:
            df_sector = pd.DataFrame(sector_results)
            best_sector = df_sector.sort_values(by='Sharpe', ascending=False).iloc[0]
            print(f"\nBest config for {sector_name}:")
            print(f"Alpha={best_sector['Alpha']}, Exposure={best_sector['Exposure']}, Lookback={best_sector['Lookback']}")
            print(f"Sharpe: {best_sector['Sharpe']:.2f}, Return: {best_sector['Return']:.2%}")

    if not all_results:
        print("No results obtained from optimization.")
        return

    df_all = pd.DataFrame(all_results)
    print(f"\n{'='*60}")
    print("OVERALL OPTIMIZATION RESULTS")
    print(f"{'='*60}")

    print(f"\nTop {min(8, len(df_all))} configurations (by Sharpe Ratio):")
    top_configs = df_all.sort_values(by='Sharpe', ascending=False).head(8)
    print(top_configs.to_string(index=False))

    print("\nBest configuration by sector:")
    sector_summary = df_all.loc[df_all.groupby('Sector')['Sharpe'].idxmax()]
    print(sector_summary[['Sector', 'Alpha', 'Exposure', 'Lookback', 'Sharpe', 'Return']].to_string(index=False))

    overall_best = df_all.sort_values(by='Sharpe', ascending=False).iloc[0]
    print(f"\nOverall optimal configuration:")
    print(f"Sector: {overall_best['Sector']}")
    print(f"Alpha={overall_best['Alpha']}, Exposure={overall_best['Exposure']}, Lookback={overall_best['Lookback']}")
    print(f"Sharpe: {overall_best['Sharpe']:.2f}, Return: {overall_best['Return']:.2%}")

    return df_all
    
if __name__ == "__main__":
    optimize()
