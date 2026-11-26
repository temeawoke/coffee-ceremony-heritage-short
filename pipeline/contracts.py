"""Shared paths and storyboard loading helpers for pipeline stages."""
from __future__ import annotations
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
STORYBOARD_PATH = ROOT / "storyboard.json"
OUTPUTS_DIR = ROOT / "outputs"


def load_storyboard() -> dict[str, Any]:
    """Load the project's central storyboard JSON."""
    with STORYBOARD_PATH.open("r", encoding="utf-8") as file:
        return json.load(file)


def shot_output_path(folder: str, shot_id: str, suffix: str) -> Path:
    """Return a safe, project-relative output path for a shot artifact."""
    if not shot_id.startswith("shot_") or not shot_id[5:].isdigit():
        raise ValueError(f"Invalid shot id: {shot_id!r}")
    if not folder.replace("_", "").isalnum():
        raise ValueError(f"Invalid output folder: {folder!r}")
    if not suffix.startswith(".") or "/" in suffix or "\\\\" in suffix:
        raise ValueError(f"Invalid file suffix: {suffix!r}")
    target_dir = OUTPUTS_DIR / folder
    target_dir.mkdir(parents=True, exist_ok=True)
    return target_dir / f"{shot_id}{suffix}"
