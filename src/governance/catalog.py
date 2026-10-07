from datetime import datetime


DATASET_METADATA = {
    "name": "Producao semanal de E&P",
    "description": "Extrato demonstrativo de producao planejada, realizada e indisponibilidade por poco.",
    "data_owner": "Gerencia de Operacoes de E&P",
    "indicator_owner": "Coordenacao de Desempenho Operacional",
    "version": "1.0.0",
    "refresh_policy": "Semanal; demonstracao atualizada sob demanda",
}

COLUMN_CATALOG = [
    ("period", "date", "Semana de referencia operacional", "Sistema operacional E&P"),
    ("asset_id", "string", "Identificador corporativo do ativo", "Cadastro de ativos"),
    ("asset_name", "string", "Nome legivel do ativo", "Cadastro de ativos"),
    ("facility", "string", "Instalacao responsavel pela producao", "Cadastro de instalacoes"),
    ("well_id", "string", "Identificador do poco produtor", "Cadastro de pocos"),
    ("production_plan_bopd", "decimal", "Producao planejada em barris por dia", "Plano operacional"),
    ("production_actual_bopd", "decimal", "Producao realizada em barris por dia", "Medicao de producao"),
    ("downtime_hours", "decimal", "Horas de indisponibilidade no periodo", "Sistema de operacao"),
]

INDICATOR_CATALOG = [
    {"name": "Producao realizada", "definition": "Soma da producao realizada no periodo, em bopd.", "owner": "Coordenacao de Desempenho Operacional", "version": "1.0.0"},
    {"name": "Desvio de producao", "definition": "Producao realizada menos producao planejada, em bopd e percentual.", "owner": "Engenharia de Producao", "version": "1.0.0"},
    {"name": "Cumprimento de meta", "definition": "Realizado / planejado; meta cumprida quando atinge 95%.", "owner": "Gerencia de Operacoes de E&P", "version": "1.0.0"},
    {"name": "Tendencia", "definition": "Media da variacao semanal da producao realizada nas quatro semanas mais recentes.", "owner": "Analytics de Operacoes", "version": "1.0.0"},
]


def catalog_snapshot(updated_at: datetime) -> dict:
    return {**DATASET_METADATA, "updated_at": updated_at.isoformat(timespec="minutes")}