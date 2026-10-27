import pandas as pd
import pytest
from datetime import datetime, timedelta
from src.checks import (
    check_schema_drift,
    check_freshness,
    check_row_count_anomaly,
)


# ── Fixtures ──────────────────────────────────────────────────────────────────

EXPECTED_COLUMNS = [
    "student_id", "name", "grade", "score",
    "enrollment_date", "last_updated",
]


@pytest.fixture
def valid_df():
    today = datetime.utcnow().strftime("%Y-%m-%d")
    return pd.DataFrame({
        "student_id":      [1, 2, 3],
        "name":            ["Alice", "Bob", "Carol"],
        "grade":           [10, 11, 12],
        "score":           [80.0, 75.5, 90.2],
        "enrollment_date": ["2024-01-01"] * 3,
        "last_updated":    [today] * 3,
    })


# ── Schema drift ──────────────────────────────────────────────────────────────

def test_schema_drift_ok(valid_df):
    result = check_schema_drift(valid_df, EXPECTED_COLUMNS)
    assert result["status"] == "OK"


def test_schema_drift_missing_column(valid_df):
    df = valid_df.drop(columns=["score"])
    result = check_schema_drift(df, EXPECTED_COLUMNS)
    assert result["status"] == "FAIL"
    assert "score" in result["details"]


def test_schema_drift_extra_column(valid_df):
    valid_df["unexpected_col"] = 0
    result = check_schema_drift(valid_df, EXPECTED_COLUMNS)
    assert result["status"] == "FAIL"
    assert "unexpected_col" in result["details"]


# ── Freshness ─────────────────────────────────────────────────────────────────

def test_freshness_ok(valid_df):
    result = check_freshness(valid_df, "last_updated", max_age_days=7)
    assert result["status"] == "OK"


def test_freshness_stale(valid_df):
    stale_date = (datetime.utcnow() - timedelta(days=30)).strftime("%Y-%m-%d")
    valid_df["last_updated"] = stale_date
    result = check_freshness(valid_df, "last_updated", max_age_days=7)
    assert result["status"] == "WARN"
    assert "30" in result["details"]


def test_freshness_missing_column(valid_df):
    result = check_freshness(valid_df, "nonexistent_col")
    assert result["status"] == "FAIL"


# ── Row count anomaly ─────────────────────────────────────────────────────────

def test_row_count_ok(valid_df):
    result = check_row_count_anomaly(valid_df, expected_min=1, expected_max=10)
    assert result["status"] == "OK"


def test_row_count_too_few(valid_df):
    result = check_row_count_anomaly(valid_df, expected_min=10, expected_max=100)
    assert result["status"] == "FAIL"
    assert "below" in result["details"]


def test_row_count_too_many(valid_df):
    result = check_row_count_anomaly(valid_df, expected_min=1, expected_max=2)
    assert result["status"] == "FAIL"
    assert "exceeds" in result["details"]
