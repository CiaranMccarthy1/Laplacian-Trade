import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from datetime import datetime

from core import config
from data.fetcher import DataFetcher


class MonteCarloSimulator:
    """Geometric Brownian Motion Monte Carlo with correlated assets."""

    def __init__(self, simulations: int = config.MC_SIMULATIONS, horizon: int = config.MC_HORIZON_DAYS):
        self.simulations = simulations
        self.horizon = horizon
        self.fetcher = DataFetcher()
        self.returns = pd.DataFrame()
        self.mean_returns = None
        self.cov_matrix = None
        self.weights = None

    def fetch_data(self):
        """Fetch historical data and compute return statistics."""
        self.fetcher.fetch_historical_data(period=config.BACKTEST_PERIOD)
        self.returns = self.fetcher.get_returns()

        if self.returns.empty:
            print("No data available for simulation.")
            return

        self.mean_returns = self.returns.mean()
        self.cov_matrix = self.returns.cov()
        n = len(self.mean_returns)
        self.weights = np.ones(n) / n if n > 0 else np.array([])

    def run(self):
        """Full pipeline: fetch → simulate → metrics → plot."""
        self.fetch_data()
        results = self._simulate()
        if results is None:
            return {}
        metrics = self._risk_metrics(results)
        self._plot(results)
        return metrics

    def _simulate(self) -> np.ndarray | None:
        """Run GBM with Cholesky-correlated shocks."""
        if self.returns.empty:
            return None

        mu = self.mean_returns.values
        cov = self.cov_matrix.values
        n = len(mu)

        try:
            L = np.linalg.cholesky(cov)
        except np.linalg.LinAlgError:
            try:
                L = np.linalg.cholesky(cov + np.eye(n) * 1e-6)
            except np.linalg.LinAlgError:
                print("Covariance matrix not positive-definite. Aborting.")
                return None

        drift = mu - 0.5 * np.diag(cov)
        initial_value = 10_000.0
        sims = np.zeros((self.horizon, self.simulations))

        for s in range(self.simulations):
            Z = np.random.normal(0, 1, (self.horizon, n))
            daily = drift + Z @ L.T
            port_ret = np.exp(daily) @ self.weights
            sims[:, s] = initial_value * np.cumprod(port_ret)

        return sims

    @staticmethod
    def _risk_metrics(results: np.ndarray) -> dict:
        """Compute VaR and CVaR at the configured confidence level."""
        final = results[-1, :]
        pnl = np.sort(final - 10_000.0)
        idx = int((1 - config.MC_CONFIDENCE_LEVEL) * len(pnl))
        return {
            'VaR_95': abs(pnl[idx]),
            'CVaR_95': abs(pnl[:idx].mean()),
            'Mean_Final_Value': float(np.mean(final)),
            'Median_Final_Value': float(np.median(final)),
        }

    def _plot(self, results: np.ndarray):
        """Save a simulation fan chart to results/."""
        os.makedirs('results', exist_ok=True)
        plt.figure(figsize=(12, 6))
        plt.plot(results, color='cyan', alpha=0.05, linewidth=0.5)
        plt.plot(np.mean(results, axis=1), color='red', linewidth=2, label='Mean')
        plt.title(f'Monte Carlo: {self.simulations} runs, {self.horizon} days')
        plt.xlabel('Days')
        plt.ylabel('Portfolio Value ($)')
        plt.legend()
        plt.grid(True, alpha=0.3)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        fname = f'results/monte_carlo_{ts}.png'
        plt.savefig(fname)
        plt.close()
        print(f"Plot saved to {fname}")


if __name__ == "__main__":
    sim = MonteCarloSimulator()
    metrics = sim.run()
    if metrics:
        for k, v in metrics.items():
            print(f"  {k}: ${v:,.2f}")
