# Pipeline-Health-Observer

## Overview

Pipeline Health Observer monitors a data pipeline to detect data quality issues and track pipeline health.
It loads a CSV dataset, runs a suite of health checks, stores the results in SQLite, and displays them
in an interactive Streamlit dashboard.

## Features

- Detect schema drift — flags missing or unexpected columns.
- Monitor data freshness — warns when data hasn't been updated recently.
- Detect row-count anomalies — flags datasets that are too small or too large.
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
├── requirements.txt
└── README.md
```

## Setup

### 1. Install Python

Download and install Python 3.11 or later from [python.org/downloads](https://www.python.org/downloads/).

> **Windows:** Make sure to tick **"Add python.exe to PATH"** during installation.

### 2. Clone the repository

```bash
git clone <your-repository-url>
cd Pipeline-Health-Observer
```

### 3. Create and activate a virtual environment

**macOS / Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

**Windows (PowerShell):**
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

> If you get a permissions error on Windows, run this first:
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

## Running the Project

### Run the pipeline

Loads `data/students.csv`, runs all health checks, and saves results to `pipeline_health.db`.

```bash
python src/pipeline.py
```

Expected output:

```
Running Pipeline Health Observer...

✅  [OK]   schema_drift: Schema matches expected columns.
✅  [OK]   freshness: Data is fresh. Latest record: 2026-10-27.
✅  [OK]   row_count_anomaly: Row count 20 is within expected range.

All checks passed.
```

The pipeline exits with code `1` if any check has a `FAIL` status, making it safe to use in CI.

### Launch the dashboard

Starts the Streamlit dashboard at `http://localhost:8501`.

> Run the pipeline at least once first so there is data to display.

```bash
streamlit run dashboard/app.py
```

The dashboard shows:
- Summary metrics (total runs, OK / WARN / FAIL counts)
- A full colour-coded table of all check results
- A breakdown of the most recent run

### Run the tests

```bash
pytest tests/ -v
```

Expected output: 13 tests passing across `test_checks.py` (9 tests) and `test_pipeline.py` (4 tests).

## How It Works

1. `pipeline.py` calls `observer.run_checks()` with the path to the CSV.
2. The observer loads the CSV into a pandas DataFrame.
3. Each check in `checks.py` returns a dict with `check`, `status` (`OK` / `WARN` / `FAIL`), and `details`.
4. Results are written to the `health_checks` SQLite table via `database.py`.
5. The Streamlit dashboard reads from the same SQLite file and renders the results.

See [docs/architecture.md](docs/architecture.md) for a full component diagram.

## Project Status

Complete. All source modules, tests, dashboard, and documentation are implemented.
