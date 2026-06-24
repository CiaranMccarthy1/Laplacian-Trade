import pandas as pd
import numpy as np
from typing import Dict
from core import config

class IntegrationEngine:

    def __init__(self):
        self.leverage_multiplier = config.LEVERAGE_MULTIPLIER
        self.target_annual_vol = 0.35 
        self.prev_persistence = 0.0
        self.regime_state = 'neutral'
        self.regime_counter = 0
        self.max_drawdown_limit = config.MAX_DRAWDOWN_LIMIT
        

    def get_risk_scalars(self, h1_persistence: float, current_drawdown: float, returns_history: pd.Series) -> float:
            if current_drawdown < -self.max_drawdown_limit:
                return 0.0
            elif current_drawdown < 0:
                return 1.0 + (current_drawdown / self.max_drawdown_limit)
            else:
                return 1.0

    def get_adaptive_net_exposure(self, h1_persistence: float) -> float:
        """
        Modulates the portfolio Beta. High persistence (H1 > 0.18) triggers 
        full directional bias (Net=1.0). Chaotic regimes (H1 < 0.08) force 
        a Market-Neutral profile (Net=0.0).
        """
        if h1_persistence > 0.04:
            return 1.0
        if h1_persistence < 0.0015:
            return 0.0 
        return 0.85

    def generate_signals(self, residuals: pd.Series, regime_metrics: Dict[str, float], 
                     current_drawdown: float = 0.0, returns_history: pd.Series = None) -> pd.DataFrame:
        """
        Simplified signal generation without confidence filtering.
        Uses binary regime switch with hysteresis for energy markets.
        """
        
        z_scores = (residuals - residuals.mean()) / (residuals.std() + 1e-6)
        h1_persistence = regime_metrics.get('max_persistence_h1', 0.0)
        
        # --- REGIME SWITCH  ---
        # 0.02 = trend threshold, 0.01 = revert threshold
        if h1_persistence > 0.025:
            self.regime_counter = min(self.regime_counter + 1, 3)
            if self.regime_counter >= 2:
                self.regime_state = 'trend'
        elif h1_persistence < 0.01:
            self.regime_counter = max(self.regime_counter - 1, -3)
            if self.regime_counter <= -2:
                self.regime_state = 'revert'
        # else: stay in current regime
        
        raw_signals = z_scores if self.regime_state == 'trend' else -z_scores
        
        # --- SIGNAL FILTERING  ---
        significant = raw_signals[abs(raw_signals) > 1.0]
        if significant.empty:
            significant = raw_signals[abs(raw_signals) > 0.4]
            
        sorted_sig = significant.sort_values(ascending=False)
        top_n = min(6, len(sorted_sig))
        longs = sorted_sig[sorted_sig > 0].head(top_n)
        shorts = sorted_sig[sorted_sig < 0].tail(top_n)
        
        # --- RISK MANAGEMENT ---
        risk_multiplier = self.get_risk_scalars(h1_persistence, current_drawdown, returns_history)
        adaptive_net = self.get_adaptive_net_exposure(h1_persistence)
        
        # Apply risk scalers 
        active_leverage = self.leverage_multiplier * risk_multiplier
        
        long_total = ((1.0 + adaptive_net) / 2.0) * active_leverage
        short_total = ((1.0 - adaptive_net) / 2.0) * active_leverage
        
        signals = pd.DataFrame(0.0, index=residuals.index, columns=['Signal'])
        if not longs.empty:
            exp_weights = np.exp(longs * 0.5)
            signals.loc[longs.index, 'Signal'] = long_total * exp_weights / exp_weights.sum()
        if not shorts.empty:
            exp_weights = np.exp(np.abs(shorts) * 0.5)
            signals.loc[shorts.index, 'Signal'] = -short_total * exp_weights / exp_weights.sum()
        
        return signals