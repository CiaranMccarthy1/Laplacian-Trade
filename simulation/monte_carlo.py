import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from datetime import datetime
import core.config as config
from data.fetcher import DataFetcher

class MonteCarloSimulator:
    def __init__(self, tickers=None, simulations: int = config.MC_SIMULATIONS, horizon: int = config.MC_HORIZON_DAYS):
        """
        Initialize the Monte Carlo Simulator.
        
        :param tickers: List of tickers to simulate.
        :param simulations: Number of simulation runs.
        :param horizon: Time horizon in days.
        """
        self.simulations = simulations
        self.horizon = horizon
        self.tickers = tickers if tickers is not None else config.TICKERS
        self.fetcher = DataFetcher(tickers=self.tickers)
        self.data = pd.DataFrame()
        self.returns = pd.DataFrame()
        self.mean_returns = None
        self.cov_matrix = None
        self.weights = None

    def fetch_data(self):
        """
        Fetch historical data and calculate returns, covariance matrix,
        and equal-weight portfolio allocation.
        """
        print("Fetching market data...")
        self.data = self.fetcher.fetch_historical_data(period=config.BACKTEST_PERIOD) 
        self.returns = self.fetcher.get_returns()
        
        if self.returns.empty:
            print("No data available for simulation.")
            return

        self.mean_returns = self.returns.mean()
        self.cov_matrix = self.returns.cov()
        
        num_assets = len(self.mean_returns)
        if num_assets > 0:
            self.weights = np.ones(num_assets) / num_assets
        else:
            self.weights = np.array([])
            
        print(f"Data fetched for {num_assets} assets.")

    def run(self):
        """
        Orchestrate the full simulation flow and return metrics.
        """
        self.fetch_data()
        results = self.run_simulation()
        if results is not None:
            metrics = self.calculate_risk_metrics(results)
            self.plot_simulation(results)
            return metrics
        return {}

    def run_simulation(self):
        """
        Run the Monte Carlo simulation using Geometric Brownian Motion with Cholesky
        decomposition to preserve asset correlations.

        Uses drift = (mu - 0.5 * sigma^2) with correlated shocks via L * L.T = Cov.
        Assumes constant equal weights rebalanced daily.
        """
        if self.returns.empty:
            self.fetch_data()

        if self.returns.empty:
            return None

        mean_returns_vals = self.mean_returns.values
        cov_matrix_vals = self.cov_matrix.values
        num_assets = len(mean_returns_vals)

        try:
            L = np.linalg.cholesky(cov_matrix_vals)
        except np.linalg.LinAlgError:
            print("Covariance matrix is not positive definite. Using nearest positive definite matrix.")
            jitter = 1e-6
            try:
                L = np.linalg.cholesky(cov_matrix_vals + np.eye(num_assets) * jitter)
            except:
                print("Matrix still not positive definite. Aborting.")
                return None

        portfolio_sims = np.zeros((self.horizon, self.simulations))
        initial_portfolio_value = 10000.0

        print(f"Running {self.simulations} simulations over {self.horizon} days...")

        drift = mean_returns_vals - 0.5 * np.diag(cov_matrix_vals)

        for sim in range(self.simulations):
            Z = np.random.normal(0, 1, (self.horizon, num_assets))
            correlated_shocks = np.dot(Z, L.T)
            daily_returns_sim = drift + correlated_shocks
            asset_price_paths = np.cumprod(np.exp(daily_returns_sim), axis=0)

            portfolio_period_returns = np.dot(np.exp(daily_returns_sim), self.weights)
            portfolio_path = initial_portfolio_value * np.cumprod(portfolio_period_returns)

            portfolio_sims[:, sim] = portfolio_path

        return portfolio_sims

    def calculate_risk_metrics(self, simulation_results):
        """
        Calculate Value at Risk (VaR) and Conditional Value at Risk (CVaR)
        from the final simulation values at the given confidence level.
        """
        if simulation_results is None:
            return {}

        final_values = simulation_results[-1, :]
        initial_value = 10000.0
        profit_loss = final_values - initial_value

        sorted_pl = np.sort(profit_loss)

        confidence_level = config.MC_CONFIDENCE_LEVEL
        index = int((1 - confidence_level) * self.simulations)

        var = abs(sorted_pl[index])
        cvar = abs(sorted_pl[:index].mean())
        
        return {
            "VaR_95": var,
            "CVaR_95": cvar,
            "Mean_Final_Value": np.mean(final_values),
            "Median_Final_Value": np.median(final_values),
            "Min_Final_Value": np.min(final_values),
            "Max_Final_Value": np.max(final_values)
        }

    def plot_simulation(self, simulation_results):
        """
        Plot all simulation paths with the mean path highlighted,
        and save the figure to the results directory.
        """
        if simulation_results is None:
            return

        plt.figure(figsize=(12, 6))
        plt.plot(simulation_results, color='cyan', alpha=0.1, linewidth=0.5)
        plt.plot(np.mean(simulation_results, axis=1), color='red', linewidth=2, label='Mean Path')

        sector_info = ""
        if hasattr(self, 'tickers') and len(self.tickers) > 0:
            if self.tickers == config.TICKER_SETS.get('DEFAULT_MIXED', []):
                sector_info = " (DEFAULT_MIXED)"
            else:
                for sector_name, sector_tickers in config.TICKER_SETS.items():
                    if sector_name.startswith('SECTOR_') and self.tickers == sector_tickers:
                        sector_info = f" ({sector_name})"
                        break

        plt.title(f'Monte Carlo Simulation{sector_info}: {self.simulations} Runs over {self.horizon} Days')
        plt.xlabel('Days')
        plt.ylabel('Portfolio Value ($)')
        plt.legend()
        plt.grid(True, alpha=0.3)

        import os
        if not os.path.exists('results'):
            os.makedirs('results')

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        sector_suffix = sector_info.replace(" (", "_").replace(")", "").replace(" ", "") if sector_info else ""
        filename = f'results/monte_carlo{sector_suffix}_{timestamp}.png'
        plt.savefig(filename)
        print(f"Plot saved to {filename}")

        plt.close()

