import pandas as pd

from src.checks import (
    check_schema_drift,
    check_freshness,
    check_row_count_anomaly,
)
from src.database import init_db, insert_result


EXPECTED_COLUMNS = [
    "student_id", "name", "grade", "score",
    "enrollment_date", "last_updated",
]


def run_checks(csv_path: str, db_path: str = "pipeline_health.db") -> list[dict]:
    """
    Load the CSV, run all health checks, persist results, and return them.
    """
    init_db(db_path)

    df = pd.read_csv(csv_path)

    results = [
        check_schema_drift(df, EXPECTED_COLUMNS),
        check_freshness(df, date_column="last_updated", max_age_days=7),
        check_row_count_anomaly(df, expected_min=10, expected_max=1000),
    ]

    for result in results:
        insert_result(
            check_name=result["check"],
            status=result["status"],
            details=result["details"],
            db_path=db_path,
        )

    return results
