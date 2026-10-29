WTC-MMBMJF8B

# Pipeline-Health-Observer

## Overview

Pipeline Health Observer monitors a data pipeline to detect data quality issues and track pipeline health.
It loads a CSV dataset, runs a suite of health checks, stores the results in SQLite, and displays them
## Features

- Detect schema drift — flags missing or unexpected columns.
- Monitor data freshness — warns when data hasn't been updated recently.
- Detect row-count anomalies — flags datasets that are too small or too large.
- Detect high null rates — warns when any column exceeds the configured missing-value threshold.
- Detect duplicate rows — flags duplicate values in the ID column.
- Store health-check results in SQLite for historical tracking.
- Display monitoring results in a Streamlit dashboard with colour-coded statuses.
- All thresholds configurable via `config.py` — no source code changes needed.
- Store health-check results in SQLite for historical tracking.
- Display monitoring results in a Streamlit dashboard with colour-coded statuses.

## Technologies

- Python 3.11+
- pandas
- SQLite (built into Python)
- Streamlit
- pytest

## Project Structure

```text
Pipeline-Health-Observer/
├── data/
│   └── students.csv          # Sample input dataset
├── src/
│   ├── checks.py             # Health check functions
│   ├── database.py           # SQLite persistence layer
│   ├── observer.py           # Orchestrates checks and DB writes
│   └── pipeline.py           # CLI entry point
├── dashboard/
│   └── app.py                # Streamlit dashboard
├── tests/
│   ├── test_checks.py        # Unit tests for check functions
│   └── test_pipeline.py      # Integration tests for pipeline and DB
├── docs/
│   └── architecture.md       # Architecture overview and component diagram
├── config.py                 # All configurable thresholds and settings
├── requirements.txt
└── README.md
```

## Setup & Running the Project

Follow these steps in order from the project root directory.

### 1. Install Python

Download and install Python 3.11 or later from [python.org/downloads](https://www.python.org/downloads/).

> **Windows:** Make sure to tick **"Add python.exe to PATH"** during installation.

### 2. Clone the repository

```bash
git clone https://github.com/LeratoTala/Pipeline-Health-Observer
cd Pipeline-Health-Observer
```

### 3. Create a virtual environment

**macOS / Linux:**
```bash
python3 -m venv .venv
```

**Windows (PowerShell):**
```powershell
python -m venv .venv
```

### 4. Activate the virtual environment

**macOS / Linux:**
```bash
source .venv/bin/activate
```

**Windows (PowerShell):**
```powershell
.venv\Scripts\Activate.ps1
```

> If you get a permissions error on Windows, run this first:
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```

### 5. Install dependencies

```bash
pip install -r requirements.txt
```

---

### 6. Run the pipeline

Loads `data/students.csv`, runs all health checks, and saves results to `pipeline_health.db`.

```bash
python src/pipeline.py
```

Expected output:

```
Running Pipeline Health Observer...

✅  [OK]   schema_drift: Schema matches expected columns.
✅  [OK]   freshness: Data is fresh. Latest record: 2026-10-29.
✅  [OK]   row_count_anomaly: Row count 20 is within expected range.
✅  [OK]   null_rate: All checked columns are within the 5% null-rate threshold.
✅  [OK]   duplicate_rows: No duplicate values found in 'student_id'.

All checks passed.
```

> The pipeline exits with code `1` if any check has a `FAIL` status, making it safe to use in CI.

### 7. Launch the dashboard

> Run the pipeline (step 6) at least once before launching the dashboard, so there is data to display.

```bash
streamlit run dashboard/app.py
```

Then open [http://localhost:8501](http://localhost:8501) in your browser.

The dashboard shows:
- Summary metrics (total runs, OK / WARN / FAIL counts)
- A full colour-coded table of all check results
- A breakdown of the most recent run

### 8. Run the tests

```bash
pytest tests/ -v
```

Expected output: 19 tests passing — 15 in `test_checks.py` and 4 in `test_pipeline.py`.

## How It Works

1. `pipeline.py` reads `config.py` for the data path, then calls `observer.run_checks()`.
2. The observer loads the CSV into a pandas DataFrame.
3. Each check in `checks.py` returns a dict with `check`, `status` (`OK` / `WARN` / `FAIL`), and `details`.
4. Results are written to the `health_checks` SQLite table via `database.py`.
5. The Streamlit dashboard reads from the same SQLite file and renders the results.

## Configuration

All thresholds live in `config.py` at the project root. Edit it to tune any check without touching source code:

```python
FRESHNESS    = {"date_column": "last_updated", "max_age_days": 7}
ROW_COUNT    = {"expected_min": 10, "expected_max": 1000}
NULL_RATE    = {"columns": [...], "max_null_rate": 0.05}   # 5 %
DUPLICATES   = {"id_column": "student_id"}
```

See [docs/architecture.md](docs/architecture.md) for a full component diagram.


