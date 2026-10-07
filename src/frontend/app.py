from datetime import datetime
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
root_path = str(ROOT)
if root_path not in sys.path:
    sys.path.insert(0, root_path)

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src.analytics.analysis import asset_performance, detect_deviations, generate_insights, production_trend
from src.analytics.decision_support import (
    downtime_associations,
    executive_report,
    executive_snapshot,
    prioritize_assets,
)
from src.analytics.semantic_model import write_semantic_diagram
from src.business.metrics import calculate_indicators, weekly_indicators
from src.config import BUSINESS_CONFIG
from src.governance.audit import read_recent_audits, record_ingestion
from src.governance.catalog import COLUMN_CATALOG, DATASET_METADATA, INDICATOR_CATALOG
from src.ingestion.file_source import UploadedFileSource
from src.ingestion.simulated_api import SimulatedEandPApiSource
from src.transformation.quality import NUMERIC_COLUMNS, QualityIssue, normalize_and_validate


AUDIT_DATABASE = ROOT / "data" / "audit.db"
DIAGRAM_PATH = ROOT / "docs" / "semantic-model.mmd"
COLORS = {"ink": "#152523", "green": "#176B5B", "lime": "#C8D94A", "red": "#C44936", "muted": "#697572", "grid": "#E2E8E4"}

