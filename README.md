Fabrication Data Platform Demo
================================

### Elevator Pitch
This repo demonstrates how a data engineer stitches together CAM, robotic telemetry, QC, and ERP context for a robotic stone-carving shop. Synthetic datasets feed a repeatable Python ETL pipeline, data quality guardrails, engineered metrics, and a Streamlit dashboard that showcases production, profitability, and feature-store views.

### Installation & Quickstart
```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python scripts/generate_data.py && python scripts/etl_pipeline.py
python scripts/data_quality.py && python scripts/feature_engineering.py
```
*Optional:* `streamlit run app/app.py` for the dashboard, `flask --app app.api run --port 8000` for the API.

### Repository Highlights
- **Synthetic data generators** capture realistic ranges for PowerMill toolpaths, KUKA telemetry, QC outcomes, ERP costs, and operator notes—all keyed by job.
- **ETL + warehouse** pipelines merge sources into Parquet artifacts (via DuckDB), handle missingness, and log merge fidelity.
- **Data quality checks** quantify completeness, nulls, outliers, and tool catalog drift with machine-friendly reports.
- **Feature engineering** surfaces metrics like energy-per-cm³, profit margin, and quality-vs-speed for analytics/ML.
- **Streamlit dashboard** brings KPIs, process analytics, cost views, feature catalog, and quality telemetry into one interface.
- **Optional Flask API** exposes feature-store lookups for job- or material-scoped slices.

### Project Structure
```
fabrication-data-platform/
├─ data/                  # Synthetic CSVs (generated)
├─ scripts/               # Generation, ETL, quality, feature jobs
├─ warehouse/             # Parquet outputs & reports (generated)
├─ app/                   # Streamlit app + optional API
└─ docs/                  # Architecture, data flow, feature catalog
```

### Learn More
- [Docs overview](docs/README.md)
- [Feature catalog](docs/FEATURES.md)
- [Data flow walkthrough](docs/DATA_FLOW.md)
- [Boundaries of the demo](docs/WHAT_THIS_IS_NOT.md)
