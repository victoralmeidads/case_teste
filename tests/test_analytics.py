import unittest

import pandas as pd

from src.analytics.analysis import asset_performance, detect_deviations, generate_insights, production_trend
from src.business.metrics import calculate_indicators
from src.ingestion.simulated_api import SimulatedEandPApiSource
from src.transformation.quality import normalize_and_validate


class AnalyticsTests(unittest.TestCase):
    def test_business_indicators_are_consistent(self):
        source = pd.DataFrame(
            {
                "period": ["2026-01-05"],
                "asset_id": ["A-1"],
                "asset_name": ["Ativo 1"],
                "facility": ["Instalacao 1"],
                "well_id": ["P-1"],
                "production_plan_bopd": [100],
                "production_actual_bopd": [90],
                "downtime_hours": [4],
            }
        )

        result = calculate_indicators(source)

        self.assertEqual(result.loc[0, "variance_bopd"], -10)
        self.assertEqual(result.loc[0, "variance_pct"], -10)
        self.assertFalse(result.loc[0, "target_met"])

    def test_simulated_data_drives_rank_deviation_trend_and_insights(self):
        frame = calculate_indicators(SimulatedEandPApiSource().load())

        self.assertEqual(len(asset_performance(frame)), 5)
        deviations = detect_deviations(frame)
        self.assertFalse(deviations.empty)
        self.assertTrue(deviations["period"].eq(frame["period"].max()).all())
        self.assertIn(production_trend(frame)["direction"], {"recuperacao", "queda", "estavel"})
        self.assertGreaterEqual(len(generate_insights(frame)), 2)

    def test_incomplete_recent_period_makes_trend_inconclusive(self):
        frame = normalize_and_validate(SimulatedEandPApiSource().load()).data
        latest_index = frame.index[frame["period"] == frame["period"].max()][0]
        frame.loc[latest_index, "production_actual_bopd"] = pd.NA
        frame = calculate_indicators(frame)

        trend = production_trend(frame)
        insights = generate_insights(frame)

        self.assertEqual(trend["direction"], "inconclusiva")
        self.assertIsNone(trend["slope_bopd_per_period"])
        self.assertTrue(any("inconclusiva" in insight for insight in insights))


if __name__ == "__main__":
    unittest.main()