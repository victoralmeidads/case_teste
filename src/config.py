from dataclasses import dataclass


@dataclass(frozen=True)
class BusinessConfig:
    minimum_compliance_pct: float = 95.0
    material_deviation_pct: float = -10.0
    significant_drop_pct: float = 15.0
    trend_window_periods: int = 4


BUSINESS_CONFIG = BusinessConfig()