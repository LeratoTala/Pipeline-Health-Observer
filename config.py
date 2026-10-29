# Pipeline Health Observer — configuration
# Adjust these values to tune thresholds without touching any source code.

PIPELINE = {
    "data_path": "data/students.csv",
    "db_path":   "pipeline_health.db",
}

SCHEMA = {
    "expected_columns": [
        "student_id",
        "name",
        "grade",
        "score",
        "enrollment_date",
        "last_updated",
    ],
}

FRESHNESS = {
    "date_column":  "last_updated",
    "max_age_days": 7,
}

ROW_COUNT = {
    "expected_min": 10,
    "expected_max": 1000,
}

NULL_RATE = {
    # Columns to check for missing values.
    # A WARN is raised when any column's null rate exceeds max_null_rate.
    "columns": [
        "student_id",
        "name",
        "grade",
        "score",
        "enrollment_date",
        "last_updated",
    ],
    "max_null_rate": 0.05,   # 5 %
}

DUPLICATES = {
    # Column whose values must be unique across all rows.
    "id_column": "student_id",
}
