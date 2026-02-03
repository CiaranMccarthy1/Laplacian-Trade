import pytest
import numpy as np
import pandas as pd
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from spatial.laplacian import SpatialGraph
from topological.homology import TopologicalFeatureExtractor

@pytest.fixture
def sample_returns():
    np.random.seed(42)
    df = pd.DataFrame(np.random.randn(100, 5), columns=['A', 'B', 'C', 'D', 'E'])
    df['B'] = df['A'] * 0.9 + np.random.normal(0, 0.1, 100)
    return df

@pytest.fixture
def spatial_graph():
    return SpatialGraph(correlation_threshold=0.5, alpha=0.5)

@pytest.fixture
def topo_extractor():
    return TopologicalFeatureExtractor()

def test_spatial_graph_construction(spatial_graph, sample_returns):
    G = spatial_graph.build_graph(sample_returns)
    assert G.number_of_nodes() == 5
    assert G.has_edge('A', 'B')

def test_laplacian_shape(spatial_graph, sample_returns):
    G = spatial_graph.build_graph(sample_returns)
    L = spatial_graph.compute_laplacian(G)
    assert L.shape == (5, 5)

def test_diffusion_signal(spatial_graph, sample_returns):
    G = spatial_graph.build_graph(sample_returns)
    spatial_graph.compute_laplacian(G)
    
    current = sample_returns.iloc[-1]
    h = spatial_graph.compute_diffusion_signal(current)
    
    assert len(h) == 5
    assert isinstance(h, pd.Series)

def test_topological_point_cloud(topo_extractor, sample_returns):
    corr = sample_returns.corr()
    dist = topo_extractor.create_point_cloud(corr)
    
    assert dist.shape == (5, 5)
    assert np.all(dist >= 0)
    assert np.allclose(np.diag(dist), 0)

def test_persistence_diagrams(topo_extractor, sample_returns):
    corr = sample_returns.corr()
    dist = topo_extractor.create_point_cloud(corr)
    diagrams = topo_extractor.compute_persistence_diagrams(dist)
    
    assert len(diagrams) >= 1
    assert isinstance(diagrams[0], np.ndarray)

def test_regime_metrics(topo_extractor, sample_returns):
    corr = sample_returns.corr()
    dist = topo_extractor.create_point_cloud(corr)
    diagrams = topo_extractor.compute_persistence_diagrams(dist)
    metrics = topo_extractor.get_regime_metrics(diagrams)
    
    assert 'max_persistence_h1' in metrics
    assert isinstance(metrics['max_persistence_h1'], float)
