import numpy as np
import pandas as pd
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
        Fetch historical data and calculate returns and covariance.
        """
        print("Fetching market data...")
        # Use fetch_historical_data instead of fetch_data (which is for live context)
        # 1y or 2y is usually sufficient for covariance estimation
        self.data = self.fetcher.fetch_historical_data(period=config.BACKTEST_PERIOD) 
        self.returns = self.fetcher.get_returns()
        
        if self.returns.empty:
            print("No data available for simulation.")
            return

        self.mean_returns = self.returns.mean()
        self.cov_matrix = self.returns.cov()
        
        # Default to equal weighting for the simulation
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
        Run the Monte Carlo simulation using Geometric Brownian Motion with Cholesky decomposition
        to preserve asset correlations.
        """
        if self.returns.empty:
            self.fetch_data()
            
        if self.returns.empty:
            return None

        # Ensure we are working with numpy arrays for stats
        mean_returns_vals = self.mean_returns.values
        cov_matrix_vals = self.cov_matrix.values
        num_assets = len(mean_returns_vals)
        
        # Cholesky Decomposition of Covariance Matrix
        # L * L.T = Cov
        try:
            L = np.linalg.cholesky(cov_matrix_vals)
        except np.linalg.LinAlgError:
            print("Covariance matrix is not positive definite. Using nearest positive definite matrix.")
            # Simple fix: add small jitter to diagonal
            jitter = 1e-6
            try:
                L = np.linalg.cholesky(cov_matrix_vals + np.eye(num_assets) * jitter)
            except:
                print("Matrix still not positive definite. Aborting.")
                return None

        # Simulation storage: (days, simulations) for portfolio value
        portfolio_sims = np.zeros((self.horizon, self.simulations))
        initial_portfolio_value = 10000.0 # Starting with $10k
        
        print(f"Running {self.simulations} simulations over {self.horizon} days...")
        
        # Pre-compute drift (constant)
        # drift = (mu - 0.5 * sigma^2)
        drift = mean_returns_vals - 0.5 * np.diag(cov_matrix_vals)
        
        # Pre-compute Cholesky for correlation
        # correlated_shocks = Z @ L.T
        
        for sim in range(self.simulations):
            # Generate random shocks for all assets over time horizon
            # Shape: (horizon, num_assets)
            Z = np.random.normal(0, 1, (self.horizon, num_assets))
            
            # Correlate shocks
            correlated_shocks = np.dot(Z, L.T)
            
            # Calculate daily returns for each asset
            # R_t = drift + correlated_shocks
            # drift is (1, num_assets) broadcasted
            daily_returns_sim = drift + correlated_shocks
            
            # Asset price paths: Start at 1.0 (cumulative product of exp returns)
            asset_price_paths = np.cumprod(np.exp(daily_returns_sim), axis=0)
            
            # Portfolio value path
            # initial_portfolio_value * sum(weights * asset_price_change)
            # Note: This assumes rebalancing to initial weights every step if we just sum?
            # actually, if we hold fixed shares, it's sum(shares * price).
            # if we rebalance daily to fixed weights, it's portfolio_t = portfolio_{t-1} * (sum(w * exp(r)))
            
            # Simplified: Constant weights (rebalanced daily)
            # Portfolio return at step t: sum(w_i * exp(r_i,t)) - 1
            # Portfolio Value t = Value_{t-1} * (1 + Portfolio Return)
            # OR Value t = Value_{t-1} * sum(w * exp(r))
            
            portfolio_period_returns = np.dot(np.exp(daily_returns_sim), self.weights)
            portfolio_path = initial_portfolio_value * np.cumprod(portfolio_period_returns)
            
            portfolio_sims[:, sim] = portfolio_path

        return portfolio_sims

    def calculate_risk_metrics(self, simulation_results):
        """
        Calculate Value at Risk (VaR) and Conditional Value at Risk (CVaR).
        """
        if simulation_results is None:
            return {}

        final_values = simulation_results[-1, :]
        initial_value = 10000.0
        profit_loss = final_values - initial_value
        
        # Sort P&L
        sorted_pl = np.sort(profit_loss)
        
        # VaR index
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
        Plot the simulation paths.
        """
        if simulation_results is None:
            return

        plt.figure(figsize=(12, 6))
        plt.plot(simulation_results, color='cyan', alpha=0.1, linewidth=0.5)
        plt.plot(np.mean(simulation_results, axis=1), color='red', linewidth=2, label='Mean Path')
        plt.title(f'Monte Carlo Simulation: {self.simulations} Runs over {self.horizon} Days')
        plt.xlabel('Days')
        plt.ylabel('Portfolio Value ($)')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        # Save plot
        import os
        if not os.path.exists('results'):
            os.makedirs('results')
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f'results/monte_carlo_{timestamp}.png'
        plt.savefig(filename)
        print(f"Plot saved to {filename}")
        
        # Show or save

if __name__ == "__main__":
    sim = MonteCarloSimulator()
    metrics = sim.run()
    
    if metrics:
        print("\nSimulation Metrics:")
        for k, v in metrics.items():
            print(f"{k}: {v:,.2f}")
    else:
        print("Simulation failed.")
