"""Generate synthetic fabrication datasets for the Monumental demo."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Dict, Iterable

import numpy as np
import pandas as pd
from faker import Faker


STONE_PROFILES: Dict[str, Dict[str, float]] = {
    "granite": {
        "feed_rate_mean": 880,
        "feed_rate_sd": 90,
        "feed_rate_low": 520,
        "feed_rate_high": 1350,
        "stepover_mean": 2.2,
        "stepover_sd": 0.6,
        "path_length_mean": 28000,
        "path_length_sd": 6200,
        "volume_mean": 15200,
        "volume_sd": 3100,
        "duration_bias": 1.25,
        "current_mean": 27.5,
        "current_sd": 3.4,
        "torque_mean": 148,
        "torque_sd": 18,
        "power_factor": 0.42,
        "quality_mean": 85,
        "defect_lambda": 1.8,
        "cost_per_cm3": 0.29,
        "labor_base": 8.0,
    },
    "marble": {
        "feed_rate_mean": 1180,
        "feed_rate_sd": 120,
        "feed_rate_low": 720,
        "feed_rate_high": 1650,
        "stepover_mean": 3.1,
        "stepover_sd": 0.7,
        "path_length_mean": 24500,
        "path_length_sd": 5400,
        "volume_mean": 13800,
        "volume_sd": 2800,
        "duration_bias": 1.12,
        "current_mean": 22.5,
        "current_sd": 2.6,
        "torque_mean": 122,
        "torque_sd": 16,
        "power_factor": 0.36,
        "quality_mean": 88,
        "defect_lambda": 1.2,
        "cost_per_cm3": 0.24,
        "labor_base": 7.0,
    },
    "limestone": {
        "feed_rate_mean": 1350,
        "feed_rate_sd": 130,
        "feed_rate_low": 820,
        "feed_rate_high": 1850,
        "stepover_mean": 3.6,
        "stepover_sd": 0.8,
        "path_length_mean": 21600,
        "path_length_sd": 4800,
        "volume_mean": 12400,
        "volume_sd": 2500,
        "duration_bias": 1.05,
        "current_mean": 18.8,
        "current_sd": 2.2,
        "torque_mean": 94,
        "torque_sd": 14,
        "power_factor": 0.31,
        "quality_mean": 91,
        "defect_lambda": 0.8,
        "cost_per_cm3": 0.19,
        "labor_base": 6.5,
    },
}

TOOL_IDS = (
    "TOOL-ROUGH-20MM",
    "TOOL-ROUGH-16MM",
    "TOOL-FINISH-6MM",
    "TOOL-DETAIL-3MM",
    "TOOL-POLISH-8MM",
)


def build_job_index(job_count: int, rng: np.random.Generator) -> pd.DataFrame:
    """Create the canonical list of jobs that other datasets reference."""
    stone_choices = list(STONE_PROFILES.keys())
    complexity = rng.uniform(0.6, 1.4, size=job_count)
    schedule_offset = rng.integers(0, 14, size=job_count)
    jobs = []

    for idx in range(job_count):
        stone_type = rng.choice(stone_choices)
        hardness_factor = STONE_PROFILES[stone_type]["duration_bias"]
        jobs.append(
            {
                "job_id": f"J{idx+1:03d}",
                "stone_type": stone_type,
                "material": stone_type.title(),
                "complexity_index": round(complexity[idx], 3),
                "scheduled_day": int(schedule_offset[idx]),
                "hardness_factor": hardness_factor,
            }
        )

    return pd.DataFrame(jobs)


def generate_powermill(job_index: pd.DataFrame, rng: np.random.Generator) -> pd.DataFrame:
    """Construct synthetic CAM toolpath metrics for each job."""
    records = []
    for row in job_index.itertuples(index=False):
        profile = STONE_PROFILES[row.stone_type]
        feed_rate = np.clip(
            rng.normal(profile["feed_rate_mean"], profile["feed_rate_sd"]),
            profile["feed_rate_low"],
            profile["feed_rate_high"],
        )
        stepover = np.clip(
            rng.normal(profile["stepover_mean"], profile["stepover_sd"]),
            0.8,
            6.5,
        )
        path_length = np.clip(
            rng.normal(profile["path_length_mean"] * row.complexity_index, profile["path_length_sd"]),
            4800,
            62000,
        )
        volume_removed = np.clip(
            rng.normal(profile["volume_mean"] * row.complexity_index, profile["volume_sd"]),
            3200,
            26000,
        )
        simulated_minutes = max(path_length / feed_rate * rng.uniform(0.95, 1.35), 12.0)

        records.append(
            {
                "job_id": row.job_id,
                "material": row.material,
                "tool_id": rng.choice(TOOL_IDS),
                "feed_rate_mm_min": round(feed_rate, 1),
                "stepover_mm": round(stepover, 2),
                "path_length_mm": round(path_length, 1),
                "volume_removed_cm3": round(volume_removed, 1),
                "simulation_time_min": round(simulated_minutes, 2),
            }
        )

    return pd.DataFrame.from_records(records)


def generate_kuka(
    job_index: pd.DataFrame, powermill: pd.DataFrame, rng: np.random.Generator
) -> pd.DataFrame:
    """Create summarized robot telemetry influenced by CAM settings."""
    job_lookup = job_index.set_index("job_id")
    records = []

    for row in powermill.itertuples(index=False):
        job_profile = job_lookup.loc[row.job_id]
        stone_profile = STONE_PROFILES[job_profile["stone_type"]]
        complexity = float(job_profile["complexity_index"])
        complexity_scale = 1 + (complexity - 1) * 0.65

        theoretical_minutes = row.path_length_mm / row.feed_rate_mm_min
        duration_seconds = np.clip(
            theoretical_minutes * 60 * stone_profile["duration_bias"] * rng.uniform(0.92, 1.15)
            + rng.uniform(120, 420),
            600,
            7200,
        )

        spindle_current = np.clip(
            rng.normal(stone_profile["current_mean"], stone_profile["current_sd"])
            * complexity_scale,
            9.0,
            36.0,
        )
        torque_mean = np.clip(
            rng.normal(stone_profile["torque_mean"], stone_profile["torque_sd"])
            * complexity_scale,
            28.0,
            220.0,
        )
        energy_kwh = (
            duration_seconds / 3600
            * spindle_current
            * stone_profile["power_factor"]
            * rng.uniform(0.82, 1.18)
        )

        records.append(
            {
                "job_id": row.job_id,
                "spindle_current_a": round(spindle_current, 2),
                "torque_mean_nm": round(torque_mean, 1),
                "duration_s": round(duration_seconds, 1),
                "energy_kwh": round(energy_kwh, 3),
            }
        )

    return pd.DataFrame.from_records(records)


def generate_quality(job_index: pd.DataFrame, rng: np.random.Generator) -> pd.DataFrame:
    """Simulate QC inspection results per job."""
    job_lookup = job_index.set_index("job_id")
    scores = []
    for job_id, job in job_lookup.iterrows():
        profile = STONE_PROFILES[job.stone_type]
        base_score = rng.normal(profile["quality_mean"], 6.0)
        hit_by_complexity = base_score - job.complexity_index * rng.uniform(5.0, 10.0)
        surface_score = float(np.clip(hit_by_complexity, 62.0, 98.5))
        defect_lambda = max(profile["defect_lambda"] * job.complexity_index, 0.2)
        defect_count = int(rng.poisson(defect_lambda))
        scores.append(
            {
                "job_id": job_id,
                "surface_score": round(surface_score, 1),
                "defect_count": defect_count,
            }
        )

    return pd.DataFrame(scores)


def generate_costs(
    job_index: pd.DataFrame, powermill: pd.DataFrame, rng: np.random.Generator
) -> pd.DataFrame:
    """Craft ERP-like cost records for each job."""
    job_lookup = job_index.set_index("job_id")
    volume_lookup = powermill.set_index("job_id")["volume_removed_cm3"]
    records = []

    for job_id, job in job_lookup.iterrows():
        profile = STONE_PROFILES[job.stone_type]
        volume = float(volume_lookup.loc[job_id])
        tool_wear_cost = np.clip(
            volume * profile["cost_per_cm3"] * rng.uniform(0.85, 1.25),
            65.0,
            525.0,
        )
        labor_hours = np.clip(
            profile["labor_base"] * job.complexity_index * rng.uniform(0.9, 1.25)
            + rng.uniform(0.5, 1.5),
            3.5,
            16.0,
        )
        revenue = volume * rng.uniform(0.38, 0.6) + labor_hours * rng.uniform(65, 120)

        records.append(
            {
                "job_id": job_id,
                "tool_wear_cost_usd": round(tool_wear_cost, 2),
                "labor_hours": round(labor_hours, 2),
                "revenue_usd": round(revenue, 2),
            }
        )

    return pd.DataFrame(records)


def generate_operator_logs(
    job_index: pd.DataFrame, fake: Faker, rng: np.random.Generator
) -> pd.DataFrame:
    """Assemble human-readable operator notes per job."""
    mood = ("smooth pass", "minor chatter", "tool swap required", "rework requested", "on schedule")
    notes = []
    for row in job_index.itertuples(index=False):
        anecdote = fake.sentence(nb_words=12)
        qualifier = rng.choice(mood)
        notes.append(
            {
                "job_id": row.job_id,
                "stone_type": row.stone_type,
                "operator_notes": f"{qualifier}; {anecdote}",
            }
        )

    return pd.DataFrame(notes)


def write_csv(path: Path, frame: pd.DataFrame) -> None:
    """Persist a dataframe to CSV with common settings."""
    frame.to_csv(path, index=False)


def run_pipeline(job_count: int, output_dir: Path) -> Dict[str, int]:
    """Execute the data generation workflow."""
    rng = np.random.default_rng(seed=2024)
    fake = Faker()
    fake.seed_instance(2024)

    job_index = build_job_index(job_count, rng)
    powermill = generate_powermill(job_index, rng)
    kuka = generate_kuka(job_index, powermill, rng)
    quality = generate_quality(job_index, rng)
    costs = generate_costs(job_index, powermill, rng)
    operator_log = generate_operator_logs(job_index, fake, rng)

    output_dir.mkdir(parents=True, exist_ok=True)

    write_csv(output_dir / "powermill_toolpaths.csv", powermill)
    write_csv(output_dir / "kuka_telemetry.csv", kuka)
    write_csv(output_dir / "quality_inspection.csv", quality)
    write_csv(output_dir / "erp_costs.csv", costs)
    write_csv(output_dir / "operator_log.csv", operator_log)

    return {
        "powermill_toolpaths.csv": len(powermill),
        "kuka_telemetry.csv": len(kuka),
        "quality_inspection.csv": len(quality),
        "erp_costs.csv": len(costs),
        "operator_log.csv": len(operator_log),
    }


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    """Parse CLI arguments for the generator script."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--jobs",
        type=int,
        default=75,
        help="Number of unique jobs to generate (50-100 keeps the demo tidy).",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=None,
        help="Optional output directory for CSVs (defaults to repository data/).",
    )
    return parser.parse_args(args=argv)


def main(argv: Iterable[str] | None = None) -> None:
    """Entry point used by the task runner or CLI."""
    args = parse_args(argv)
    if args.jobs < 50 or args.jobs > 200:
        raise ValueError("jobs must be between 50 and 200 for this demonstration.")

    base_output = (
        Path(args.output_dir).expanduser()
        if args.output_dir
        else Path(__file__).resolve().parents[1] / "data"
    )

    results = run_pipeline(args.jobs, base_output)
    summary = ", ".join(f"{name}: {count}" for name, count in results.items())
    print(f"Synthetic datasets generated in {base_output.resolve()} -> {summary}")


if __name__ == "__main__":
    main()
