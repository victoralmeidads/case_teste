ENTITIES = {
    "Ativo": ["asset_id (PK)", "asset_name"],
    "Instalacao": ["facility_id (PK)", "facility_name"],
    "Poco": ["well_id (PK)", "asset_id (FK)", "facility_id (FK)"],
    "Periodo": ["period_id (PK)", "week_start", "week_end"],
    "Meta": ["target_id (PK)", "well_id (FK)", "period_id (FK)", "planned_bopd"],
    "Producao": ["production_id (PK)", "well_id (FK)", "period_id (FK)", "actual_bopd", "downtime_hours"],
    "Indicador": ["metric_id (PK)", "metric_name", "definition", "version"],
}

RELATIONSHIPS = [
    ("Instalacao", "Poco", "1:N"),
    ("Ativo", "Poco", "1:N"),
    ("Poco", "Producao", "1:N"),
    ("Poco", "Meta", "1:N"),
    ("Periodo", "Producao", "1:N"),
    ("Periodo", "Meta", "1:N"),
    ("Producao", "Indicador", "N:1"),
    ("Meta", "Indicador", "N:1"),
]


def generate_mermaid() -> str:
    lines = ["erDiagram"]
    for entity, attributes in ENTITIES.items():
        lines.append(f"    {entity} {{")
        for attribute in attributes:
            if " (" in attribute:
                field_name, key = attribute.split(" (", 1)
                key = key.rstrip(")")
                lines.append(f"        string {field_name} {key}")
            else:
                lines.append(f"        string {attribute}")
        lines.append("    }")
    for left, right, cardinality in RELATIONSHIPS:
        notation = "||--o{" if cardinality == "1:N" else "}o--||"
        lines.append(f"    {left} {notation} {right} : relaciona")
    return "\n".join(lines) + "\n"


def write_semantic_diagram(path) -> str:
    diagram = generate_mermaid()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(diagram, encoding="utf-8")
    return diagram