if __name__ == "__main__":
    """
    Run Monte Carlo simulations across all sectors for comprehensive risk analysis.
    """
    import core.config as config

    sector_sets = {
        name: tickers for name, tickers in config.TICKER_SETS.items() 
        if name.startswith('SECTOR_') and len(tickers) > 0
    }

    if config.TICKER_SETS['SP500_FULL_UNIVERSE']:
        sector_sets['SP500_FULL_UNIVERSE'] = config.TICKER_SETS['SP500_FULL_UNIVERSE']

    print(f"Running Monte Carlo simulations for {len(sector_sets)} sectors:")
    print(f"Sectors: {list(sector_sets.keys())}")
    print(f"Simulations per sector: {config.MC_SIMULATIONS}")
    print(f"Horizon: {config.MC_HORIZON_DAYS} days\n")

    all_sector_metrics = []

    for sector_name, sector_tickers in sector_sets.items():
        print(f"\n{'='*60}")
        print(f"MONTE CARLO SIMULATION: {sector_name} ({len(sector_tickers)} tickers)")
        print(f"{'='*60}")

        try:
            sim = MonteCarloSimulator(tickers=sector_tickers)
            metrics = sim.run()

            if metrics:
                metrics['Sector'] = sector_name
                metrics['Num_Tickers'] = len(sector_tickers)
                all_sector_metrics.append(metrics)

                print(f"\n{sector_name} Risk Metrics:")
                print(f"  VaR (95%): ${metrics['VaR_95']:,.2f}")
                print(f"  CVaR (95%): ${metrics['CVaR_95']:,.2f}")
                print(f"  Mean Final Value: ${metrics['Mean_Final_Value']:,.2f}")
                print(f"  Median Final Value: ${metrics['Median_Final_Value']:,.2f}")
                print(f"  Min Final Value: ${metrics['Min_Final_Value']:,.2f}")
                print(f"  Max Final Value: ${metrics['Max_Final_Value']:,.2f}")

                initial_value = 10000.0
                mean_return_pct = (metrics['Mean_Final_Value'] - initial_value) / initial_value * 100
                print(f"  Expected Return: {mean_return_pct:.2f}%")

            else:
                print(f"Simulation failed for {sector_name}")

        except Exception as e:
            print(f"Error simulating {sector_name}: {e}")
            continue

    if all_sector_metrics:
        print(f"\n{'='*80}")
        print("SECTOR MONTE CARLO RISK COMPARISON")
        print(f"{'='*80}")

        import pandas as pd
        df_metrics = pd.DataFrame(all_sector_metrics)

        df_summary = df_metrics.sort_values('VaR_95')

        print("\nSector Risk Rankings (sorted by VaR - lower is better):")
        print("-" * 80)

        for _, row in df_summary.iterrows():
            initial_value = 10000.0
            expected_return = (row['Mean_Final_Value'] - initial_value) / initial_value * 100
            print(f"{row['Sector']:<25} | VaR: ${row['VaR_95']:>8,.0f} | CVaR: ${row['CVaR_95']:>8,.0f} | Expected Return: {expected_return:>6.1f}%")

        best_risk = df_summary.iloc[0]
        worst_risk = df_summary.iloc[-1]

        print(f"\nLOWEST RISK: {best_risk['Sector']}")
        print(f"   VaR (95%): ${best_risk['VaR_95']:,.2f}")
        print(f"   CVaR (95%): ${best_risk['CVaR_95']:,.2f}")

        print(f"\nHIGHEST RISK: {worst_risk['Sector']}")
        print(f"   VaR (95%): ${worst_risk['VaR_95']:,.2f}")
        print(f"   CVaR (95%): ${worst_risk['CVaR_95']:,.2f}")

        df_by_return = df_metrics.sort_values('Mean_Final_Value', ascending=False)
        best_return = df_by_return.iloc[0]
        initial_value = 10000.0
        best_return_pct = (best_return['Mean_Final_Value'] - initial_value) / initial_value * 100

        print(f"\nHIGHEST EXPECTED RETURN: {best_return['Sector']}")
        print(f"   Expected Return: {best_return_pct:.2f}%")
        print(f"   VaR (95%): ${best_return['VaR_95']:,.2f}")

        print(f"\nRISK-ADJUSTED PERFORMANCE:")
        print("   (Expected Return % / VaR)")
        print("-" * 50)

        for _, row in df_metrics.iterrows():
            expected_return = (row['Mean_Final_Value'] - initial_value) / initial_value * 100
            risk_adj = expected_return / (row['VaR_95'] / 100) if row['VaR_95'] > 0 else 0
            print(f"   {row['Sector']:<25}: {risk_adj:>6.3f}")

        import os
        from datetime import datetime
        if not os.path.exists('results'):
            os.makedirs('results')

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f'results/monte_carlo_sectors_{timestamp}.csv'
        df_metrics.to_csv(filename, index=False)
        print(f"\n💾 Results saved to {filename}")

    else:
        print("No successful simulations completed.")

    print(f"\n{'='*80}")
    print("MONTE CARLO SECTOR ANALYSIS COMPLETE")
    print(f"{'='*80}")
