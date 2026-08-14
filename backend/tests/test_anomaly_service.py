from app.services.anomaly_service import (
    calculate_hybrid_anomalies,
)


def test_hybrid_anomaly_service():
    result = (
        calculate_hybrid_anomalies(
            top_n=5
        )
    )

    assert result[
        "total_centres"
    ] > 0

    assert (
        result[
            "returned_results"
        ]
        <= 5
    )

    assert (
        result[
            "hybrid_flagged"
        ]
        >= result[
            "statistical_flagged"
        ]
    )

    for anomaly in result[
        "anomalies"
    ]:

        assert (
            anomaly[
                "hybrid_anomaly"
            ]
            is True
        )

        assert anomaly[
            "risk_level"
        ] in {
            "Critical",
            "High",
            "Medium",
            "Watch",
            "Normal",
        }

        assert isinstance(
            anomaly[
                "reasons"
            ],
            list,
        )

        assert len(
            anomaly[
                "reasons"
            ]
        ) > 0