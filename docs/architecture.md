# Architecture

## Overview

Pipeline Health Observer is a lightweight data quality monitoring system.
It loads a CSV dataset, runs a suite of health checks, persists results
to SQLite, and displays them in a Streamlit dashboard.

## Component Diagram

```
data/students.csv
       │
       ▼
 src/pipeline.py  ◄── entry point (python src/pipeline.py)
       │
       ▼
 src/observer.py  ◄── orchestrates all checks
       │
       ├──► src/checks.py        ◄── check_schema_drift()
       │                              check_freshness()
       │                              check_row_count_anomaly()
       │
       └──► src/database.py      ◄── init_db(), insert_result()
                  │
                  ▼
         pipeline_health.db  (SQLite)
                  │
                  ▼
        dashboard/app.py     ◄── streamlit run dashboard/app.py
```

## Data Flow

1. `pipeline.py` calls `observer.run_checks(csv_path)`.
2. The observer loads the CSV into a pandas DataFrame.
3. Each check function receives the DataFrame and returns a result dict
   with keys `check`, `status` (`OK` / `WARN` / `FAIL`), and `details`.
4. Results are written to the `health_checks` table in SQLite via `database.py`.
5. The Streamlit dashboard reads from the same SQLite file and renders
   a summary table with colour-coded statuses.

## Module Responsibilities

| Module | Responsibility |
|---|---|
| `src/checks.py` | Pure check functions — no I/O, easy to unit test |
| `src/database.py` | All SQLite access — schema creation, insert, select |
| `src/observer.py` | Orchestration — loads data, calls checks, calls DB |
| `src/pipeline.py` | CLI entry point — calls observer, prints output, sets exit code |
| `dashboard/app.py` | Streamlit UI — reads DB, renders metrics and tables |

## Technology Choices

- **pandas** — DataFrame-based data loading and manipulation
- **SQLite** — zero-config embedded database for persisting check results
- **Streamlit** — rapid dashboard UI without a separate frontend
- **pytest** — unit and integration testing
