import pandas as pd

from src.config import BUSINESS_CONFIG, BusinessConfig


def calculate_indicators(frame: pd.DataFrame, config: BusinessConfig = BUSINESS_CONFIG) -> pd.DataFrame:
    data = frame.copy()
    data["variance_bopd"] = data["production_actual_bopd"] - data["production_plan_bopd"]
    data["variance_pct"] = data["variance_bopd"].div(data["production_plan_bopd"].where(data["production_plan_bopd"] != 0)).mul(100)
    data["efficiency_pct"] = data["production_actual_bopd"].div(data["production_plan_bopd"].where(data["production_plan_bopd"] != 0)).mul(100)
    data["target_met"] = data["efficiency_pct"] >= config.minimum_compliance_pct
    return data


def weekly_indicators(frame: pd.DataFrame) -> pd.DataFrame:
    return (
        frame.groupby("period", as_index=False)
        .agg(
            production_plan_bopd=("production_plan_bopd", lambda values: values.sum(min_count=1)),
            production_actual_bopd=("production_actual_bopd", lambda values: values.sum(min_count=1)),
            plan_observations=("production_plan_bopd", "count"),
            actual_observations=("production_actual_bopd", "count"),
            record_count=("period", "size"),
        )
        .sort_values("period")
    )