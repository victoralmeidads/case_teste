import pandas as pd

from src.analytics.analysis import asset_performance
from src.business.metrics import weekly_indicators
from src.config import BUSINESS_CONFIG


def executive_snapshot(frame: pd.DataFrame) -> dict:
    weekly = weekly_indicators(frame)
    if weekly.empty:
        return {"period": None, "record_count": 0, "actual": None, "plan": None, "variance": None, "compliance_pct": None}

    latest = weekly.iloc[-1]
    record_count = int(latest["record_count"])
    actual_count = int(latest["actual_observations"])
    plan_count = int(latest["plan_observations"])
    actual = None if pd.isna(latest["production_actual_bopd"]) else float(latest["production_actual_bopd"])
    plan = None if pd.isna(latest["production_plan_bopd"]) else float(latest["production_plan_bopd"])
    complete = actual_count == record_count and plan_count == record_count
    variance = actual - plan if complete and actual is not None and plan is not None else None
    compliance = actual / plan * 100 if complete and actual is not None and plan not in (None, 0) else None

    return {
        "period": latest["period"],
        "record_count": record_count,
        "actual": actual,
        "plan": plan,
        "variance": variance,
        "compliance_pct": compliance,
        "actual_observations": actual_count,
        "plan_observations": plan_count,
        "actual_coverage_pct": actual_count / record_count * 100 if record_count else 0.0,
        "plan_coverage_pct": plan_count / record_count * 100 if record_count else 0.0,
    }


def downtime_associations(frame: pd.DataFrame) -> pd.DataFrame:
    columns = ["asset_id", "asset_name", "weekly_samples", "correlation_loss_downtime"]
    if frame.empty:
        return pd.DataFrame(columns=columns)

    weekly = (
        frame.groupby(["asset_id", "asset_name", "period"], as_index=False)
        .agg(
            plan=("production_plan_bopd", lambda values: values.sum(min_count=1)),
            actual=("production_actual_bopd", lambda values: values.sum(min_count=1)),
            downtime=("downtime_hours", lambda values: values.sum(min_count=1)),
            record_count=("period", "size"),
            plan_count=("production_plan_bopd", "count"),
            actual_count=("production_actual_bopd", "count"),
            downtime_count=("downtime_hours", "count"),
        )
    )
    weekly["loss_bopd"] = weekly["plan"] - weekly["actual"]
    rows = []
    for (asset_id, asset_name), asset_weeks in weekly.groupby(["asset_id", "asset_name"]):
        complete = asset_weeks.loc[
            asset_weeks["plan_count"].eq(asset_weeks["record_count"])
            & asset_weeks["actual_count"].eq(asset_weeks["record_count"])
            & asset_weeks["downtime_count"].eq(asset_weeks["record_count"])
        ].dropna(subset=["loss_bopd", "downtime"])
        correlation = None
        if len(complete) >= 4 and complete["loss_bopd"].nunique() > 1 and complete["downtime"].nunique() > 1:
            correlation = float(complete["loss_bopd"].corr(complete["downtime"]))
        rows.append(
            {
                "asset_id": asset_id,
                "asset_name": asset_name,
                "weekly_samples": len(complete),
                "correlation_loss_downtime": correlation,
            }
        )
    return pd.DataFrame(rows, columns=columns).sort_values("asset_name").reset_index(drop=True)


