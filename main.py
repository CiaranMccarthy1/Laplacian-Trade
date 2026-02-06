import time
import pandas as pd
from datetime import datetime
from core import config
from data.fetcher import DataFetcher
from spatial.laplacian import SpatialGraph
from topological.homology import TopologicalFeatureExtractor
from integration.decision_engine import IntegrationEngine
import sys

def main():
    """
    Main entry point for the Topological Arbitrage System.
    
    Orchestrates the data fetching, spatial graph construction, topological data analysis,
    signal generation, and trade execution simulation. Runs a single pass representing
    an automated trading interval.
    """
    print("Initializing Topological Arb System...")
    
    fetcher = DataFetcher(tickers=config.TICKERS)
    spatial = SpatialGraph(alpha=config.ALPHA, correlation_threshold=config.CORRELATION_THRESHOLD)
    topo = TopologicalFeatureExtractor(max_dimension=config.MAX_DIMENSION)
    engine = IntegrationEngine()
    
    print(f"Fetching data (Lookback: {config.LOOKBACK_WINDOW}m)...")
    price_data = fetcher.fetch_data(lookback_minutes=config.LOOKBACK_WINDOW)
    
    if price_data.empty:
        print("No data fetched. Exiting.")
        return

    returns = fetcher.get_returns()
    if returns.empty:
         print("Not enough data for returns. Exiting.")
         return

    print(f"Data shape: {returns.shape}")

    print("\n[T-60m] Building Spatial Graph...")
    G = spatial.build_graph(returns)
    spatial.compute_laplacian(G)
    print(f"Graph constructed with {G.number_of_nodes()} nodes and {G.number_of_edges()} edges.")

    print("\n[T-30m] Running Persistent Homology...")
    corr_matrix = spatial.adjacency_matrix
    point_cloud = topo.create_point_cloud(corr_matrix)
    diagrams = topo.compute_persistence_diagrams(point_cloud)
    
    regime_metrics = topo.get_regime_metrics(diagrams)
    print(f"Regime Metrics: {regime_metrics}")
    
    print("\n[T-1m] Calculating Diffusion Signal and Residuals...")
    current_returns = returns.iloc[-1]
    
    try:
        diffusion_signal = spatial.compute_diffusion_signal(current_returns)
        residuals = spatial.get_residuals(current_returns, diffusion_signal)
    except Exception as e:
        print(f"Error in spatial calculation: {e}")
        return

    print("\n[Market Open] Generating Trade Signals...")
    signals = engine.generate_signals(residuals, regime_metrics)
    
    active_signals = signals[signals['Signal'] != 0].copy()
    if not active_signals.empty:
        print("Active Signals:")
        print(active_signals)
    else:
        print("No trading signals generated.")

if __name__ == "__main__":
    main()
