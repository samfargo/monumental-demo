"""Simple MQTT telemetry simulator for the Monumental Labs demo."""

from __future__ import annotations

import argparse
import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Iterator

import numpy as np
import pandas as pd

try:
    import paho.mqtt.client as mqtt
except ImportError as exc:  # pragma: no cover - handled in README
    raise SystemExit(
        "paho-mqtt is required. Install with `pip install paho-mqtt`."
    ) from exc


DATA_DIR = Path(__file__).resolve().parents[1] / "data"
DEFAULT_TOPIC = "monumental/telemetry"


def generate_stream(interval: float = 0.5) -> Iterator[dict]:
    rng = np.random.default_rng(1234)
    telemetry = pd.read_csv(DATA_DIR / "telemetry.csv")
    toolpaths = pd.read_csv(DATA_DIR / "toolpaths.csv").set_index("toolpath_id")
    jobs = pd.read_csv(DATA_DIR / "jobs.csv").set_index("job_id")

    base_time = datetime.utcnow()
    for _, row in telemetry.iterrows():
        job_id = toolpaths.loc[row["toolpath_id"], "job_id"]
        material = jobs.loc[job_id, "material"]
        payload = {
            "timestamp": (
                base_time + timedelta(seconds=float(row.name) * interval)
            ).isoformat(),
            "job_id": job_id,
            "toolpath_id": row["toolpath_id"],
            "material": material,
            "spindle_current_a": round(
                float(row["spindle_current_a"]) * rng.uniform(0.97, 1.05), 2
            ),
            "vibration_g": round(
                float(row["vibration_g"]) * rng.uniform(0.95, 1.08), 3
            ),
            "coolant_flow_lpm": round(
                float(row["coolant_flow_lpm"]) * rng.uniform(0.9, 1.05), 2
            ),
        }
        yield payload
        time.sleep(interval)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Publish synthetic robot telemetry to an MQTT broker."
    )
    parser.add_argument("--host", default="localhost", help="MQTT broker host")
    parser.add_argument("--port", type=int, default=1883, help="MQTT broker port")
    parser.add_argument("--topic", default=DEFAULT_TOPIC, help="MQTT topic name")
    parser.add_argument(
        "--interval",
        type=float,
        default=0.5,
        help="Seconds between messages (default 0.5s)",
    )
    args = parser.parse_args()

    client = mqtt.Client()
    client.connect(args.host, args.port, keepalive=60)
    client.loop_start()
    print(
        f"Streaming telemetry to mqtt://{args.host}:{args.port}/{args.topic} "
        f"every {args.interval:.2f}s. Press Ctrl+C to stop."
    )

    try:
        for message in generate_stream(interval=args.interval):
            client.publish(args.topic, json.dumps(message), qos=0)
    except KeyboardInterrupt:
        pass
    finally:
        client.loop_stop()
        client.disconnect()
        print("Stopped MQTT simulator.")


if __name__ == "__main__":
    main()
