import pandas as pd
import numpy as np
from typing import Dict
from core import config

class IntegrationEngine:
    def __init__(self):
        self.stop_loss_pct = config.STOP_LOSS_PCT
        self.max_drawdown_limit = config.MAX_DRAWDOWN_LIMIT
        self.leverage_multiplier = config.LEVERAGE_MULTIPLIER

    def calculate_regime_multiplier(self, topological_metrics: Dict[str, float]) -> float:
        """
        Scale position size down when H1 persistence is low (unstable regime).
        """
        persistence = topological_metrics.get('max_persistence_h1', 0.0)
        return 0.5 if persistence < 0.1 else 1.0

    def generate_signals(self, residuals: pd.Series, regime_metrics: Dict[str, float]) -> pd.DataFrame:
        """
        Combine spatial residuals with regime stability to produce long/short signals.
        """
        z_scores = (residuals - residuals.mean()) / residuals.std()

        significant = z_scores[abs(z_scores) > 0.5]
        if significant.empty:
            significant = z_scores

        sorted_z = significant.sort_values(ascending=False)
        top_n = 10
        longs = sorted_z[sorted_z > 0].head(top_n)
        shorts = sorted_z[sorted_z < 0].tail(top_n)

        multiplier = self.calculate_regime_multiplier(regime_metrics)
        net_exposure = config.NET_EXPOSURE

        long_weight = ((1.0 + net_exposure) / 2.0) * self.leverage_multiplier * multiplier
        short_weight = ((1.0 - net_exposure) / 2.0) * self.leverage_multiplier * multiplier

        weight_per_long = long_weight / len(longs) if not longs.empty else 0.0
        weight_per_short = short_weight / len(shorts) if not shorts.empty else 0.0

        signals = pd.DataFrame(0.0, index=residuals.index, columns=['Signal'])
        signals.loc[longs.index, 'Signal'] = weight_per_long
        signals.loc[shorts.index, 'Signal'] = -weight_per_short

        return signals
