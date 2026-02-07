import matplotlib
import sys
import os
import pandas as pd
import numpy as np
import core.config as config
from simulation import backtest
from simulation.monte_carlo import MonteCarloSimulator

sys.stdout.reconfigure(encoding='utf-8')

def run_sector_analysis():
    """
    Run backtests and Monte Carlo simulations across all SECTOR_ ticker sets,
    then aggregate and display a comparative performance report.
    """
    print("Starting Sector Analysis...")
    print("===========================")
    
    sector_keys = [k for k in config.TICKER_SETS.keys() if k.startswith('SECTOR_')]
    
    results = []
    
    for sector in sector_keys:
        sector_name = sector.replace('SECTOR_', '').replace('_', ' ').title()
        tickers = config.TICKER_SETS[sector]
        
        print(f"\nProcessing Sector: {sector_name} ({len(tickers)} tickers)")
        print("-" * 40)

        print(" > Running Backtest...")
        bt_metrics = backtest.run_backtest(override_params={
            'TICKERS': tickers
        })
        if not bt_metrics:
            bt_metrics = {'Return': 0.0, 'Sharpe': 0.0}

        print(" > Running Monte Carlo Simulation...")
        mc = MonteCarloSimulator(tickers=tickers)
        mc_metrics = mc.run()
        if not mc_metrics:
            mc_metrics = {'VaR_95': 0.0, 'CVaR_95': 0.0}
            
        results.append({
            'Sector': sector_name,
            'Tickers': len(tickers),
            'Return': bt_metrics.get('Return', 0.0),
            'Sharpe': bt_metrics.get('Sharpe', 0.0),
            'VaR (95%)': mc_metrics.get('VaR_95', 0.0),
            'CVaR (95%)': mc_metrics.get('CVaR_95', 0.0)
        })
        
    if not results:
        print("No results generated.")
        return

    df = pd.DataFrame(results)

    total_row = {
        'Sector': 'TOTAL / AVG',
        'Tickers': df['Tickers'].sum(),
        'Return': df['Return'].mean(),
        'Sharpe': df['Sharpe'].mean(),
        'VaR (95%)': df['VaR (95%)'].sum(),
        'CVaR (95%)': df['CVaR (95%)'].sum()
    }

    df = pd.concat([df, pd.DataFrame([total_row])], ignore_index=True)

    print("\n\nSECTOR ANALYSIS REPORT")
    print("======================")

    display_df = df.copy()
    display_df['Return'] = display_df['Return'].map('{:.2%}'.format)
    display_df['Sharpe'] = display_df['Sharpe'].map('{:.2f}'.format)
    display_df['VaR (95%)'] = display_df['VaR (95%)'].map('${:,.0f}'.format)
    display_df['CVaR (95%)'] = display_df['CVaR (95%)'].map('${:,.0f}'.format)
    
    print(display_df.to_string(index=False))

    os.makedirs('results', exist_ok=True)
    filename = 'results/sector_analysis.csv'
    df.to_csv(filename, index=False)
    print(f"\nDetailed results saved to {filename}")

if __name__ == "__main__":
    run_sector_analysis()
