"""Minimal ML feature store API for serving engineered fabrication metrics."""

from __future__ import annotations

from typing import Any, Dict, List

from flask import Flask, abort, jsonify, request

from app import utils

app = Flask(__name__)


def _normalize_material(value: str | None) -> str | None:
    return value.lower() if value else None


def _serialize_records(records) -> List[Dict[str, Any]]:
    return records.to_dict(orient="records")


@app.route("/features", methods=["GET"])
def features_endpoint():
    """Fetch engineered features filtered by job or material."""
    features = utils.load_feature_table()
    job_id = request.args.get("job_id")
    material = _normalize_material(request.args.get("material"))
    limit = request.args.get("limit", default="20")

    try:
        limit_value = max(1, min(int(limit), 100))
    except ValueError:
        abort(400, description="limit must be an integer between 1 and 100")

    if job_id:
        match = features[features["job_id"] == job_id]
        if match.empty:
            abort(404, description=f"No feature rows found for job_id={job_id}")
        return jsonify(_serialize_records(match))

    filtered = features.copy()
    if material:
        filtered = filtered[
            (filtered["material"].str.lower() == material)
            | (filtered["stone_type"].str.lower() == material)
        ]

    return jsonify(_serialize_records(filtered.head(limit_value)))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
