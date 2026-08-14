from pathlib import Path

import numpy as np
import pandas as pd

from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler


PROJECT_ROOT = Path(__file__).resolve().parents[3]

DEFAULT_DATASET_PATH = (
    PROJECT_ROOT
    / "data"
    / "sample_procurement_data.xlsx"
)


def load_dataset() -> pd.DataFrame:
    """
    Load the synthetic procurement dataset.
    """

    if not DEFAULT_DATASET_PATH.exists():
        raise FileNotFoundError(
            f"Dataset not found: {DEFAULT_DATASET_PATH}"
        )

    dataframe = pd.read_excel(
        DEFAULT_DATASET_PATH
    )

    dataframe.columns = (
        dataframe.columns
        .astype(str)
        .str.strip()
        .str.replace("\n", " ", regex=False)
        .str.replace(r"\s+", "_", regex=True)
    )

    return dataframe


def prepare_features(
    dataframe: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Clean source columns and generate anomaly features.
    """

    required_columns = [
        "Procurement_Centre",
        "Quantity_Procured_(qtl)",
        "DO_Issued",
        "DO_Lifted",
        "TO_Issued",
        "TO_Lifted",
        "Total_Lifted",
        "Pending_Lift_(qtl)",
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in dataframe.columns
    ]

    if missing_columns:
        raise ValueError(
            "Dataset is missing required columns: "
            + ", ".join(missing_columns)
        )

    dataframe = dataframe.copy()

    numeric_columns = [
        "Quantity_Procured_(qtl)",
        "DO_Issued",
        "DO_Lifted",
        "TO_Issued",
        "TO_Lifted",
        "Total_Lifted",
        "Pending_Lift_(qtl)",
    ]

    for column in numeric_columns:
        dataframe[column] = pd.to_numeric(
            dataframe[column],
            errors="coerce",
        )

    dataframe = dataframe.dropna(
        subset=[
            "Procurement_Centre",
            "Quantity_Procured_(qtl)",
            "Total_Lifted",
            "Pending_Lift_(qtl)",
        ]
    )

    dataframe = dataframe[
        dataframe["Quantity_Procured_(qtl)"] > 0
    ].copy()

    dataframe["Pending_Lift_Pct"] = (
        dataframe["Pending_Lift_(qtl)"]
        / dataframe["Quantity_Procured_(qtl)"]
        * 100
    )

    dataframe["Lifted_Pct"] = (
        dataframe["Total_Lifted"]
        / dataframe["Quantity_Procured_(qtl)"]
        * 100
    )

    dataframe["DO_Lift_Ratio"] = np.where(
        dataframe["DO_Issued"] > 0,
        dataframe["DO_Lifted"]
        / dataframe["DO_Issued"],
        0,
    )

    dataframe["TO_Lift_Ratio"] = np.where(
        dataframe["TO_Issued"] > 0,
        dataframe["TO_Lifted"]
        / dataframe["TO_Issued"],
        0,
    )

    feature_columns = [
        "Quantity_Procured_(qtl)",
        "DO_Issued",
        "DO_Lifted",
        "TO_Issued",
        "TO_Lifted",
        "Total_Lifted",
        "Pending_Lift_(qtl)",
        "Pending_Lift_Pct",
        "Lifted_Pct",
        "DO_Lift_Ratio",
        "TO_Lift_Ratio",
    ]

    feature_frame = (
        dataframe[
            feature_columns
        ]
        .replace(
            [np.inf, -np.inf],
            np.nan,
        )
        .fillna(0)
    )

    return dataframe, feature_frame


def add_statistical_detection(
    dataframe: pd.DataFrame,
) -> tuple[pd.DataFrame, dict]:
    """
    Add the existing 3-sigma anomaly rule.
    """

    dataframe = dataframe.copy()

    mean_pending_pct = dataframe[
        "Pending_Lift_Pct"
    ].mean()

    sigma = dataframe[
        "Pending_Lift_Pct"
    ].std(ddof=0)

    threshold = (
        mean_pending_pct
        + (3 * sigma)
    )

    dataframe[
        "Statistical_Anomaly"
    ] = (
        dataframe[
            "Pending_Lift_Pct"
        ] > threshold
    )

    stats = {
        "mean_pending_lift_pct": round(
            float(mean_pending_pct),
            2,
        ),
        "sigma": round(
            float(sigma),
            2,
        ),
        "threshold_pct": round(
            float(threshold),
            2,
        ),
    }

    return dataframe, stats


def add_isolation_forest_detection(
    dataframe: pd.DataFrame,
    feature_frame: pd.DataFrame,
) -> pd.DataFrame:
    """
    Apply Isolation Forest to multivariate procurement features.
    """

    dataframe = dataframe.copy()

    scaler = StandardScaler()

    scaled_features = scaler.fit_transform(
        feature_frame
    )

    model = IsolationForest(
        n_estimators=300,
        contamination="auto",
        random_state=42,
    )

    predictions = model.fit_predict(
        scaled_features
    )

    decision_scores = model.decision_function(
        scaled_features
    )

    dataframe[
        "ML_Anomaly"
    ] = predictions == -1

    dataframe[
        "Isolation_Score"
    ] = decision_scores

    return dataframe


def determine_risk_level(
    statistical_anomaly: bool,
    ml_anomaly: bool,
    pending_pct: float,
) -> str:
    """
    Assign an interpretable risk tier.
    """

    if statistical_anomaly and ml_anomaly:
        return "Critical"

    if statistical_anomaly:
        return "High"

    if ml_anomaly:
        return "Medium"

    if pending_pct >= 5:
        return "Watch"

    return "Normal"


def explain_anomaly(
    row: pd.Series,
) -> list[str]:
    """
    Generate transparent reasons for each anomaly flag.
    """

    reasons = []

    if bool(
        row["Statistical_Anomaly"]
    ):
        reasons.append(
            "Pending lifting percentage exceeds the "
            "3-sigma statistical threshold."
        )

    if bool(
        row["ML_Anomaly"]
    ):
        reasons.append(
            "Isolation Forest identifies this centre "
            "as unusual across multiple procurement "
            "and lifting features."
        )

    if (
        float(
            row["Pending_Lift_Pct"]
        ) >= 10
    ):
        reasons.append(
            "Pending lifting exceeds 10% of the "
            "quantity procured."
        )

    if (
        float(
            row["DO_Issued"]
        ) > 0
        and float(
            row["DO_Lift_Ratio"]
        ) < 0.75
    ):
        reasons.append(
            "A relatively low share of issued delivery "
            "orders has been lifted."
        )

    if (
        float(
            row["TO_Issued"]
        ) > 0
        and float(
            row["TO_Lift_Ratio"]
        ) < 0.75
    ):
        reasons.append(
            "A relatively low share of issued transport "
            "orders has been lifted."
        )

    if not reasons:
        reasons.append(
            "No material anomaly reason detected."
        )

    return reasons


def calculate_hybrid_anomalies(
    top_n: int = 10,
) -> dict:
    """
    Run the complete hybrid anomaly pipeline.
    """

    dataframe = load_dataset()

    dataframe, feature_frame = (
        prepare_features(
            dataframe
        )
    )

    dataframe, statistical_stats = (
        add_statistical_detection(
            dataframe
        )
    )

    dataframe = (
        add_isolation_forest_detection(
            dataframe,
            feature_frame,
        )
    )

    dataframe[
        "Hybrid_Anomaly"
    ] = (
        dataframe[
            "Statistical_Anomaly"
        ]
        | dataframe[
            "ML_Anomaly"
        ]
    )

    dataframe[
        "Risk_Level"
    ] = dataframe.apply(
        lambda row: determine_risk_level(
            statistical_anomaly=bool(
                row[
                    "Statistical_Anomaly"
                ]
            ),
            ml_anomaly=bool(
                row[
                    "ML_Anomaly"
                ]
            ),
            pending_pct=float(
                row[
                    "Pending_Lift_Pct"
                ]
            ),
        ),
        axis=1,
    )

    flagged = dataframe[
        dataframe[
            "Hybrid_Anomaly"
        ]
    ].copy()

    risk_rank = {
        "Critical": 4,
        "High": 3,
        "Medium": 2,
        "Watch": 1,
        "Normal": 0,
    }

    flagged[
        "Risk_Rank"
    ] = flagged[
        "Risk_Level"
    ].map(
        risk_rank
    )

    flagged = flagged.sort_values(
        by=[
            "Risk_Rank",
            "Pending_Lift_Pct",
        ],
        ascending=[
            False,
            False,
        ],
    )

    flagged = flagged.head(
        top_n
    )

    records = []

    for _, row in flagged.iterrows():

        procured_qtl = float(
            row[
                "Quantity_Procured_(qtl)"
            ]
        )

        lifted_qtl = float(
            row[
                "Total_Lifted"
            ]
        )

        pending_qtl = float(
            row[
                "Pending_Lift_(qtl)"
            ]
        )

        records.append(
            {
                "centre": str(
                    row[
                        "Procurement_Centre"
                    ]
                ),
                "district": str(
                    row.get(
                        "District",
                        "Unknown",
                    )
                ),
                "procured_qty_mt": round(
                    procured_qtl * 0.1,
                    2,
                ),
                "lifted_qty_mt": round(
                    lifted_qtl * 0.1,
                    2,
                ),
                "pending_qty_mt": round(
                    pending_qtl * 0.1,
                    2,
                ),
                "pending_lift_pct": round(
                    float(
                        row[
                            "Pending_Lift_Pct"
                        ]
                    ),
                    2,
                ),
                "statistical_anomaly": bool(
                    row[
                        "Statistical_Anomaly"
                    ]
                ),
                "ml_anomaly": bool(
                    row[
                        "ML_Anomaly"
                    ]
                ),
                "hybrid_anomaly": bool(
                    row[
                        "Hybrid_Anomaly"
                    ]
                ),
                "isolation_score": round(
                    float(
                        row[
                            "Isolation_Score"
                        ]
                    ),
                    4,
                ),
                "risk_level": str(
                    row[
                        "Risk_Level"
                    ]
                ),
                "reasons": explain_anomaly(
                    row
                ),
            }
        )

    return {
        "method": (
            "Hybrid anomaly detection: "
            "3-sigma statistical screening "
            "+ Isolation Forest"
        ),
        "total_centres": int(
            len(dataframe)
        ),
        "statistical_flagged": int(
            dataframe[
                "Statistical_Anomaly"
            ].sum()
        ),
        "ml_flagged": int(
            dataframe[
                "ML_Anomaly"
            ].sum()
        ),
        "hybrid_flagged": int(
            dataframe[
                "Hybrid_Anomaly"
            ].sum()
        ),
        "mean_pending_lift_pct": (
            statistical_stats[
                "mean_pending_lift_pct"
            ]
        ),
        "sigma": (
            statistical_stats[
                "sigma"
            ]
        ),
        "threshold_pct": (
            statistical_stats[
                "threshold_pct"
            ]
        ),
        "returned_results": len(
            records
        ),
        "disclaimer": (
            "Hybrid anomaly flags are prioritisation "
            "signals only and must not be interpreted "
            "as evidence of fraud, corruption, diversion, "
            "or other wrongdoing."
        ),
        "anomalies": records,
    }