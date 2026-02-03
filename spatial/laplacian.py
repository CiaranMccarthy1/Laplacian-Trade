import numpy as np
import pandas as pd
import networkx as nx
from typing import Tuple
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

class SpatialGraph:
    def __init__(self, correlation_threshold: float = config.CORRELATION_THRESHOLD, alpha: float = config.ALPHA):
        self.correlation_threshold = correlation_threshold
        self.alpha = alpha
        self.laplacian = None
        self.adjacency_matrix = None

    def build_graph(self, returns: pd.DataFrame) -> nx.Graph:
        """
        Builds a graph where nodes are stocks and edges are correlations > threshold.
        """
        corr_matrix = returns.corr()
        self.adjacency_matrix = corr_matrix
        
        adj = corr_matrix.copy()
        
        for col in adj.columns:
            adj.loc[col, col] = 0
        
        adj = adj.where(adj >= self.correlation_threshold, 0.0)
        
        G = nx.from_pandas_adjacency(adj)
        return G

    def compute_laplacian(self, G: nx.Graph) -> np.ndarray:
        """
        Computes the normalized Graph Laplacian.
        """
        L_sparse = nx.normalized_laplacian_matrix(G)
        self.laplacian = L_sparse.toarray()
        return self.laplacian

    def compute_diffusion_signal(self, current_returns: pd.Series, override_alpha: float = None) -> pd.Series:
        """
        Solves for the equilibrium state h = (I - alpha * L)^(-1) * x
        Where x is the current returns vector.
        """
        if self.laplacian is None:
            raise ValueError("Laplacian not computed. Call build_graph and compute_laplacian first.")
            
        n = len(current_returns)
        if self.laplacian.shape[0] != n:
             pass

        x = current_returns.values
        I = np.eye(n)
        
        alpha = override_alpha if override_alpha is not None else self.alpha
        
        A = I - alpha * self.laplacian
        
        try:
            h = np.linalg.solve(A, x)
        except np.linalg.LinAlgError:
            h = x 
            
        return pd.Series(h, index=current_returns.index)

    def get_residuals(self, current_returns: pd.Series, diffusion_signal: pd.Series) -> pd.Series:
        """
        Calculates residuals e = x - h.
        High residuals indicate statistical outliers.
        """
        residuals = current_returns - diffusion_signal
        return residuals

if __name__ == "__main__":
    np.random.seed(42)
    dummy_returns = pd.DataFrame(np.random.randn(100, 5), columns=['A', 'B', 'C', 'D', 'E'])
    dummy_returns['B'] = dummy_returns['A'] * 0.9 + np.random.normal(0, 0.1, 100)
    
    spatial = SpatialGraph(correlation_threshold=0.3)
    G = spatial.build_graph(dummy_returns)
    print("Graph Edges:", G.edges())
    
    L = spatial.compute_laplacian(G)
    print("Laplacian shape:", L.shape)
    
    current = dummy_returns.iloc[-1]
    h = spatial.compute_diffusion_signal(current)
    e = spatial.get_residuals(current, h)
    
    print("\nCurrent Returns:\n", current)
    print("\nDiffusion Signal:\n", h)
    print("\nResiduals:\n", e)
