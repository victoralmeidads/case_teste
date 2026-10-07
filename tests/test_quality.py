import unittest

import pandas as pd

from src.transformation.quality import normalize_and_validate


class QualityValidationTests(unittest.TestCase):
    def test_preserves_zero_missing_not_applicable_and_invalid_numeric_values(self):
        source = pd.DataFrame(
            {
                " PERIOD ": ["2026-01-05"] * 5,
                "asset_id": [" A01 ", "A02", "A03", "A04", "A05"],
                "asset_name": [" Ativo 1 ", "Ativo 2", "Ativo 3", "Ativo 4", "Ativo 5"],
                "facility": ["FPSO X"] * 5,
                "well_id": ["P-1", "P-2", "P-3", "P-4", "P-5"],
                "production_plan_bopd": [100, 120, 130, 140, 150],
                "production_actual_bopd": [None, 0, "N/A", "estimado", "valor invalido"],
                "downtime_hours": [2, 3, 4, 5, 6],
            }
        )

        result = normalize_and_validate(source)

        self.assertEqual(result.input_rows, 5)
        self.assertEqual(result.accepted_rows, 5)
        self.assertEqual(result.rejected_rows, 0)
        self.assertEqual(result.data.loc[0, "asset_id"], "A01")
        self.assertTrue(pd.isna(result.data.loc[0, "production_actual_bopd"]))
        self.assertEqual(result.data.loc[1, "production_actual_bopd"], 0)
        self.assertTrue(pd.isna(result.data.loc[2, "production_actual_bopd"]))
        self.assertTrue(pd.isna(result.data.loc[3, "production_actual_bopd"]))
        self.assertTrue(pd.isna(result.data.loc[4, "production_actual_bopd"]))
        self.assertEqual(
            {issue.code for issue in result.issues},
            {"NUMERIC_MISSING", "NUMERIC_NOT_APPLICABLE", "NUMERIC_ESTIMATE_UNSUPPORTED", "NUMERIC_INVALID"},
        )
        self.assertTrue(all(issue.column == "production_actual_bopd" for issue in result.issues))

    def test_missing_schema_column_fails_fast(self):
        with self.assertRaisesRegex(ValueError, "Colunas obrigatorias ausentes"):
            normalize_and_validate(pd.DataFrame({"asset_id": ["A01"]}))


if __name__ == "__main__":
    unittest.main()