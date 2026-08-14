from pydantic import BaseModel, Field


class AnomalyRecord(BaseModel):
    centre: str

    district: str

    procured_qty_mt: float

    lifted_qty_mt: float

    pending_qty_mt: float

    pending_lift_pct: float

    statistical_anomaly: bool

    ml_anomaly: bool

    hybrid_anomaly: bool

    isolation_score: float

    risk_level: str

    reasons: list[str]


class HybridAnalyticsResponse(BaseModel):
    method: str

    total_centres: int

    statistical_flagged: int

    ml_flagged: int

    hybrid_flagged: int

    mean_pending_lift_pct: float

    sigma: float

    threshold_pct: float

    returned_results: int

    disclaimer: str

    anomalies: list[
        AnomalyRecord
    ]


class AnalyticsSummaryResponse(BaseModel):
    total_centres: int = Field(
        description=(
            "Total procurement centres analysed."
        )
    )

    statistical_flagged: int

    ml_flagged: int

    hybrid_flagged: int

    mean_pending_lift_pct: float

    threshold_pct: float