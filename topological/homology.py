import numpy as np
import pandas as pd
from ripser import ripser
from persim import plot_diagrams
from typing import Dict, List, Tuple
import sys
import os

from core import config

class TopologicalFeatureExtractor:
    def __init__(self, max_dimension: int = config.MAX_DIMENSION):
        self.max_dimension = max_dimension

    def create_point_cloud(self, correlation_matrix: pd.DataFrame) -> np.ndarray:
        """
        Converts a correlation matrix into a distance matrix/point cloud for TDA.
        Metric: d_ij = sqrt(2 * (1 - rho_ij))
        This transforms correlation (1 to -1) to distance (0 to 2).
        """
        corr = correlation_matrix.values
        
        dist_matrix = np.sqrt(2 * (1 - corr).clip(min=0))

        if not dist_matrix.flags.writeable:
             dist_matrix = dist_matrix.copy()
        
        np.fill_diagonal(dist_matrix, 0)
        
        return dist_matrix

    def compute_persistence_diagrams(self, distance_matrix: np.ndarray) -> List[np.ndarray]:
        """
        Computes persistence diagrams using Vietoris-Rips filtration.
        Returns a list of diagrams [H0, H1, ...].
        """
        results = ripser(distance_matrix, maxdim=self.max_dimension - 1, distance_matrix=True)
        diagrams = results['dgms']
        return diagrams

    def compute_betti_curves(self, diagrams: List[np.ndarray], resolution: int = 100) -> Dict[str, np.ndarray]:
        """
        Computes Betti curves (number of features vs filtration parameter).
        returns: { 'betti_0': array, 'betti_1': array, 'filtration_axis': array }
        """
        all_points = np.vstack([d for d in diagrams if d.size > 0])
        finite_points = all_points[np.isfinite(all_points[:, 1])]
        
        if finite_points.size == 0:
             max_val = 1.0 
        else:
             max_val = np.max(finite_points)
             
        xs = np.linspace(0, max_val * 1.1, resolution)
        
        curves = {}
        for dim, diagram in enumerate(diagrams):
            betti_vals = []
            for x in xs:
                count = np.sum((diagram[:, 0] <= x) & (diagram[:, 1] > x))
                betti_vals.append(count)
            curves[f'betti_{dim}'] = np.array(betti_vals)
            
        curves['filtration_axis'] = xs
        return curves

    def get_regime_metrics(self, diagrams: List[np.ndarray]) -> Dict[str, float]:
        """
        Extracts scalar metrics for the decision engine.
        Using H1 (loops) persistence (Life = Death - Birth)
        """
        h1 = diagrams[1] 
        
        if h1.size == 0:
            return {'max_persistence_h1': 0.0, 'total_persistence_h1': 0.0}
            
        finite_h1 = h1[np.isfinite(h1[:, 1])]
        if finite_h1.size == 0:
             return {'max_persistence_h1': 0.0, 'total_persistence_h1': 0.0}

        persistence = finite_h1[:, 1] - finite_h1[:, 0]
        
        return {
            'max_persistence_h1': np.max(persistence),
            'total_persistence_h1': np.sum(persistence),
            'avg_persistence_h1': np.mean(persistence),
            'num_loops': len(persistence),
            'persistence_entropy_h1': self.compute_persistence_entropy(persistence)
        }

    def compute_persistence_entropy(self, persistence_values: np.ndarray) -> float:
        """
        Calculates Persistence Entropy of a diagram.
        H = - sum(p_i * log(p_i))
        where p_i = l_i / sum(l_i)
        l_i = persistence (lifetime) of feature i.
        """
        if persistence_values.size == 0:
            return 0.0
            
        total_p = np.sum(persistence_values)
        if total_p == 0:
            return 0.0
            
        probs = persistence_values / total_p
        probs = probs[probs > 0]
        
        entropy = -np.sum(probs * np.log2(probs))
        return entropy

if __name__ == "__main__":
    np.random.seed(42)
    t = np.linspace(0, 2*np.pi, 20)
    x = np.cos(t) + np.random.normal(0, 0.1, 20)
    y = np.sin(t) + np.random.normal(0, 0.1, 20)
    data = pd.DataFrame({'x': x, 'y': y}).T 
    
    dummy_returns = pd.DataFrame(np.random.randn(50, 10)) 
    corr = dummy_returns.corr()
    
    topo = TopologicalFeatureExtractor()
    dist = topo.create_point_cloud(corr)
    diagrams = topo.compute_persistence_diagrams(dist)
    
    print("H0 features:", len(diagrams[0]))
    print("H1 features:", len(diagrams[1]))
    
    metrics = topo.get_regime_metrics(diagrams)
    print("Regime Metrics:", metrics)
