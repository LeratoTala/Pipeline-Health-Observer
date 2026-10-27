import pandas as pd
from datetime import datetime, timedelta


def check_schema_drift(df: pd.DataFrame,
                       expected_columns: list[str]) -> dict:
    """
    Compare the DataFrame's actual columns against the expected schema.
    Returns FAIL if any column is missing or unexpected.
    """
    actual = set(df.columns.tolist())
    expected = set(expected_columns)

    missing = expected - actual
    unexpected = actual - expected

    if missing or unexpected:
        details = []
        if missing:
            details.append(f"Missing columns: {sorted(missing)}")
        if unexpected:
            details.append(f"Unexpected columns: {sorted(unexpected)}")
        return {"check": "schema_drift", "status": "FAIL",
                "details": " | ".join(details)}

    return {"check": "schema_drift", "status": "OK",
            "details": "Schema matches expected columns."}


def check_freshness(df: pd.DataFrame, date_column: str,
                    max_age_days: int = 7) -> dict:
    """
    Check that the most recent value in date_column is within max_age_days
    of today. Returns WARN if data is stale.
    """
    if date_column not in df.columns:
        return {"check": "freshness", "status": "FAIL",
                "details": f"Date column '{date_column}' not found."}

    latest = pd.to_datetime(df[date_column]).max()
    age = datetime.utcnow() - latest.to_pydatetime()

    if age > timedelta(days=max_age_days):
        return {"check": "freshness", "status": "WARN",
                "details": (f"Latest record is {age.days} day(s) old "
                            f"(threshold: {max_age_days} days).")}

    return {"check": "freshness", "status": "OK",
            "details": f"Data is fresh. Latest record: {latest.date()}."}


def check_row_count_anomaly(df: pd.DataFrame,
                            expected_min: int,
                            expected_max: int) -> dict:
    """
    Check that the number of rows in the DataFrame falls within
    [expected_min, expected_max]. Returns FAIL if outside the range.
    """
    row_count = len(df)

    if row_count < expected_min:
        return {"check": "row_count_anomaly", "status": "FAIL",
                "details": (f"Row count {row_count} is below "
                            f"minimum {expected_min}.")}

    if row_count > expected_max:
        return {"check": "row_count_anomaly", "status": "FAIL",
                "details": (f"Row count {row_count} exceeds "
                            f"maximum {expected_max}.")}

    return {"check": "row_count_anomaly", "status": "OK",
            "details": f"Row count {row_count} is within expected range."}
