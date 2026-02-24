import numpy as np
import pandas as pd
import networkx as nx
from core import config

class SpatialGraph:
    def __init__(self, correlation_threshold: float = config.CORRELATION_THRESHOLD, alpha: float = config.ALPHA):
        self.correlation_threshold = correlation_threshold
        self.alpha = alpha
        self.laplacian = None
        self.adjacency_matrix = None

    def build_graph(self, returns: pd.DataFrame) -> nx.Graph:
        """Build a correlation-based graph where edges exceed the threshold."""
        corr_matrix = returns.corr()
        self.adjacency_matrix = corr_matrix

        adj = corr_matrix.copy()
        for col in adj.columns:
            adj.loc[col, col] = 0
        adj = adj.where(adj >= self.correlation_threshold, 0.0)

        return nx.from_pandas_adjacency(adj)

    def compute_laplacian(self, G: nx.Graph) -> np.ndarray:
        """Compute the normalised Graph Laplacian."""
        self.laplacian = nx.normalized_laplacian_matrix(G).toarray()
        return self.laplacian

    def compute_diffusion_signal(self, current_returns: pd.Series, override_alpha: float = None) -> pd.Series:
        """Solve h = (I - α·L)⁻¹ · x  for the equilibrium diffusion state."""
        if self.laplacian is None:
            raise ValueError("Laplacian not computed. Call build_graph and compute_laplacian first.")

        x = current_returns.values
        n = len(x)
        alpha = override_alpha if override_alpha is not None else self.alpha
        A = np.eye(n) - alpha * self.laplacian

        try:
            h = np.linalg.solve(A, x)
        except np.linalg.LinAlgError:
            h = x

        return pd.Series(h, index=current_returns.index)

    def get_residuals(self, current_returns: pd.Series, diffusion_signal: pd.Series) -> pd.Series:
        """Return residuals e = x − h (deviations from equilibrium)."""
        return current_returns - diffusion_signal
