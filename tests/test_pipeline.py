import sys
import types
import pandas as pd
import pytest
from datetime import datetime, timezone
from src.observer import run_checks
from src.database import init_db, get_all_results


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def temp_csv(tmp_path):
    """Write a small valid CSV to a temp file and return its path."""
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    df = pd.DataFrame({
        "student_id":      range(1, 16),
        "name":            [f"Student {i}" for i in range(1, 16)],
        "grade":           [10] * 15,
        "score":           [75.0] * 15,
        "enrollment_date": ["2024-01-01"] * 15,
        "last_updated":    [today] * 15,
    })
    csv_path = tmp_path / "students.csv"
    df.to_csv(csv_path, index=False)
    return str(csv_path)


@pytest.fixture
def temp_db(tmp_path):
    """Return a path to a temporary SQLite database."""
    return str(tmp_path / "test_health.db")


@pytest.fixture
def temp_config(tmp_path, monkeypatch):
    """
    Inject a synthetic config module so tests don't depend on the real
    config.py or any external file.
    """
    module_name = "test_config_stub"
    mod = types.ModuleType(module_name)
    mod.PIPELINE = {
        "data_path": str(tmp_path / "students.csv"),
        "db_path":   str(tmp_path / "test_health.db"),
    }
    mod.SCHEMA = {
        "expected_columns": [
            "student_id", "name", "grade", "score",
            "enrollment_date", "last_updated",
        ],
    }
    mod.FRESHNESS = {"date_column": "last_updated", "max_age_days": 7}
    mod.ROW_COUNT = {"expected_min": 10, "expected_max": 1000}
    mod.NULL_RATE = {
        "columns": ["student_id", "name", "grade", "score",
                    "enrollment_date", "last_updated"],
        "max_null_rate": 0.05,
    }
    mod.DUPLICATES = {"id_column": "student_id"}

    monkeypatch.setitem(sys.modules, module_name, mod)
    return module_name


# ── Tests ─────────────────────────────────────────────────────────────────────

def test_run_checks_returns_all_checks(temp_csv, temp_db, temp_config):
    results = run_checks(temp_csv, db_path=temp_db, config_module=temp_config)
    check_names = [r["check"] for r in results]
    assert "schema_drift" in check_names
    assert "freshness" in check_names
    assert "row_count_anomaly" in check_names
    assert "null_rate" in check_names
    assert "duplicate_rows" in check_names


def test_run_checks_persists_results(temp_csv, temp_db, temp_config):
    run_checks(temp_csv, db_path=temp_db, config_module=temp_config)
    stored = get_all_results(db_path=temp_db)
    assert len(stored) == 5  # one row per check


def test_run_checks_valid_data_all_ok(temp_csv, temp_db, temp_config):
    results = run_checks(temp_csv, db_path=temp_db, config_module=temp_config)
    statuses = [r["status"] for r in results]
    assert all(s in ("OK", "WARN") for s in statuses)


def test_run_checks_schema_drift_detected(tmp_path, temp_db, temp_config):
    """Pipeline should report FAIL when CSV has wrong columns."""
    bad_df = pd.DataFrame({"wrong_col": [1, 2, 3]})
    bad_csv = tmp_path / "bad.csv"
    bad_df.to_csv(bad_csv, index=False)

    results = run_checks(str(bad_csv), db_path=temp_db, config_module=temp_config)
    schema_result = next(r for r in results if r["check"] == "schema_drift")
    assert schema_result["status"] == "FAIL"
