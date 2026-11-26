import json
from pathlib import Path
import jsonschema

ROOT = Path(__file__).resolve().parents[1]


def load_storyboard():
    return json.loads((ROOT / "storyboard.json").read_text(encoding="utf-8"))


def test_storyboard_matches_schema():
    storyboard = load_storyboard()
    schema = json.loads((ROOT / "schema" / "storyboard.schema.json").read_text(encoding="utf-8"))
    jsonschema.validate(instance=storyboard, schema=schema)


def test_shot_durations_match_target():
    storyboard = load_storyboard()
    total = sum(shot["duration_seconds"] for shot in storyboard["shots"])
    assert total == storyboard["project"]["target_duration_seconds"]


def test_storyboard_has_eight_to_twelve_shots():
    storyboard = load_storyboard()
    assert 8 <= len(storyboard["shots"]) <= 12


def test_shot_ids_are_unique():
    storyboard = load_storyboard()
    ids = [shot["id"] for shot in storyboard["shots"]]
    assert len(ids) == len(set(ids))
