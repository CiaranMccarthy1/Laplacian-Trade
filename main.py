import pandas as pd
from core import config
from data.fetcher import DataFetcher
from spatial.laplacian import SpatialGraph
from topological.homology import TopologicalFeatureExtractor
from integration.decision_engine import IntegrationEngine


def main():
    """Single-pass execution: fetch data → build graph → TDA → generate signals."""
    print("Initializing Topological Arb System...")

    fetcher = DataFetcher()
    spatial = SpatialGraph()
    topo = TopologicalFeatureExtractor()
    engine = IntegrationEngine()

    print(f"Fetching data (lookback={config.LOOKBACK_WINDOW})...")
    price_data = fetcher.fetch_data()
    if price_data.empty:
        print("No data fetched. Exiting.")
        return

    returns = fetcher.get_returns()
    if returns.empty:
        print("Not enough data for returns. Exiting.")
        return

    print(f"Data shape: {returns.shape}")

    print("\nBuilding Spatial Graph...")
    G = spatial.build_graph(returns)
    spatial.compute_laplacian(G)
    print(f"Graph: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")

    print("\nRunning Persistent Homology...")
    point_cloud = topo.create_point_cloud(spatial.adjacency_matrix)
    diagrams = topo.compute_persistence_diagrams(point_cloud)
    regime_metrics = topo.get_regime_metrics(diagrams)
    print(f"Regime Metrics: {regime_metrics}")

    print("\nComputing Diffusion Signal...")
    current_returns = returns.iloc[-1]
    try:
        diffusion_signal = spatial.compute_diffusion_signal(current_returns)
        residuals = spatial.get_residuals(current_returns, diffusion_signal)
    except Exception as e:
        print(f"Error in spatial calculation: {e}")
        return

    print("\nGenerating Trade Signals...")
    signals = engine.generate_signals(residuals, regime_metrics)
    active = signals[signals['Signal'] != 0]

    if not active.empty:
        print("Active Signals:")
        print(active)
    else:
        print("No trading signals generated.")


if __name__ == "__main__":
    main()
