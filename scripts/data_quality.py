"""Data quality checks for the integrated fabrication warehouse table."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Iterable, List

import duckdb
import pandas as pd

SOURCE_GROUPS: Dict[str, List[str]] = {
    "powermill": [
        "material",
        "tool_id",
        "feed_rate_mm_min",
        "stepover_mm",
        "path_length_mm",
        "volume_removed_cm3",
    ],
    "kuka": ["spindle_current_a", "torque_mean_nm", "duration_s", "energy_kwh"],
    "quality": ["surface_score", "defect_count"],
    "erp": ["tool_wear_cost_usd", "labor_hours", "revenue_usd"],
    "operator": ["stone_type", "operator_notes"],
}

VALID_TOOL_IDS = {
    "TOOL-ROUGH-20MM",
    "TOOL-ROUGH-16MM",
    "TOOL-FINISH-6MM",
    "TOOL-DETAIL-3MM",
    "TOOL-POLISH-8MM",
}

GREEN = "\033[92m"
RED = "\033[91m"
RESET = "\033[0m"
CHECK = "✓"
CROSS = "✗"


def load_integrated_table(parquet_path: Path) -> pd.DataFrame:
    """Load the integrated parquet file via DuckDB."""
    if not parquet_path.exists():
        raise FileNotFoundError(f"Integrated parquet file not found at {parquet_path}")
    query = duckdb.query(f"SELECT * FROM read_parquet('{parquet_path.as_posix()}')")
    return query.to_df()


def completeness_by_group(df: pd.DataFrame) -> Dict[str, float]:
    """Calculate completeness percentage for each source group."""
    completeness = {}
    for group, columns in SOURCE_GROUPS.items():
        available_cols = [col for col in columns if col in df.columns]
        if not available_cols:
            completeness[group] = 0.0
            continue
        completeness[group] = round(
            float(1 - df[available_cols].isna().mean().mean()) * 100, 2
        )
    return completeness


def critical_null_counts(df: pd.DataFrame) -> Dict[str, int]:
    """Count nulls in key business metrics."""
    critical_cols = ("duration_s", "surface_score", "revenue_usd")
    return {col: int(df[col].isna().sum()) for col in critical_cols if col in df.columns}


def carve_time_outliers(df: pd.DataFrame) -> Dict[str, object]:
    """Detect carve time outliers above three standard deviations."""
    duration = df["duration_s"].dropna()
    if duration.empty:
        return {"count": 0, "job_ids": []}
    threshold = duration.mean() + 3 * duration.std(ddof=0)
    mask = df["duration_s"] > threshold
    return {"count": int(mask.sum()), "job_ids": df.loc[mask, "job_id"].tolist()}


def validate_tool_catalog(df: pd.DataFrame) -> Dict[str, object]:
    """Ensure all tool IDs are part of the expected catalog."""
    if "tool_id" not in df.columns:
        return {"invalid_count": 0, "unknown_ids": []}
    invalid = df.loc[~df["tool_id"].isin(VALID_TOOL_IDS), "tool_id"]
    return {"invalid_count": int(invalid.size), "unknown_ids": sorted(set(invalid))}


def assemble_report(df: pd.DataFrame) -> Dict[str, object]:
    """Aggregate all quality metrics into a single structure."""
    return {
        "record_count": int(len(df)),
        "completeness_percent": completeness_by_group(df),
        "critical_nulls": critical_null_counts(df),
        "carve_time_outliers": carve_time_outliers(df),
        "tool_catalog_validation": validate_tool_catalog(df),
    }


def print_summary(report: Dict[str, object]) -> None:
    """Emit a colored console summary using simple checks."""
    completeness = report["completeness_percent"]
    critical_nulls = report["critical_nulls"]
    outliers = report["carve_time_outliers"]
    tools = report["tool_catalog_validation"]

    def emit(passed: bool, message: str) -> None:
        symbol = CHECK if passed else CROSS
        color = GREEN if passed else RED
        print(f"{color}{symbol} {message}{RESET}")

    emit(all(value >= 95 for value in completeness.values()), "Source completeness ≥ 95%")
    emit(all(count == 0 for count in critical_nulls.values()), "No nulls in critical metrics")
    emit(outliers["count"] == 0, "Duration outliers within 3σ threshold")
    emit(tools["invalid_count"] == 0, "Tool IDs match approved catalog")


def run_quality_checks(warehouse_dir: Path) -> Dict[str, object]:
    """Execute all quality checks and persist the report."""
    parquet_path = warehouse_dir / "jobs_integrated.parquet"
    df = load_integrated_table(parquet_path)
    report = assemble_report(df)

    output_path = warehouse_dir / "data_quality_report.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2))

    print_summary(report)
    return report


def parse_args(argv: Iterable[str] | None = None) -> Path:
    """Parse CLI arguments for the quality checker."""
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--warehouse-dir",
        type=Path,
        default=None,
        help="Directory containing warehouse outputs (defaults to warehouse/).",
    )
    args = parser.parse_args(args=argv)
    return args.warehouse_dir or Path(__file__).resolve().parents[1] / "warehouse"


def main(argv: Iterable[str] | None = None) -> None:
    """Run the command line interface."""
    warehouse_dir = parse_args(argv)
    report = run_quality_checks(warehouse_dir)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
