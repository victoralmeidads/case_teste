from dataclasses import dataclass

import pandas as pd


REQUIRED_COLUMNS = (
    "period",
    "asset_id",
    "asset_name",
    "facility",
    "well_id",
    "production_plan_bopd",
    "production_actual_bopd",
    "downtime_hours",
)
NUMERIC_COLUMNS = (
    "production_plan_bopd",
    "production_actual_bopd",
    "downtime_hours",
)
TEXT_COLUMNS = ("asset_id", "asset_name", "facility", "well_id")


@dataclass(frozen=True)
class QualityIssue:
    severity: str
    code: str
    message: str
    affected_rows: int = 0
    column: str | None = None


@dataclass
class QualityResult:
    data: pd.DataFrame
    issues: list[QualityIssue]
    input_rows: int
    accepted_rows: int

    @property
    def rejected_rows(self) -> int:
        return self.input_rows - self.accepted_rows


def normalize_and_validate(frame: pd.DataFrame) -> QualityResult:
    """Normalize an operational extract to the canonical production schema."""
    data = frame.copy()
    data.columns = [str(column).strip().lower() for column in data.columns]
    missing = sorted(set(REQUIRED_COLUMNS) - set(data.columns))
    if missing:
        raise ValueError(f"Colunas obrigatorias ausentes: {', '.join(missing)}")

    input_rows = len(data)
    issues: list[QualityIssue] = []
    for column in TEXT_COLUMNS:
        data[column] = data[column].astype("string").str.strip()
        data[column] = data[column].replace("", pd.NA)

    data["period"] = pd.to_datetime(data["period"], errors="coerce")
    invalid_period = data["period"].isna()
    if invalid_period.any():
        issues.append(QualityIssue("error", "INVALID_PERIOD", "Periodo ausente ou invalido; registro descartado.", int(invalid_period.sum())))

    missing_dimensions = data[list(TEXT_COLUMNS)].isna().any(axis=1)
    if missing_dimensions.any():
        issues.append(QualityIssue("error", "MISSING_DIMENSION", "Identificador ou dimensao obrigatoria ausente; registro descartado.", int(missing_dimensions.sum())))

    for column in NUMERIC_COLUMNS:
        original = data[column]
        text = original.astype("string").str.strip()
        missing = original.isna() | text.eq("").fillna(False)
        not_applicable = text.str.lower().isin(
            {"n/a", "na", "n.a.", "not applicable", "not_applicable", "não aplicável", "nao aplicavel"}
        ).fillna(False)
        not_applicable &= ~missing
        estimated = text.str.match(r"^(estimado|estimativa|estimated|est\.)", case=False, na=False)
        parsed = pd.to_numeric(original.mask(missing | not_applicable | estimated), errors="coerce")
        invalid = parsed.isna() & ~missing & ~not_applicable & ~estimated

        for mask, code, message in (
            (missing, "NUMERIC_MISSING", f"{column}: valor ausente preservado como nulo."),
            (not_applicable, "NUMERIC_NOT_APPLICABLE", f"{column}: valor nao aplicavel preservado como nulo."),
            (estimated, "NUMERIC_ESTIMATE_UNSUPPORTED", f"{column}: estimativa sem metadado numerico preservada como nula."),
            (invalid, "NUMERIC_INVALID", f"{column}: valor invalido preservado como nulo."),
        ):
            if mask.any():
                issues.append(QualityIssue("warning", code, message, int(mask.sum()), column))
        data[column] = parsed.astype("Float64")

    rejected = invalid_period | missing_dimensions
    data = data.loc[~rejected, list(REQUIRED_COLUMNS)].reset_index(drop=True)
    negative_values = (data[list(NUMERIC_COLUMNS)] < 0).any(axis=1)
    if negative_values.any():
        issues.append(QualityIssue("warning", "NEGATIVE_VALUE", "Valores negativos identificados para revisao de negocio.", int(negative_values.sum())))

    return QualityResult(data, issues, input_rows, len(data))