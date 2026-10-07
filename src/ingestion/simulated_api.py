from datetime import date, timedelta

import pandas as pd


class SimulatedEandPApiSource:
    """Deterministic operational extract representing a simulated E&P API."""

    ASSETS = (
        ("A-101", "Marlim Sul", "FPSO Atlantico Sul", 12600, 0.97, 0.010),
        ("A-202", "Jubarte", "FPSO Capixaba", 9800, 0.78, -0.025),
        ("A-303", "Buzios", "FPSO Almirante Barroso", 15400, 0.91, 0.012),
        ("A-404", "Marlim Leste", "FPSO P-54", 8200, 0.91, -0.004),
        ("A-505", "Roncador", "FPSO P-52", 10500, 0.94, 0.002),
    )

    @property
    def name(self) -> str:
        return "API simulada E&P"

    def load(self) -> pd.DataFrame:
        today = date.today()
        latest_monday = today - timedelta(days=today.weekday())
        rows = []
        for week_index in range(12):
            period = latest_monday - timedelta(weeks=11 - week_index)
            for asset_index, (asset_id, asset_name, facility, plan, start_ratio, slope) in enumerate(self.ASSETS):
                ratio = start_ratio + (week_index - 5) * slope
                if asset_id == "A-404" and week_index == 10:
                    ratio -= 0.24
                if asset_id == "A-202" and week_index in (8, 9, 10, 11):
                    ratio -= 0.04
                ratio += ((week_index * 7 + asset_index * 3) % 5 - 2) * 0.008
                actual = round(plan * ratio)
                rows.append(
                    {
                        "period": period.isoformat(),
                        "asset_id": asset_id,
                        "asset_name": asset_name,
                        "facility": facility,
                        "well_id": f"{asset_id}-P01",
                        "production_plan_bopd": plan,
                        "production_actual_bopd": actual,
                        "downtime_hours": round(max(0, (1 - ratio) * 168), 1),
                    }
                )
        return pd.DataFrame(rows)