st.set_page_config(page_title="IPNOD | Operações E&P", page_icon="◈", layout="wide")
write_semantic_diagram(DIAGRAM_PATH)

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@500;600;700&family=IBM+Plex+Sans:wght@400;500;600;700&display=swap');
    :root { --ink: #152523; --green: #176B5B; --lime: #C8D94A; --paper: #F4F6F2; --line: #DCE4DF; }
    html, body, [class*="css"] { font-family: 'IBM Plex Sans', sans-serif; color: var(--ink); }
    .stApp { background: var(--paper); }
    h1, h2, h3 { font-family: 'Barlow Condensed', sans-serif !important; letter-spacing: 0 !important; color: var(--ink); }
    h1 { font-size: 2.25rem !important; }
    [data-testid="stMetric"] { background: white; border-top: 3px solid var(--green); padding: 14px 16px; }
    [data-testid="stMetricValue"] { color: var(--ink); }
    [data-testid="stSidebar"] { background: #E8EEEA; }
    .eyebrow { color: var(--green); text-transform: uppercase; font-size: 0.75rem; font-weight: 700; letter-spacing: 1px; }
    .decision-note { border-left: 3px solid var(--lime); padding: 8px 12px; color: #46534F; background: #FFFFFF; font-size: 0.86rem; }
    div[data-testid="stDataFrame"] { border: 1px solid var(--line); }
    </style>
    """,
    unsafe_allow_html=True,
)


def load_data(source_kind: str, uploaded_file) -> None:
    if source_kind == "Arquivo CSV / Excel" and uploaded_file is not None:
        source = UploadedFileSource(uploaded_file.name, uploaded_file.getvalue())
    else:
        source = SimulatedEandPApiSource()
    try:
        raw = source.load()
        quality = normalize_and_validate(raw)
        record_ingestion(AUDIT_DATABASE, source.name, quality.input_rows, quality.accepted_rows, len(quality.issues), "sucesso")
        st.session_state["raw_data"] = raw
        st.session_state["quality_data"] = quality.data
        st.session_state["quality_issues"] = quality.issues
        st.session_state["source_name"] = source.name
        st.session_state["updated_at"] = datetime.now().astimezone()
        st.session_state["load_error"] = None
    except Exception as error:
        record_ingestion(AUDIT_DATABASE, source.name, 0, 0, 1, "erro")
        st.session_state["load_error"] = str(error)


with st.sidebar:
    st.markdown('<p class="eyebrow">IPNOD · E&P</p>', unsafe_allow_html=True)
    st.subheader("Operação analítica")
    source_kind = st.radio("Fonte de dados", ["API simulada", "Arquivo CSV / Excel"], index=0)
    uploaded = None
    if source_kind == "Arquivo CSV / Excel":
        uploaded = st.file_uploader("Extrato operacional", type=["csv", "xlsx", "xls"])
    refresh = st.button("Atualizar dados", type="primary", use_container_width=True)
    if source_kind == "Arquivo CSV / Excel" and uploaded is None:
        st.caption("Sem arquivo selecionado, a demonstração mantém a última carga.")
    st.divider()
    st.caption("Protótipo demonstrativo · dados sintéticos · v1.0.0")

if refresh or "quality_data" not in st.session_state:
    if source_kind == "Arquivo CSV / Excel" and uploaded is None:
        st.warning("Selecione um arquivo antes de atualizar. Os dados sintéticos permanecem disponíveis.")
        if "quality_data" not in st.session_state:
            load_data("API simulada", None)
    else:
        load_data(source_kind, uploaded)

if st.session_state.get("load_error"):
    st.error(f"Falha na ingestao: {st.session_state['load_error']}")
if "quality_data" not in st.session_state:
    st.stop()

data = calculate_indicators(st.session_state["quality_data"])
if data.empty:
    st.error("Nenhum registro passou pela validação estrutural. Revise os alertas da carga e corrija o extrato antes de analisar.")
    quality_issues: list[QualityIssue] = st.session_state.get("quality_issues", [])
    if quality_issues:
        st.dataframe(
            pd.DataFrame(
                [
                    {"Severidade": issue.severity, "Campo": issue.column or "registro", "Código": issue.code, "Detalhe": issue.message, "Registros": issue.affected_rows}
                    for issue in quality_issues
                ]
            ),
            hide_index=True,
            use_container_width=True,
        )
    st.stop()

source_name = st.session_state.get("source_name", "Fonte nao identificada")
updated_at = st.session_state.get("updated_at", datetime.now().astimezone())
updated_label = updated_at.strftime("%d/%m/%Y %H:%M %Z")
period_label = pd.to_datetime(data["period"]).max().strftime("%d/%m/%Y")
performance = asset_performance(data)
weekly = weekly_indicators(data)
snapshot = executive_snapshot(data)
latest_actual = snapshot["actual"]
latest_plan = snapshot["plan"]
actual_value = "Sem dado" if latest_actual is None else f"{latest_actual:,.0f} bopd"
plan_value = "Sem dado" if latest_plan is None else f"{latest_plan:,.0f} bopd"
if snapshot["actual_coverage_pct"] < 100 and latest_actual is not None:
    actual_value = f"Parcial · {actual_value}"
if snapshot["plan_coverage_pct"] < 100 and latest_plan is not None:
    plan_value = f"Parcial · {plan_value}"
compliance_value = "Inconclusivo" if snapshot["compliance_pct"] is None else f"{snapshot['compliance_pct']:.1f}%"
compliance_delta = "Valide cobertura" if snapshot["compliance_pct"] is None else f"{snapshot['compliance_pct'] - 100:+.1f} p.p."
coverage_note = f"Realizado {snapshot['actual_observations']}/{snapshot['record_count']} · Plano {snapshot['plan_observations']}/{snapshot['record_count']} registros"

st.markdown('<p class="eyebrow">Painel executivo · produção e desempenho</p>', unsafe_allow_html=True)
st.title("Da operação à decisão")
st.caption(f"Recorte mais recente: {period_label} · Fonte: {source_name} · Atualizado em {updated_label}")

tab_overview, tab_assistant, tab_assets, tab_analytics, tab_governance = st.tabs(["Visão geral", "Assistente", "Ativos", "Análises", "Governança"])

with tab_overview:
    st.info("Problema: perda de produção frente ao plano. Decisão: priorizar investigação operacional. Responsável: Coordenação de Desempenho Operacional. Fonte e atualização: indicadas no cabeçalho.")
    metric_a, metric_b, metric_c, metric_d = st.columns(4)
    metric_a.metric("Produção realizada", actual_value, f"Plano {plan_value}", help="Soma conhecida do realizado; confira a cobertura antes de interpretar totais parciais.")
    metric_b.metric("Cumprimento do plano", compliance_value, delta=compliance_delta, help=f"Realizado / planejado; referência de meta em {BUSINESS_CONFIG.minimum_compliance_pct:.0f}%. Só é calculado com cobertura integral no período.")
    variance_value = "Inconclusivo" if snapshot["variance"] is None else f"{snapshot['variance']:+,.0f} bopd"
    metric_c.metric("Desvio do plano", variance_value, help="Realizado menos planejado. Exibido apenas com cobertura integral.")
    evaluated_assets = performance["efficiency_pct"].notna()
    below_target = int((performance.loc[evaluated_assets, "efficiency_pct"] < BUSINESS_CONFIG.minimum_compliance_pct).sum())
    metric_d.metric("Ativos abaixo da meta", f"{below_target} / {int(evaluated_assets.sum())} avaliados", help="Ativos avaliados com cobertura válida; os demais não são classificados.")
    st.caption(coverage_note)

    chart = go.Figure()
    chart.add_trace(go.Scatter(x=weekly["period"], y=weekly["production_plan_bopd"], name="Plano", line={"color": COLORS["muted"], "dash": "dot", "width": 2}))
    chart.add_trace(go.Scatter(x=weekly["period"], y=weekly["production_actual_bopd"], name="Realizado", line={"color": COLORS["green"], "width": 3}, fill="tozeroy", fillcolor="rgba(23,107,91,0.08)"))
    chart.update_layout(title="Produção semanal · realizado versus plano", height=370, margin={"t": 48, "b": 8}, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="white", legend={"orientation": "h", "y": 1.12}, xaxis_title=None, yaxis_title="bopd", font={"family": "IBM Plex Sans", "color": COLORS["ink"]}, yaxis={"gridcolor": COLORS["grid"]})
    st.plotly_chart(chart, use_container_width=True)
    st.markdown(f'<p class="decision-note">Decisão apoiada: identificar se a distância ao plano está aumentando. Owner: {DATASET_METADATA["indicator_owner"]} · Fonte: {source_name} · Atualização: {updated_label}.</p>', unsafe_allow_html=True)

    source_frame = st.session_state["quality_data"]
    st.download_button("Baixar extrato canônico CSV", source_frame.to_csv(index=False).encode("utf-8"), "producao_ep_canonica.csv", "text/csv")

with tab_assistant:
    st.info("Assistente determinístico sobre a carga ativa. Não consulta sistemas, documentos ou modelos de linguagem externos.")
    question = st.selectbox(
        "Pergunta de negócio",
        [
            "Panorama do período",
            "Comparar ativos",
            "Rastrear um indicador",
            "Investigar associação com indisponibilidade",
            "Priorizar próximos passos",
        ],
    )
    st.caption(f"Base: {source_name} · período de referência {period_label} · atualizado em {updated_label}")

    if question == "Panorama do período":
        st.subheader("Conclusão principal")
        if snapshot["compliance_pct"] is None:
            st.write("A cobertura de plano e realizado não permite calcular com segurança o cumprimento agregado deste período.")
        else:
            st.write(
                f"O realizado conhecido foi de {latest_actual:,.0f} bopd frente ao plano de {latest_plan:,.0f} bopd "
                f"({snapshot['compliance_pct']:.1f}% de cumprimento)."
            )
        evidence = pd.DataFrame(
            [
                {"Métrica": "Realizado", "Valor conhecido": actual_value, "Cobertura": f"{snapshot['actual_observations']}/{snapshot['record_count']} registros"},
                {"Métrica": "Plano", "Valor conhecido": plan_value, "Cobertura": f"{snapshot['plan_observations']}/{snapshot['record_count']} registros"},
                {"Métrica": "Desvio", "Valor conhecido": variance_value, "Cobertura": "Somente cobertura integral"},
                {"Métrica": "Cumprimento", "Valor conhecido": compliance_value, "Cobertura": "Somente cobertura integral"},
            ]
        )
        st.subheader("Evidências")
        st.dataframe(evidence, hide_index=True, use_container_width=True)
        st.subheader("Interpretação")
        if snapshot["compliance_pct"] is not None and snapshot["compliance_pct"] < BUSINESS_CONFIG.minimum_compliance_pct:
            st.write("O indicador está abaixo do limiar configurado. Isso sinaliza uma revisão operacional; não identifica causa nem comprova que uma ação específica recuperará produção.")
        else:
            st.write("Use o cumprimento e a distribuição por ativo como triagem, não como explicação causal do resultado.")
        st.subheader("Próxima ação")
        st.write("Validar plano, realizado e contexto com Operações e o owner do indicador antes de priorizar uma intervenção.")
        st.subheader("Limitações")
        st.write("Dados demonstrativos; sem criticidade, risco de segurança, custo de intervenção ou confirmação de causa no conjunto disponível.")

    elif question == "Comparar ativos":
        st.subheader("Comparação contextualizada")
        asset_labels = dict(zip(performance["asset_id"], performance["asset_name"]))
        selected_assets = st.multiselect(
            "Ativos para comparar no mesmo período",
            options=performance["asset_id"].tolist(),
            default=performance["asset_id"].head(2).tolist(),
            format_func=lambda asset_id: asset_labels[asset_id],
        )
        if len(selected_assets) < 2:
            st.caption("Selecione pelo menos dois ativos para comparar.")
        else:
            comparison = performance.loc[performance["asset_id"].isin(selected_assets)].copy()
            comparison["coverage_pct"] = comparison[["plan_observations", "actual_observations"]].min(axis=1).div(comparison["record_count"]).mul(100)
            comparison = comparison[["asset_name", "facility", "production_plan_bopd", "production_actual_bopd", "variance_bopd", "variance_pct", "efficiency_pct", "coverage_pct"]]
            comparison = comparison.rename(columns={"asset_name": "Ativo", "facility": "Instalação", "production_plan_bopd": "Plano (bopd)", "production_actual_bopd": "Realizado (bopd)", "variance_bopd": "Desvio (bopd)", "variance_pct": "Desvio (%)", "efficiency_pct": "Cumprimento (%)", "coverage_pct": "Cobertura (%)"})
            st.dataframe(comparison, hide_index=True, use_container_width=True)
        st.markdown("**Interpretação:** compare valores do mesmo período e unidade. Desvio absoluto prioriza volume; percentual contextualiza a escala do ativo. A comparação não explica causalidade.")
        st.write("**Próxima ação:** validar os maiores desvios com Engenharia e Operações, considerando criticidade e janela operacional que não estão nesta base.")

    elif question == "Rastrear um indicador":
        indicator = st.selectbox("Indicador", INDICATOR_CATALOG, format_func=lambda item: item["name"])
        name = indicator["name"]
        trend = production_trend(data)
        if name == "Producao realizada":
            value = actual_value
            formula = "Soma do realizado no período; resultado parcial quando a cobertura é inferior a 100%."
        elif name == "Desvio de producao":
            value = variance_value
            formula = "Realizado menos planejado; publicado somente quando plano e realizado cobrem todos os registros."
        elif name == "Cumprimento de meta":
            value = compliance_value
            formula = f"Soma do realizado / soma do plano × 100; limiar configurado em {BUSINESS_CONFIG.minimum_compliance_pct:.0f}%."
        else:
            value = "Inconclusiva" if trend["slope_bopd_per_period"] is None else f"{trend['direction']} · {trend['slope_bopd_per_period']:+,.0f} bopd/semana"
            formula = f"Média das variações semanais nas últimas {BUSINESS_CONFIG.trend_window_periods} observações completas."
        st.markdown(f"**Valor no período:** {value}")
        st.markdown(f"**Definição:** {indicator['definition']}")
        st.markdown(f"**Fórmula aplicada:** {formula}")
        st.markdown(f"**Owner:** {indicator['owner']} · **Versão:** {indicator['version']} · **Fonte:** {source_name} · **Período:** {period_label}")
        st.write("**Limite de interpretação:** confirme a definição com o owner antes de tratar o indicador como oficial.")

    elif question == "Investigar associação com indisponibilidade":
        st.subheader("Perda versus horas de indisponibilidade")
        associations = downtime_associations(data)
        associations = associations.rename(columns={"asset_name": "Ativo", "weekly_samples": "Semanas completas", "correlation_loss_downtime": "Correlação de Pearson"})
        st.dataframe(associations.drop(columns=["asset_id"]), hide_index=True, use_container_width=True)
        st.write("**Interpretação:** a correlação é uma associação exploratória por ativo entre perda frente ao plano e horas indisponíveis nas semanas completas; amostras abaixo de quatro semanas ou sem variação suficiente não recebem coeficiente.")
        st.write("**Limitações:** associação não demonstra causalidade; tendência temporal, eventos operacionais e outros fatores não foram controlados. As horas são a única variável de direcionador disponível nesta carga.")
        st.write("**Próxima ação:** validar eventos e causas com Operações antes de propor intervenção ou estimar recuperação.")

    else:
        st.subheader("Fila de investigação, sem score opaco")
        priorities = prioritize_assets(data).rename(columns={"asset_name": "Ativo", "facility": "Instalação", "latest_loss_bopd": "Perda recente (bopd)", "consecutive_weeks_below_target": "Semanas consecutivas abaixo da meta", "coverage_pct": "Cobertura (%)", "suggested_next_step": "Próxima ação sugerida"})
        st.dataframe(priorities, hide_index=True, use_container_width=True)
        st.write("**Critério:** perda conhecida no período mais recente, persistência abaixo do limiar e cobertura dos dados. Cobertura incompleta leva à validação do dado antes da priorização.")
        st.write("**Limitação decisória:** segurança, integridade, criticidade, custo e viabilidade da intervenção não estão disponíveis; esta fila não substitui a priorização operacional.")
        st.write("**Próxima ação:** atribuir owner e prazo após validação conjunta com Operações e Engenharia.")

    report = executive_report(data, source_name, updated_label, generate_insights(data))
    st.download_button("Exportar resumo executivo Markdown", report, "resumo_executivo_ep.md", "text/markdown")

with tab_assets:
    st.info("Problema: dispersão de desempenho entre ativos. Decisão: direcionar análise de causa e capacidade para os maiores desvios. Responsável: Engenharia de Produção. Fonte e atualização: indicadas no cabeçalho.")
    rank = performance.sort_values("variance_bopd")
    bar = go.Figure()
    bar.add_trace(go.Bar(y=rank["asset_name"], x=rank["production_plan_bopd"], name="Plano", orientation="h", marker_color="#AAB5B0"))
    bar.add_trace(go.Bar(y=rank["asset_name"], x=rank["production_actual_bopd"], name="Realizado", orientation="h", marker_color=COLORS["green"]))
    bar.update_layout(title="Ranking de ativos · semana mais recente", barmode="group", height=340, margin={"t": 48, "b": 8}, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="white", xaxis_title="bopd", yaxis_title=None, font={"family": "IBM Plex Sans", "color": COLORS["ink"]}, xaxis={"gridcolor": COLORS["grid"]}, legend={"orientation": "h", "y": 1.12})
    st.plotly_chart(bar, use_container_width=True)
    st.markdown(f'<p class="decision-note">Decisão apoiada: priorizar os ativos com maior perda absoluta, sem confundir volume com percentual. Owner: Engenharia de Produção · Fonte: {source_name} · Atualização: {updated_label}.</p>', unsafe_allow_html=True)
    display_performance = performance[["asset_name", "facility", "production_plan_bopd", "production_actual_bopd", "variance_bopd", "variance_pct", "efficiency_pct", "downtime_hours"]].rename(columns={"asset_name": "Ativo", "facility": "Instalacao", "production_plan_bopd": "Plano (bopd)", "production_actual_bopd": "Realizado (bopd)", "variance_bopd": "Desvio (bopd)", "variance_pct": "Desvio (%)", "efficiency_pct": "Cumprimento (%)", "downtime_hours": "Indisponibilidade (h)"})
    st.dataframe(display_performance, hide_index=True, use_container_width=True)

with tab_analytics:
    st.info("Problema: sinais relevantes se perdem na leitura manual. Decisão: investigar causas antes de redirecionar recursos. Responsável: Analytics de Operações com validação do owner operacional. Fonte e atualização: indicadas no cabeçalho.")
    left, right = st.columns([1.1, 0.9])
    with left:
        st.subheader("Insights automáticos")
        for insight in generate_insights(data):
            st.markdown(f"- {insight}")
        st.caption("Insights são sinais de triagem; não substituem validação da operação.")
    with right:
        trend = production_trend(data)
        trend_delta = "Cobertura insuficiente" if trend["slope_bopd_per_period"] is None else f"{trend['slope_bopd_per_period']:+,.0f} bopd/semana"
        st.metric("Tendência recente", trend["direction"].capitalize(), trend_delta)
        st.caption("Método: média da variação semanal nas quatro observações mais recentes.")

    anomalies = detect_deviations(data)
    st.subheader("Desvios e quedas relevantes")
    if anomalies.empty:
        st.success("Nenhum desvio material identificado no período mais recente.")
    else:
        anomaly_view = anomalies[["period", "asset_name", "facility", "variance_bopd", "variance_pct", "drop_pct", "material_deviation", "significant_drop"]].rename(columns={"period": "Periodo", "asset_name": "Ativo", "facility": "Instalacao", "variance_bopd": "Desvio (bopd)", "variance_pct": "Desvio (%)", "drop_pct": "Queda semanal (%)", "material_deviation": "Desvio material", "significant_drop": "Queda relevante"})
        st.dataframe(anomaly_view, hide_index=True, use_container_width=True)
    st.markdown(f'<p class="decision-note">Decisão apoiada: validar desvio material (≤ {BUSINESS_CONFIG.material_deviation_pct:.0f}%) ou queda semanal (≤ -{BUSINESS_CONFIG.significant_drop_pct:.0f}%). Owner: Analytics de Operações · Fonte: {source_name} · Atualização: {updated_label}.</p>', unsafe_allow_html=True)

    weekly["compliance_pct"] = weekly["production_actual_bopd"] / weekly["production_plan_bopd"].replace(0, pd.NA) * 100
    trend_chart = px.line(weekly, x="period", y="compliance_pct", markers=True, title="Cumprimento do plano · tendência semanal")
    trend_chart.add_hline(y=BUSINESS_CONFIG.minimum_compliance_pct, line_dash="dash", line_color=COLORS["red"], annotation_text=f"Meta {BUSINESS_CONFIG.minimum_compliance_pct:.0f}%")
    trend_chart.update_layout(height=320, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="white", margin={"t": 48, "b": 8}, xaxis_title=None, yaxis_title="%", font={"family": "IBM Plex Sans", "color": COLORS["ink"]}, yaxis={"gridcolor": COLORS["grid"]})
    st.plotly_chart(trend_chart, use_container_width=True)
    st.markdown(f'<p class="decision-note">Decisão apoiada: avaliar persistência de não cumprimento da meta. Owner: Gerência de Operações de E&P · Fonte: {source_name} · Atualização: {updated_label}.</p>', unsafe_allow_html=True)

with tab_governance:
    quality_data = st.session_state["quality_data"]
    quality_issues: list[QualityIssue] = st.session_state.get("quality_issues", [])
    input_rows = max(len(st.session_state.get("raw_data", quality_data)), 1)
    accepted_pct = len(quality_data) / input_rows * 100
    st.info("Problema: decisão sem linhagem ou ownership claro reduz confiança. Decisão: usar indicadores publicados com origem, regra e responsável visíveis. Responsável: Data Owner de Operações. Fonte e atualização: indicadas no cabeçalho.")
    q1, q2, q3, q4 = st.columns(4)
    q1.metric("Completude estrutural", f"{accepted_pct:.1f}%", help="Registros aceitos após validar dimensões e período obrigatórios.")
    q2.metric("Registros aceitos", f"{len(quality_data):,}")
    q3.metric("Registros rejeitados", f"{input_rows - len(quality_data):,}")
    q4.metric("Alertas de qualidade", f"{len(quality_issues)}")

    st.subheader("Cobertura numérica por campo")
    numeric_coverage = pd.DataFrame(
        [
            {
                "Campo": column,
                "Observações disponíveis": int(quality_data[column].notna().sum()),
                "Ausentes após normalização": int(quality_data[column].isna().sum()),
                "Cobertura (%)": quality_data[column].notna().mean() * 100 if len(quality_data) else 0.0,
            }
            for column in NUMERIC_COLUMNS
        ]
    )
    st.dataframe(numeric_coverage, hide_index=True, use_container_width=True)
    st.caption("Zero explícito é uma observação válida. Nulo, N/A, estimativa sem metadados e valor inválido permanecem distintos nos alertas da carga.")

    st.subheader("Catálogo e dicionário de dados")
    catalog_rows = [{"Campo": name, "Tipo": field_type, "Definicao": definition, "Fonte de referencia": source, "Data Owner": DATASET_METADATA["data_owner"], "Versao": DATASET_METADATA["version"]} for name, field_type, definition, source in COLUMN_CATALOG]
    st.dataframe(pd.DataFrame(catalog_rows), hide_index=True, use_container_width=True)
    st.subheader("Indicadores governados")
    st.dataframe(pd.DataFrame(INDICATOR_CATALOG), hide_index=True, use_container_width=True)

    if quality_issues:
        st.subheader("Ocorrencias da validacao")
        issue_rows = [{"Severidade": issue.severity, "Campo": issue.column or "registro", "Codigo": issue.code, "Detalhe": issue.message, "Registros": issue.affected_rows} for issue in quality_issues]
        st.dataframe(pd.DataFrame(issue_rows), hide_index=True, use_container_width=True)
    else:
        st.success("Nenhuma ocorrência de qualidade identificada nesta carga.")

    st.subheader("Modelo semantico")
    st.caption("Entidades e relacionamentos são gerados a partir do contrato em src/analytics/semantic_model.py.")
    st.code(DIAGRAM_PATH.read_text(encoding="utf-8"), language="mermaid")
    st.download_button("Baixar diagrama Mermaid", DIAGRAM_PATH.read_bytes(), "semantic-model.mmd", "text/plain")

    st.subheader("Auditoria de cargas")
    audit_rows = read_recent_audits(AUDIT_DATABASE)
    if audit_rows:
        st.dataframe(pd.DataFrame(audit_rows), hide_index=True, use_container_width=True)
    else:
        st.caption("Ainda não há cargas registradas.")