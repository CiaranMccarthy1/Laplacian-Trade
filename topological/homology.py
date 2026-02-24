import numpy as np
import pandas as pd
from ripser import ripser
from typing import Dict, List
from core import config


class TopologicalFeatureExtractor:
    def __init__(self, max_dimension: int = config.MAX_DIMENSION):
        self.max_dimension = max_dimension

    def create_point_cloud(self, correlation_matrix: pd.DataFrame) -> np.ndarray:
        """Convert a correlation matrix to a distance matrix: d = √(2·(1 − ρ))."""
        corr = correlation_matrix.values
        dist_matrix = np.sqrt(2 * (1 - corr).clip(min=0))
        if not dist_matrix.flags.writeable:
            dist_matrix = dist_matrix.copy()
        np.fill_diagonal(dist_matrix, 0)
        return dist_matrix

    def compute_persistence_diagrams(self, distance_matrix: np.ndarray) -> List[np.ndarray]:
        """Compute persistence diagrams via Vietoris-Rips filtration."""
        results = ripser(distance_matrix, maxdim=self.max_dimension - 1, distance_matrix=True)
        return results['dgms']

    def get_regime_metrics(self, diagrams: List[np.ndarray]) -> Dict[str, float]:
        """Extract scalar regime metrics from H1 persistence."""
        h1 = diagrams[1]

        if h1.size == 0:
            return {'max_persistence_h1': 0.0, 'total_persistence_h1': 0.0}

        finite_h1 = h1[np.isfinite(h1[:, 1])]
        if finite_h1.size == 0:
            return {'max_persistence_h1': 0.0, 'total_persistence_h1': 0.0}

        persistence = finite_h1[:, 1] - finite_h1[:, 0]

        return {
            'max_persistence_h1': float(np.max(persistence)),
            'total_persistence_h1': float(np.sum(persistence)),
            'avg_persistence_h1': float(np.mean(persistence)),
            'num_loops': len(persistence),
            'persistence_entropy_h1': self._persistence_entropy(persistence),
        }

    @staticmethod
    def _persistence_entropy(persistence_values: np.ndarray) -> float:
        """H = −Σ pᵢ log₂ pᵢ  where pᵢ = lᵢ / Σlᵢ."""
        if persistence_values.size == 0:
            return 0.0
        total = np.sum(persistence_values)
        if total == 0:
            return 0.0
        probs = persistence_values / total
        probs = probs[probs > 0]
        return float(-np.sum(probs * np.log2(probs)))
