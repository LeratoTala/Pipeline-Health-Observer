# Pipeline-Health-Observer

# Pipeline Health Observer

## Overview

Pipeline Health Observer monitors a data pipeline to detect data quality issues and track pipeline health.

## Features

- Detect schema drift.
- Monitor data freshness.
- Detect row-count anomalies.
- Store health-check results in SQLite.
- Display monitoring results using Streamlit.

## Technologies

- Python
- pandas
- SQLite
- Streamlit
- pytest

## Project Structure

```text
pipeline-health-observer/
├── data/
├── src/
├── dashboard/
├── tests/
├── docs/
├── requirements.txt
└── README.md
```

## Setup

Clone the repository and enter the project directory.

```bash
git clone <your-repository-url>
cd pipeline-health-observer
```

Create and activate a virtual environment.

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install the dependencies.

```bash
pip install -r requirements.txt
```

## Usage

Run the data pipeline:

```bash
python src/pipeline.py
```

Launch the dashboard:

```bash
streamlit run dashboard/app.py
```

Run the tests:

```bash
pytest -v
```

## Project Status

This project is under development. Features and documentation will be updated as development progresses.