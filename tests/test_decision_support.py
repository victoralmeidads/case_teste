import unittest

import pandas as pd

from src.analytics.decision_support import (
    downtime_associations,
    executive_report,
    executive_snapshot,
    prioritize_assets,
)
from src.business.metrics import calculate_indicators
from src.ingestion.simulated_api import SimulatedEandPApiSource


class DecisionSupportTests(unittest.TestCase):
    def setUp(self):
        self.data = calculate_indicators(SimulatedEandPApiSource().load())

    def test_snapshot_with_partial_actual_coverage_does_not_publish_compliance(self):
        frame = self.data.copy()
        latest_period = frame["period"].max()
        latest_index = frame.index[frame["period"] == latest_period][0]
        frame.loc[latest_index, "production_actual_bopd"] = pd.NA

        snapshot = executive_snapshot(frame)

        self.assertEqual(snapshot["actual_observations"], 4)
        self.assertEqual(snapshot["record_count"], 5)
        self.assertIsNone(snapshot["compliance_pct"])

    def test_priorities_include_data_coverage_and_human_next_step(self):
        result = prioritize_assets(self.data)

        self.assertEqual(len(result), 5)
        self.assertIn("suggested_next_step", result.columns)
        self.assertTrue(result["coverage_pct"].eq(100).all())

    def test_associations_and_export_preserve_limits(self):
        associations = downtime_associations(self.data)
        report = executive_report(self.data, "API simulada E&P", "2026-10-07 10:00", [])

        self.assertEqual(len(associations), 5)
        self.assertIn("Associação não demonstra causalidade.", report)
        self.assertIn("API simulada E&P", report)


if __name__ == "__main__":
    unittest.main()