def prioritize_assets(frame: pd.DataFrame) -> pd.DataFrame:
    columns = [
        "asset_name", "facility", "latest_loss_bopd", "consecutive_weeks_below_target",
        "coverage_pct", "suggested_next_step",
    ]
    if frame.empty:
        return pd.DataFrame(columns=columns)

    performance = asset_performance(frame)
    periods = sorted(frame["period"].dropna().unique())[-BUSINESS_CONFIG.trend_window_periods :]
    rows = []
    for _, asset in performance.iterrows():
        asset_data = frame.loc[frame["asset_id"] == asset["asset_id"]]
        recent = asset_data.loc[asset_data["period"].isin(periods)]
        by_period = (
            recent.groupby("period")
            .agg(
                plan=("production_plan_bopd", lambda values: values.sum(min_count=1)),
                actual=("production_actual_bopd", lambda values: values.sum(min_count=1)),
                record_count=("period", "size"),
                plan_count=("production_plan_bopd", "count"),
                actual_count=("production_actual_bopd", "count"),
            )
            .sort_index(ascending=False)
        )
        consecutive = 0
        for _, observation in by_period.iterrows():
            is_complete = (
                observation["record_count"] == observation["plan_count"]
                and observation["record_count"] == observation["actual_count"]
                and pd.notna(observation["plan"])
                and observation["plan"] > 0
                and pd.notna(observation["actual"])
            )
            if not is_complete:
                break
            compliance = observation["actual"] / observation["plan"] * 100
            if compliance < BUSINESS_CONFIG.minimum_compliance_pct:
                consecutive += 1
            else:
                break

        latest_is_complete = (
            asset["record_count"] == asset["plan_observations"]
            and asset["record_count"] == asset["actual_observations"]
            and pd.notna(asset["variance_bopd"])
        )
        coverage = min(asset["plan_observations"], asset["actual_observations"]) / asset["record_count"] * 100
        loss = max(0.0, -float(asset["variance_bopd"])) if latest_is_complete else None
        if not latest_is_complete:
            next_step = "Validar cobertura antes de priorizar"
        elif loss and consecutive >= 2:
            next_step = "Investigar perda recorrente com Operações"
        elif loss:
            next_step = "Investigar desvio recente com Engenharia"
        else:
            next_step = "Monitorar e confirmar estabilidade"
        rows.append(
            {
                "asset_name": asset["asset_name"],
                "facility": asset["facility"],
                "latest_loss_bopd": loss,
                "consecutive_weeks_below_target": consecutive,
                "coverage_pct": coverage,
                "suggested_next_step": next_step,
            }
        )
    return pd.DataFrame(rows, columns=columns).sort_values(
        "latest_loss_bopd", ascending=False, na_position="last"
    ).reset_index(drop=True)


def executive_report(
    frame: pd.DataFrame,
    source: str,
    updated_at: str,
    insights: list[str],
) -> str:
    snapshot = executive_snapshot(frame)
    if snapshot["period"] is None:
        return "# Resumo executivo\n\nSem registros válidos para análise.\n"

    period = pd.Timestamp(snapshot["period"]).strftime("%d/%m/%Y")
    actual = "indisponível" if snapshot["actual"] is None else f"{snapshot['actual']:,.0f} bopd"
    plan = "indisponível" if snapshot["plan"] is None else f"{snapshot['plan']:,.0f} bopd"
    compliance = "inconclusivo por cobertura" if snapshot["compliance_pct"] is None else f"{snapshot['compliance_pct']:.1f}%"
    insight_lines = "\n".join(f"- {insight}" for insight in insights) or "- Sem insight sustentado pela cobertura disponível."
    return (
        "# Resumo executivo | Produção E&P\n\n"
        f"- Período: {period}\n- Fonte: {source}\n- Atualização: {updated_at}\n"
        f"- Realizado conhecido: {actual} ({snapshot['actual_observations']}/{snapshot['record_count']} registros)\n"
        f"- Plano conhecido: {plan} ({snapshot['plan_observations']}/{snapshot['record_count']} registros)\n"
        f"- Cumprimento: {compliance}\n\n"
        "## Sinais para validação humana\n\n"
        f"{insight_lines}\n\n"
        "## Limitações\n\n"
        "- Dados e API são demonstrativos; não representam operação real.\n"
        "- Associação não demonstra causalidade.\n"
        "- Risco de segurança, custo da intervenção e criticidade operacional não estão neste conjunto.\n"
        "- Valores ausentes, não aplicáveis e inválidos permanecem sem valor numérico; zero é preservado como dado.\n"
    )