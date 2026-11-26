"""Orchestrate the heritage-short pipeline without pretending missing providers exist.

Usage:
  python -m pipeline.run --plan
  python -m pipeline.run --stage validate
  python -m pipeline.run --stage radio-cut

Media stages become executable as their provider adapters are implemented.
"""
from __future__ import annotations

import argparse
import json
import logging
import subprocess
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

ROOT = Path(__file__).resolve().parents[1]
LOG_DIR = ROOT / "logs"
RUN_LOG = LOG_DIR / "runs.jsonl"

@dataclass
class Stage:
    name: str
    description: str
    status: str
    command: list[str] | None = None

STAGES = [
    Stage("validate", "Validate storyboard structure and shot timing", "available",
          [sys.executable, "-m", "pipeline.validate_storyboard"]),
    Stage(
    "keyframes",
    "Generate visual keyframes from image prompts",
    "available",
    [sys.executable, "-m", "pipeline.keyframes"],
),
    Stage("shots", "Generate moving video shots from keyframes", "not_implemented"),
    Stage("music", "Generate the original background score", "not_implemented"),
    Stage("narration", "Generate Amharic narration and subtitle assets", "not_implemented"),
    Stage("assemble", "Assemble and export vertical and horizontal films", "not_implemented"),
]


def configure_logging() -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        handlers=[logging.StreamHandler(sys.stdout),
                  logging.FileHandler(LOG_DIR / "pipeline.log", encoding="utf-8")],
    )


def record_event(event: dict) -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    with RUN_LOG.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, ensure_ascii=False) + "\\n")


def run_stage(stage: Stage) -> int:
    started = datetime.now(timezone.utc)
    event = {
        "event_type": "pipeline_stage",
        "stage": stage.name,
        "description": stage.description,
        "status": "started",
        "started_at": started.isoformat(),
    }
    record_event(event)
    logging.info("Starting stage: %s — %s", stage.name, stage.description)

    if stage.status != "available" or not stage.command:
        logging.warning("Stage '%s' is not implemented yet; no generation was attempted.", stage.name)
        record_event({**event, "status": "not_implemented",
                      "finished_at": datetime.now(timezone.utc).isoformat()})
        return 2

    try:
        subprocess.run(stage.command, cwd=ROOT, check=True)
    except subprocess.CalledProcessError as exc:
        logging.exception("Stage '%s' failed with exit code %s", stage.name, exc.returncode)
        record_event({**event, "status": "failed", "exit_code": exc.returncode,
                      "finished_at": datetime.now(timezone.utc).isoformat()})
        return exc.returncode or 1

    finished = datetime.now(timezone.utc)
    record_event({**event, "status": "success", "finished_at": finished.isoformat(),
                  "duration_seconds": round((finished - started).total_seconds(), 3)})
    logging.info("Completed stage: %s", stage.name)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the Ethiopian Coffee Ceremony production pipeline")
    parser.add_argument("--plan", action="store_true", help="Show stage plan without running generation")
    parser.add_argument("--stage", choices=[s.name for s in STAGES], help="Run one named stage")
    args = parser.parse_args()
    configure_logging()

    selected = [next(s for s in STAGES if s.name == args.stage)] if args.stage else STAGES
    if args.plan:
        print("\\nPIPELINE EXECUTION PLAN")
        for index, stage in enumerate(selected, 1):
            print(f"{index}. {stage.name:10} [{stage.status}] - {stage.description}")
        print("\\nOnly stages marked 'available' can currently execute.")
        return 0

    failures = []
    for stage in selected:
        code = run_stage(stage)
        if code:
            failures.append((stage.name, code))
            if args.stage:
                break

    if failures:
        logging.error("Pipeline stopped or has pending stages: %s", failures)
        return 1
    logging.info("Selected pipeline stages completed successfully.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
