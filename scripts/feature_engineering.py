"""Create engineered fabrication metrics ready for analytics and ML use."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Iterable

import duckdb
import numpy as np
import pandas as pd


def load_integrated(warehouse_dir: Path) -> pd.DataFrame:
    """Load the integrated warehouse Parquet file into a DataFrame."""
    parquet_path = warehouse_dir / "jobs_integrated.parquet"
    if not parquet_path.exists():
        raise FileNotFoundError(
            "Integrated dataset not found. Run scripts/etl_pipeline.py before feature engineering."
        )
    query = duckdb.query(f"SELECT * FROM read_parquet('{parquet_path.as_posix()}')")
    return query.to_df()


def safe_divide(numerator: pd.Series, denominator: pd.Series | float) -> pd.Series:
    """Helper that handles division by zero and nulls gracefully."""
    if isinstance(denominator, (int, float)):
        if denominator == 0:
            return pd.Series([np.nan] * len(numerator), index=numerator.index)
        result = numerator / denominator
    else:
        result = numerator / denominator.replace({0: np.nan})
    return result.replace([np.inf, -np.inf], np.nan)


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """Compute derived features used across analytics and ML tasks."""
    enriched = df.copy()
    enriched["complexity_per_cm3"] = safe_divide(enriched["path_length_mm"], enriched["volume_removed_cm3"])
    enriched["load_per_mm"] = safe_divide(enriched["spindle_current_a"], enriched["path_length_mm"])
    enriched["energy_per_cm3"] = safe_divide(enriched["energy_kwh"], enriched["volume_removed_cm3"])
    enriched["tool_efficiency"] = safe_divide(enriched["volume_removed_cm3"], enriched["tool_wear_cost_usd"])
    enriched["profit_margin"] = safe_divide(
        enriched["revenue_usd"] - enriched["tool_wear_cost_usd"], enriched["revenue_usd"]
    )
    enriched["quality_vs_speed"] = safe_divide(
        enriched["surface_score"], safe_divide(enriched["duration_s"], 60.0)
    )

    return enriched


def select_feature_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Return only the columns intended for downstream ML consumption."""
    base_cols = [
        "job_id",
        "material",
        "stone_type",
        "feed_rate_mm_min",
        "stepover_mm",
        "path_length_mm",
        "volume_removed_cm3",
        "spindle_current_a",
        "duration_s",
        "surface_score",
        "tool_wear_cost_usd",
        "labor_hours",
        "revenue_usd",
    ]
    derived_cols = [
        "complexity_per_cm3",
        "load_per_mm",
        "energy_per_cm3",
        "tool_efficiency",
        "profit_margin",
        "quality_vs_speed",
    ]
    available = [col for col in base_cols + derived_cols if col in df.columns]
    return df[available].copy()


def write_parquet(frame: pd.DataFrame, destination: Path) -> None:
    """Persist features to parquet via DuckDB."""
    destination.parent.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(database=":memory:")
    try:
        con.register("features_df", frame)
        con.execute(
            f"COPY features_df TO '{destination.as_posix()}' (FORMAT 'parquet', COMPRESSION 'zstd')"
        )
    finally:
        con.close()


def run_feature_engineering(warehouse_dir: Path) -> Dict[str, object]:
    """Execute feature engineering pipeline and return summary info."""
    df = load_integrated(warehouse_dir)
    enriched = engineer_features(df)
    feature_table = select_feature_columns(enriched)
    write_parquet(feature_table, warehouse_dir / "ml_features.parquet")

    summary = {
        "record_count": int(len(feature_table)),
        "feature_columns": feature_table.columns.tolist(),
    }

    (warehouse_dir / "feature_summary.json").write_text(json.dumps(summary, indent=2))
    return summary


def parse_args(argv: Iterable[str] | None = None) -> Path:
    """Parse command line arguments."""
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--warehouse-dir",
        type=Path,
        default=None,
        help="Directory containing warehouse artifacts (defaults to warehouse/).",
    )
    args = parser.parse_args(args=argv)
    return args.warehouse_dir or Path(__file__).resolve().parents[1] / "warehouse"


def main(argv: Iterable[str] | None = None) -> None:
    """Run the CLI entry point."""
    warehouse_dir = parse_args(argv)
    summary = run_feature_engineering(warehouse_dir)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
