import importlib
import pandas as pd

from src.checks import (
    check_schema_drift,
    check_freshness,
    check_row_count_anomaly,
    check_null_rate,
    check_duplicate_rows,
)
from src.database import init_db, insert_result


def load_config(config_module: str = "config"):
    """
    Load configuration from a Python module.
    Accepts a dotted module name (e.g. 'config' or 'tests.test_config').
    Returns a module object whose attributes are the config dicts.
    """
    return importlib.import_module(config_module)


def run_checks(csv_path: str, db_path: str | None = None,
               config_module: str = "config") -> list[dict]:
    """
    Load the CSV, run all health checks, persist results, and return them.
    All thresholds are read from the config module (default: config.py).
    """
    cfg = load_config(config_module)

    # Allow db_path override (used in tests); fall back to config value.
    resolved_db_path = db_path or cfg.PIPELINE["db_path"]

    init_db(resolved_db_path)

    df = pd.read_csv(csv_path)

    results = [
        check_schema_drift(df, cfg.SCHEMA["expected_columns"]),
        check_freshness(
            df,
            date_column=cfg.FRESHNESS["date_column"],
            max_age_days=cfg.FRESHNESS["max_age_days"],
        ),
        check_row_count_anomaly(
            df,
            expected_min=cfg.ROW_COUNT["expected_min"],
            expected_max=cfg.ROW_COUNT["expected_max"],
        ),
        check_null_rate(
            df,
            columns=cfg.NULL_RATE["columns"],
            max_null_rate=cfg.NULL_RATE["max_null_rate"],
        ),
        check_duplicate_rows(df, id_column=cfg.DUPLICATES["id_column"]),
    ]

    for result in results:
        insert_result(
            check_name=result["check"],
            status=result["status"],
            details=result["details"],
            db_path=resolved_db_path,
        )

    return results
