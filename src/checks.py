import pandas as pd
from datetime import datetime, timedelta, timezone
from typing import Optional


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
    age = datetime.now(timezone.utc).replace(tzinfo=None) - latest.to_pydatetime()

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


def check_null_rate(df: pd.DataFrame,
                    columns: Optional[list[str]] = None,
                    max_null_rate: float = 0.05) -> dict:
    """
    Check that no column in `columns` exceeds `max_null_rate` missing values.
    Defaults to all columns when `columns` is None.
    Returns WARN if any column breaches the threshold.
    """
    cols_to_check = columns if columns is not None else df.columns.tolist()
    # Only inspect columns that actually exist in the DataFrame
    present = [c for c in cols_to_check if c in df.columns]

    if not present:
        return {"check": "null_rate", "status": "FAIL",
                "details": "None of the specified columns exist in the dataset."}

    offenders = []
    for col in present:
        rate = df[col].isna().mean()
        if rate > max_null_rate:
            offenders.append(f"{col} ({rate:.1%})")

    if offenders:
        return {"check": "null_rate", "status": "WARN",
                "details": (f"High null rate in: {', '.join(offenders)} "
                            f"(threshold: {max_null_rate:.0%}).")}

    return {"check": "null_rate", "status": "OK",
            "details": (f"All checked columns are within the "
                        f"{max_null_rate:.0%} null-rate threshold.")}


def check_duplicate_rows(df: pd.DataFrame, id_column: str) -> dict:
    """
    Check that `id_column` contains no duplicate values.
    Returns FAIL if duplicates are found.
    """
    if id_column not in df.columns:
        return {"check": "duplicate_rows", "status": "FAIL",
                "details": f"ID column '{id_column}' not found in dataset."}

    duplicate_mask = df[id_column].duplicated(keep=False)
    duplicate_count = duplicate_mask.sum()

    if duplicate_count > 0:
        duplicate_values = df.loc[duplicate_mask, id_column].unique().tolist()
        preview = duplicate_values[:5]
        suffix = f" (and {len(duplicate_values) - 5} more)" if len(duplicate_values) > 5 else ""
        return {"check": "duplicate_rows", "status": "FAIL",
                "details": (f"{duplicate_count} duplicate rows found in "
                            f"'{id_column}': {preview}{suffix}.")}

    return {"check": "duplicate_rows", "status": "OK",
            "details": f"No duplicate values found in '{id_column}'."}
