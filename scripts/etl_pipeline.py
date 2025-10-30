"""Integrate synthetic fabrication datasets into a warehouse-friendly table."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Dict, Iterable, Tuple

import duckdb
import numpy as np
import pandas as pd

DATA_FILES = {
    "powermill": "powermill_toolpaths.csv",
    "kuka": "kuka_telemetry.csv",
    "quality": "quality_inspection.csv",
    "erp": "erp_costs.csv",
    "operator": "operator_log.csv",
}


def configure_logging() -> None:
    """Configure a simple logging format for pipeline messages."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
    )


def load_csv(path: Path) -> pd.DataFrame:
    """Load a CSV file into a DataFrame with consistent options."""
    return pd.read_csv(path)


def merge_sources(data_dir: Path) -> Tuple[pd.DataFrame, Dict[str, int]]:
    """Read and merge all source CSVs into a single table."""
    sources = {name: load_csv(data_dir / filename) for name, filename in DATA_FILES.items()}
    counts = {name: df["job_id"].nunique() for name, df in sources.items()}

    merged = sources["powermill"].merge(sources["kuka"], on="job_id", how="left")
    merged = merged.merge(sources["quality"], on="job_id", how="left")
    merged = merged.merge(sources["erp"], on="job_id", how="left")
    merged = merged.merge(sources["operator"], on="job_id", how="left")

    return merged, counts


def clean_integrated(df: pd.DataFrame) -> pd.DataFrame:
    """Perform light cleaning, normalization, and missing value handling."""
    df = df.copy()

    # Normalize feed rate to floats and ensure stepover precision
    df["feed_rate_mm_min"] = df["feed_rate_mm_min"].astype(float)
    df["stepover_mm"] = df["stepover_mm"].astype(float)
    df["simulation_time_min"] = df["simulation_time_min"].astype(float)

    # Fill nulls in critical numeric columns with reasonable proxies
    df["duration_s"] = df["duration_s"].fillna(df["simulation_time_min"] * 60)
    df["surface_score"] = df["surface_score"].fillna(df["surface_score"].median())
    df["defect_count"] = df["defect_count"].fillna(0).astype(int)
    df["tool_wear_cost_usd"] = df["tool_wear_cost_usd"].fillna(df["tool_wear_cost_usd"].median())
    df["labor_hours"] = df["labor_hours"].fillna(df["labor_hours"].median())
    df["revenue_usd"] = df["revenue_usd"].fillna(df["revenue_usd"].median())
    df["operator_notes"] = df["operator_notes"].fillna("No operator notes recorded.")

    # Guard against division issues later on
    df["volume_removed_cm3"] = df["volume_removed_cm3"].replace(0, np.nan)
    df["path_length_mm"] = df["path_length_mm"].replace(0, np.nan)
    df["duration_s"] = df["duration_s"].replace(0, np.nan)

    return df


def write_parquet(frame: pd.DataFrame, destination: Path) -> None:
    """Persist the integrated table to parquet using DuckDB for reliability."""
    destination.parent.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(database=":memory:")
    try:
        con.register("jobs_df", frame)
        con.execute(
            f"COPY jobs_df TO '{destination.as_posix()}' (FORMAT 'parquet', COMPRESSION 'zstd')"
        )
    finally:
        con.close()


def summarize(df: pd.DataFrame, source_counts: Dict[str, int]) -> Dict[str, object]:
    """Compute summary statistics for logging and reporting."""
    base_count = source_counts["powermill"]
    join_success = float(df["duration_s"].notna().sum()) / float(base_count)
    missing_pct = df.isna().mean().round(4).to_dict()

    summary = {
        "row_count": int(len(df)),
        "source_counts": source_counts,
        "merge_success_rate": round(join_success, 4),
        "missing_percent": missing_pct,
    }
    return summary


def run_pipeline(data_dir: Path, warehouse_dir: Path) -> Dict[str, object]:
    """Execute the ETL pipeline end-to-end."""
    configure_logging()
    logging.info("Starting ETL pipeline using data dir %s", data_dir)

    merged, counts = merge_sources(data_dir)
    logging.info("Loaded sources with job counts: %s", counts)

    cleaned = clean_integrated(merged)
    summary = summarize(cleaned, counts)

    output_path = warehouse_dir / "jobs_integrated.parquet"
    write_parquet(cleaned, output_path)
    logging.info("Integrated dataset written to %s", output_path)

    summary_path = warehouse_dir / "etl_summary.json"
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(json.dumps(summary, indent=2))
    logging.info("Summary metrics: %s", summary)

    return summary


def parse_args(argv: Iterable[str] | None = None) -> Dict[str, Path]:
    """Minimal argument parsing for CLI invocation."""
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=None,
        help="Directory containing the generated CSV files (defaults to data/).",
    )
    parser.add_argument(
        "--warehouse-dir",
        type=Path,
        default=None,
        help="Directory where warehouse outputs should be written (defaults to warehouse/).",
    )

    args = parser.parse_args(args=argv)
    data_dir = args.data_dir or Path(__file__).resolve().parents[1] / "data"
    warehouse_dir = args.warehouse_dir or Path(__file__).resolve().parents[1] / "warehouse"

    return {"data_dir": data_dir, "warehouse_dir": warehouse_dir}


def main(argv: Iterable[str] | None = None) -> None:
    """Entry point for command line execution."""
    args = parse_args(argv)
    summary = run_pipeline(args["data_dir"], args["warehouse_dir"])
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
