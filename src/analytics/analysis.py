import pandas as pd

from src.config import BUSINESS_CONFIG, BusinessConfig
from src.business.metrics import weekly_indicators


def asset_performance(frame: pd.DataFrame) -> pd.DataFrame:
    if frame.empty:
        return pd.DataFrame(
            columns=[
                "asset_id", "asset_name", "facility", "production_plan_bopd",
                "production_actual_bopd", "variance_bopd", "variance_pct",
                "efficiency_pct", "downtime_hours", "record_count",
                "plan_observations", "actual_observations",
            ]
        )
    latest_period = frame["period"].max()
    latest = frame.loc[frame["period"] == latest_period]
    performance = (
        latest.groupby(["asset_id", "asset_name", "facility"], as_index=False)
        .agg(
            production_plan_bopd=("production_plan_bopd", lambda values: values.sum(min_count=1)),
            production_actual_bopd=("production_actual_bopd", lambda values: values.sum(min_count=1)),
            downtime_hours=("downtime_hours", lambda values: values.sum(min_count=1)),
            record_count=("period", "size"),
            plan_observations=("production_plan_bopd", "count"),
            actual_observations=("production_actual_bopd", "count"),
        )
    )
    performance["variance_bopd"] = performance["production_actual_bopd"] - performance["production_plan_bopd"]
    nonzero_plan = performance["production_plan_bopd"].where(performance["production_plan_bopd"] != 0)
    performance["variance_pct"] = performance["variance_bopd"].div(nonzero_plan).mul(100)
    performance["efficiency_pct"] = performance["production_actual_bopd"].div(nonzero_plan).mul(100)
    return performance.sort_values("variance_bopd", na_position="last")


def detect_deviations(frame: pd.DataFrame, config: BusinessConfig = BUSINESS_CONFIG) -> pd.DataFrame:
    periods = sorted(frame["period"].dropna().unique())
    if not periods:
        return frame.iloc[0:0].copy()
    latest = asset_performance(frame).copy()
    latest["period"] = periods[-1]
    if len(periods) > 1:
        previous = frame.loc[frame["period"] == periods[-2]].groupby("asset_id", as_index=False).agg(
            production_actual_bopd=("production_actual_bopd", lambda values: values.sum(min_count=1))
        )
        previous = previous.rename(columns={"production_actual_bopd": "previous_actual_bopd"})
        latest = latest.merge(previous, on="asset_id", how="left")
    else:
        latest["previous_actual_bopd"] = pd.NA

    latest["drop_pct"] = (latest["production_actual_bopd"] / latest["previous_actual_bopd"] - 1) * 100
    latest["material_deviation"] = latest["variance_pct"] <= config.material_deviation_pct
    latest["significant_drop"] = latest["drop_pct"] <= -config.significant_drop_pct
    detected = latest["material_deviation"].fillna(False) | latest["significant_drop"].fillna(False)
    return latest.loc[detected].sort_values("variance_bopd", na_position="last")


def production_trend(frame: pd.DataFrame, config: BusinessConfig = BUSINESS_CONFIG) -> dict[str, float | int | str | None]:
    weekly = weekly_indicators(frame)
    window = min(config.trend_window_periods, len(weekly))
    recent = weekly.tail(window)
    complete_actual = recent["actual_observations"].eq(recent["record_count"]).all()
    if window < 2 or not complete_actual:
        return {
            "direction": "inconclusiva",
            "slope_bopd_per_period": None,
            "latest_actual": None if weekly.empty or pd.isna(weekly.iloc[-1]["production_actual_bopd"]) else float(weekly.iloc[-1]["production_actual_bopd"]),
            "latest_plan": None if weekly.empty or pd.isna(weekly.iloc[-1]["production_plan_bopd"]) else float(weekly.iloc[-1]["production_plan_bopd"]),
            "window_periods": window,
        }
    actual = recent["production_actual_bopd"].astype(float)
    slope = float(actual.diff().dropna().mean())
    direction = "recuperacao" if slope > 0 else "queda" if slope < 0 else "estavel"
    return {
        "direction": direction,
        "slope_bopd_per_period": round(slope, 1),
        "latest_actual": float(weekly.iloc[-1]["production_actual_bopd"]),
        "latest_plan": None if pd.isna(weekly.iloc[-1]["production_plan_bopd"]) else float(weekly.iloc[-1]["production_plan_bopd"]),
        "window_periods": window,
    }


def generate_insights(frame: pd.DataFrame, config: BusinessConfig = BUSINESS_CONFIG) -> list[str]:
    performance = asset_performance(frame)
    losses = performance.assign(loss_bopd=(-performance["variance_bopd"]).clip(lower=0))
    total_losses_value = losses["loss_bopd"].sum(min_count=1)
    total_losses = None if pd.isna(total_losses_value) else float(total_losses_value)
    insights: list[str] = []
    if total_losses is None:
        insights.append("Nao ha cobertura valida de plano e realizado suficiente para quantificar perdas no periodo.")
    elif total_losses > 0:
        top_assets = losses.nlargest(2, "loss_bopd")
        share = float(top_assets["loss_bopd"].sum() / total_losses * 100)
        names = " e ".join(top_assets["asset_name"].tolist())
        insights.append(f"{names} concentram {share:.0f}% das perdas frente ao plano na semana mais recente.")

    trend = production_trend(frame, config)
    if trend["direction"] == "recuperacao":
        insights.append("A producao apresenta tendencia de recuperacao nas ultimas semanas; validar se o movimento e sustentavel.")
    elif trend["direction"] == "queda":
        insights.append("A producao apresenta tendencia de queda; priorizar a investigacao das perdas recorrentes.")
    elif trend["direction"] == "estavel":
        insights.append("A producao permaneceu estavel na janela recente; avaliar oportunidades de ganho incremental.")
    else:
        insights.append("A tendencia e inconclusiva: valide a cobertura de producao nas semanas recentes antes de interpretar a direcao.")

    if total_losses is not None and total_losses > 0:
        facility_losses = losses.groupby("facility")["loss_bopd"].sum().sort_values(ascending=False)
        leading_facility = facility_losses.index[0]
        facility_share = float(facility_losses.iloc[0] / total_losses * 100)
        insights.append(f"A instalacao {leading_facility} concentra {facility_share:.0f}% das perdas absolutas do recorte.")

    deviations = detect_deviations(frame, config)
    if not deviations.empty:
        names = ", ".join(deviations["asset_name"].head(3).tolist())
        insights.append(f"{len(deviations)} ativo(s) apresentam desvio material ou queda semanal relevante: {names}.")
    return insights