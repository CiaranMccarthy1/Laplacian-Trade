import pandas as pd
import numpy as np
from typing import Dict
from core import config

class IntegrationEngine:
    """
    Topological Alpha Engine (TAE)
    ------------------------------
    A systematic global macro engine utilizing Spectral Graph Theory and 1st-order 
    Persistent Homology (H1) to detect structural market regimes. TAE identifies 
    asset decoupling within a manifold of Tech and Commodity clusters to execute 
    adaptive Momentum and Mean-Reversion signals.
    """

    def __init__(self):
        self.stop_loss_pct = config.STOP_LOSS_PCT
        self.max_drawdown_limit = config.MAX_DRAWDOWN_LIMIT
        self.leverage_multiplier = config.LEVERAGE_MULTIPLIER
        self.target_annual_vol = 0.25 
        self.prev_persistence = 0.0

    def get_risk_scalars(self, h1_persistence: float, current_drawdown: float, returns_history: pd.Series) -> float:
        """
        Calculates a composite risk scalar based on structural stability, 
        portfolio drawdown, and realized volatility.
        """
        # Persistence Decay: Early Warning System
        # Reduces exposure by 15% if the market manifold begins to 'loosen' 
        # before price action confirms a reversal.
        persistence_decay = 1.0
        if h1_persistence < self.prev_persistence:
            persistence_decay = 0.85
        self.prev_persistence = h1_persistence

        # Topological Confidence: Scales risk based on the clarity of H1 features.
        topo_scalar = 1.0
        if h1_persistence < 0.05:
            topo_scalar = 0.10  # Structural noise detected; move to minimal size.
        elif h1_persistence < 0.12:
            topo_scalar = 0.95
        
        # Drawdown Shield: Hard protection of principal.
        # De-leverages aggressively as portfolio equity hits the 10-12% DD floor.
        dd_scalar = 1.0
        if current_drawdown < -0.10:
            dd_scalar = 0.0  # Stop-trading protocol triggered.
        elif current_drawdown < -0.05:
            dd_scalar = 0.5
            
        # Volatility Targeting: Ensures consistent risk contribution.
        # Scales leverage inversely to realized vol; includes a 'Persistence Buffer'
        # to allow larger swings during high-conviction structural shifts.
        vol_scalar = 1.0
        if returns_history is not None and len(returns_history) > 20:
            real_vol = returns_history.tail(20).std() * np.sqrt(252)
            if real_vol > 1e-6:
                persistence_buffer = 1.2 if real_vol > 0.30 else 1.0
                vol_scalar = np.clip((self.target_annual_vol / real_vol) * persistence_buffer, 0.7, 2.0)
                
        return topo_scalar * dd_scalar * vol_scalar * persistence_decay

    def get_adaptive_net_exposure(self, h1_persistence: float) -> float:
        """
        Modulates the portfolio Beta. High persistence (H1 > 0.18) triggers 
        full directional bias (Net=1.0). Chaotic regimes (H1 < 0.08) force 
        a Market-Neutral profile (Net=0.0).
        """
        if h1_persistence > 0.18:
            return 1.0
        if h1_persistence < 0.08:
            return 0.0 
        return 0.85

    def generate_signals(self, residuals: pd.Series, regime_metrics: Dict[str, float], 
                         current_drawdown: float = 0.0, returns_history: pd.Series = None) -> pd.DataFrame:
        """
        Synthesizes Z-scored Graph Laplacian residuals into actionable position weights.
        Operates in 'Trend Capture' mode when persistence is high, and 'Arbitrage' 
        mode during structural consolidation.
        """
        
        z_scores = (residuals - residuals.mean()) / (residuals.std() + 1e-6)
        h1_persistence = regime_metrics.get('max_persistence_h1', 0.0)
        
        # Regime Identification: Trend vs Mean-Reversion.
        is_trending = h1_persistence > 0.05 
        raw_signals = z_scores if is_trending else -z_scores 

        # Compute risk-adjusted leverage and exposure bias.
        risk_multiplier = self.get_risk_scalars(h1_persistence, current_drawdown, returns_history)
        adaptive_net = self.get_adaptive_net_exposure(h1_persistence)
        
        # Signal Filtering: Focus capital only on the top 6 topological outliers 
        # that exceed 1.0 standard deviations (or 0.4 in low-vol regimes).
        significant = raw_signals[abs(raw_signals) > 1.0]
        if significant.empty:
            significant = raw_signals[abs(raw_signals) > 0.4]
            
        sorted_sig = significant.sort_values(ascending=False)
        top_n = min(6, len(sorted_sig))
        longs = sorted_sig[sorted_sig > 0].head(top_n)
        shorts = sorted_sig[sorted_sig < 0].tail(top_n)

        active_leverage = self.leverage_multiplier * risk_multiplier
        
        # Dynamic Weight Allocation based on Adaptive Net Exposure.
        long_total = ((1.0 + adaptive_net) / 2.0) * active_leverage
        short_total = ((1.0 - adaptive_net) / 2.0) * active_leverage

        signals = pd.DataFrame(0.0, index=residuals.index, columns=['Signal'])
        if not longs.empty:
            signals.loc[longs.index, 'Signal'] = long_total / len(longs)
        if not shorts.empty:
            signals.loc[shorts.index, 'Signal'] = -short_total / len(shorts)

        return signals