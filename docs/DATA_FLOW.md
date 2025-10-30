# Data Flow

```
PowerMill CSV  ─┐
               ├─▶ scripts/etl_pipeline.py ──▶ warehouse/jobs_integrated.parquet
KUKA Telemetry ┤
Quality Checks ┤
ERP Costs      ┤
Operator Log   ┘
                               │
                               ▼
               scripts/feature_engineering.py ──▶ warehouse/ml_features.parquet
                               │
          ┌────────────────────┴────────────────────┐
          ▼                                         ▼
Streamlit Dashboard (app/app.py)       Flask Feature API (app/api.py)
```

## Stage-by-Stage Walkthrough
1. **Synthetic Sources (`scripts/generate_data.py`)**  
   Generates consistent `job_id` keys across PowerMill toolpaths, KUKA robot telemetry, QC outcomes, ERP cost lines, and operator notes.
2. **ETL Integration (`scripts/etl_pipeline.py`)**  
   Reads all CSVs, normalizes units, backfills critical nulls, and writes `jobs_integrated.parquet` using DuckDB for portability.
3. **Quality Monitoring (`scripts/data_quality.py`)**  
   Calculates source completeness, critical null counts, duration outliers, and tool catalog drift, persisting `data_quality_report.json`.
4. **Feature Engineering (`scripts/feature_engineering.py`)**  
   Derives downstream metrics (energy-per-cm³, quality-vs-speed, profit margin, etc.) and saves `ml_features.parquet` for analytics and APIs.
5. **Consumers (`app/app.py`, `app/api.py`)**  
   Streamlit visualizes KPIs, process analytics, profitability, feature catalog, and data quality; the optional Flask API serves feature slices.
