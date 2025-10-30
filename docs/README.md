# Documentation Hub

This folder expands on how the synthetic fabrication data platform is assembled, governed, and consumed.

- **[FEATURES.md](FEATURES.md):** Definitions, formulas, and business context for each engineered metric.
- **[DATA_FLOW.md](DATA_FLOW.md):** ASCII diagram and narrative walking through ingestion → warehouse → analytics.
- **[WHAT_THIS_IS_NOT.md](WHAT_THIS_IS_NOT.md):** Explicit scope boundaries so stakeholders understand the demo’s limits.

## Key Concepts
- **Multi-source integration:** PowerMill CAM output anchors job IDs that are enriched with KUKA telemetry, QC scoring, ERP costs, and operator observations.
- **Warehouse-first approach:** DuckDB writes Parquet artifacts for reproducible analytics, feature stores, and dashboard consumption.
- **Quality guardrails:** The `data_quality.py` script quantifies completeness, nulls, outliers, and tool-catalog drift so the demo mirrors production observability.
