import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
import sys
import os

from core import config

class IntegrationEngine:
    def __init__(self, risk_mode: str = config.RISK_MODE):
        profile = config.RISK_PROFILES.get(risk_mode.upper(), config.RISK_PROFILES['STANDARD'])
        
        self.max_drawdown_limit = profile['MAX_DRAWDOWN_LIMIT']
        self.stop_loss_pct = profile['STOP_LOSS_PCT']
        self.leverage_multiplier = profile['LEVERAGE_MULTIPLIER']
        
        print(f"Integration Engine Initialized. Mode: {risk_mode} | Leverage: {self.leverage_multiplier}x")

    def calculate_regime_multiplier(self, topological_metrics: Dict[str, float]) -> float:
        """
        Determines the position size multiplier based on topological stability.
        Logic: If H1 persistence is high, structure is stable -> Multiplier = 1.0.
               If H1 persistence collapses (low), market is unstable -> Multiplier < 1.0.
        """
        persistence = topological_metrics.get('max_persistence_h1', 0.0)
        
        if persistence < 0.1:
            return 0.5
        return 1.0

    def check_risk_stops(self, current_drawdown: float) -> bool:
        """
        Returns False if trading should stop due to risk limits.
        """
        if current_drawdown > self.max_drawdown_limit:
            return False
        return True

    def generate_signals(self, residuals: pd.Series, regime_metrics: Dict[str, float]) -> pd.DataFrame:
        """
        Combines residuals and regime metrics to output target positions.
        """
        z_scores = (residuals - residuals.mean()) / residuals.std()
        
        significant_z = z_scores[abs(z_scores) > 0.5]
        
        if significant_z.empty:
            significant_z = z_scores
            
        sorted_z = significant_z.sort_values(ascending=False)
        
        top_n = 10
        
        longs = sorted_z[sorted_z > 0].head(top_n)  
        shorts = sorted_z[sorted_z < 0].tail(top_n) 
        
        multiplier = self.calculate_regime_multiplier(regime_metrics)
        
        net_exposure = getattr(config, 'NET_EXPOSURE', 0.0)
        
        base_long_ratio = (1.0 + net_exposure) / 2.0
        base_short_ratio = (1.0 - net_exposure) / 2.0
        
        total_long_weight = base_long_ratio * self.leverage_multiplier
        total_short_weight = base_short_ratio * self.leverage_multiplier
        
        final_long_weight = total_long_weight * multiplier
        final_short_weight = total_short_weight * multiplier
        
        weight_per_long = final_long_weight / len(longs) if not longs.empty else 0.0
        weight_per_short = final_short_weight / len(shorts) if not shorts.empty else 0.0
        
        signals = pd.DataFrame(index=residuals.index, columns=['Signal'])
        signals['Signal'] = 0.0
        
        signals.loc[shorts.index, 'Signal'] = -weight_per_short
        signals.loc[longs.index, 'Signal'] = weight_per_long
        
        return signals

if __name__ == "__main__":
    engine = IntegrationEngine()
    
    dates = pd.date_range('2023-01-01', periods=10)
    residuals = pd.Series(np.random.randn(15), index=[f'Ticker_{i}' for i in range(15)])
    
    metrics = {'max_persistence_h1': 0.05} 
    
    signals = engine.generate_signals(residuals, metrics)
    print("Regime Multiplier:", engine.calculate_regime_multiplier(metrics))
    print("Signals:\n", signals[signals['Signal'] != 0])
