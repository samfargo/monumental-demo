"""Utility helpers for the Streamlit dashboard and ancillary services."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Dict

import duckdb
import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[1]
WAREHOUSE_DIR = BASE_DIR / "warehouse"


def _validate_path(path: Path) -> Path:
    if not path.exists():
        raise FileNotFoundError(f"Expected file not found: {path}")
    return path


def _read_parquet(path: Path) -> pd.DataFrame:
    """Read a parquet file via DuckDB to avoid optional dependencies."""
    query = duckdb.query(f"SELECT * FROM read_parquet('{_validate_path(path).as_posix()}')")
    return query.to_df()


@lru_cache(maxsize=1)
def load_jobs_integrated() -> pd.DataFrame:
    """Load the integrated job table."""
    return _read_parquet(WAREHOUSE_DIR / "jobs_integrated.parquet")


@lru_cache(maxsize=1)
def load_feature_table() -> pd.DataFrame:
    """Load engineered feature table."""
    return _read_parquet(WAREHOUSE_DIR / "ml_features.parquet")


@lru_cache(maxsize=1)
def load_quality_report() -> Dict[str, object]:
    """Load the persisted data quality report."""
    report_path = _validate_path(WAREHOUSE_DIR / "data_quality_report.json")
    return json.loads(report_path.read_text())


def stone_hardness_scale(stone_type: str) -> int:
    """Map stone type to an approximate Mohs hardness indicator for visuals."""
    scale = {"limestone": 3, "marble": 4, "granite": 6}
    return scale.get(stone_type.lower(), 0)
