from fastapi import (
    APIRouter,
    HTTPException,
    Query,
)

from app.models.analytics import (
    AnalyticsSummaryResponse,
    HybridAnalyticsResponse,
)

from app.services.anomaly_service import (
    calculate_hybrid_anomalies,
)


router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"],
)


@router.get(
    "/anomalies",
    response_model=HybridAnalyticsResponse,
)
def get_anomalies(
    top: int = Query(
        default=10,
        ge=1,
        le=100,
        description=(
            "Maximum number of hybrid anomaly "
            "records to return."
        ),
    ),
):

    try:
        return calculate_hybrid_anomalies(
            top_n=top
        )

    except FileNotFoundError as exc:

        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc

    except ValueError as exc:

        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=(
                "Unexpected error while running "
                "hybrid anomaly detection."
            ),
        ) from exc


@router.get(
    "/summary",
    response_model=AnalyticsSummaryResponse,
)
def get_analytics_summary():

    try:

        result = (
            calculate_hybrid_anomalies(
                top_n=1
            )
        )

        return {
            "total_centres": result[
                "total_centres"
            ],
            "statistical_flagged": result[
                "statistical_flagged"
            ],
            "ml_flagged": result[
                "ml_flagged"
            ],
            "hybrid_flagged": result[
                "hybrid_flagged"
            ],
            "mean_pending_lift_pct": result[
                "mean_pending_lift_pct"
            ],
            "threshold_pct": result[
                "threshold_pct"
            ],
        }

    except FileNotFoundError as exc:

        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc

    except ValueError as exc:

        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=(
                "Unexpected error while generating "
                "analytics summary."
            ),
        ) from exc