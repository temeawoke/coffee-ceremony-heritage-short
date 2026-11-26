import json
from pathlib import Path
from jsonschema import validate
from jsonschema.exceptions import ValidationError

ROOT = Path(__file__).resolve().parents[1]
STORYBOARD_PATH = ROOT / "storyboard.json"
SCHEMA_PATH = ROOT / "schema" / "storyboard.schema.json"

def main():
    with STORYBOARD_PATH.open("r", encoding="utf-8") as f:
        storyboard = json.load(f)
    with SCHEMA_PATH.open("r", encoding="utf-8") as f:
        schema = json.load(f)

    validate(instance=storyboard, schema=schema)

    shot_count = len(storyboard["shots"])
    total_seconds = sum(s["duration_seconds"] for s in storyboard["shots"])
    print("Storyboard validation: SUCCESS")
    print(f"Project: {storyboard['project']['title']}")
    print(f"Shots: {shot_count}")
    print(f"Planned duration: {total_seconds} seconds")
    print(f"Target duration: {storyboard['project']['target_duration_seconds']} seconds")

    if total_seconds != storyboard["project"]["target_duration_seconds"]:
        raise SystemExit("ERROR: Sum of shot durations does not match target duration.")

if __name__ == "__main__":
    try:
        main()
    except (ValidationError, json.JSONDecodeError, FileNotFoundError) as exc:
        raise SystemExit(f"Storyboard validation failed: {exc}")
