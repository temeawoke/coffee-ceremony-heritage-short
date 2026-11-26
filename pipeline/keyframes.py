
"""Generate keyframe metadata from the Ethiopian Coffee Ceremony storyboard."""

import json
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parent.parent
STORYBOARD_PATH = PROJECT_ROOT / "storyboard.json"
OUTPUT_PATH = PROJECT_ROOT / "keyframes.json"


def load_storyboard(path: Path = STORYBOARD_PATH) -> dict[str, Any]:
    """Load the storyboard JSON file."""
    if not path.exists():
        raise FileNotFoundError(f"Storyboard not found: {path}")

    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def generate_keyframes(storyboard: dict[str, Any]) -> list[dict[str, Any]]:
    """Generate keyframe metadata for every storyboard shot."""
    shots = storyboard.get("shots", [])

    if not shots:
        raise ValueError("The storyboard contains no shots.")

    keyframes = []
    current_time = 0

    for shot in shots:
        duration = shot.get("duration_seconds")

        if not isinstance(duration, (int, float)) or duration <= 0:
            raise ValueError(
                f"Invalid duration for shot: {shot.get('id', 'unknown')}"
            )

        start_time = current_time
        end_time = start_time + duration

        keyframe = {
            "shot_id": shot["id"],
            "start_time_seconds": start_time,
            "end_time_seconds": end_time,
            "duration_seconds": duration,
            "visual_description": shot.get("visual_description", ""),
            "image_prompt": shot.get("image_prompt", ""),
            "motion_prompt": shot.get("motion_prompt", ""),
            "narration_am": shot.get("narration_am", ""),
            "subtitle_en": shot.get("subtitle_en", ""),
            "music_cue": shot.get("music_cue", ""),
        }

        keyframes.append(keyframe)
        current_time = end_time

    return keyframes


def save_keyframes(
    keyframes: list[dict[str, Any]],
    output_path: Path = OUTPUT_PATH,
) -> None:
    """Save generated keyframes to a JSON file."""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8") as file:
        json.dump(
            keyframes,
            file,
            indent=2,
            ensure_ascii=False,
        )

    print(f"Keyframes saved to: {output_path}")


def main() -> None:
    """Run the keyframe generation process."""
    storyboard = load_storyboard()
    keyframes = generate_keyframes(storyboard)
    save_keyframes(keyframes)

    total_duration = sum(
        frame["duration_seconds"] for frame in keyframes
    )

    print("\nKeyframe generation: SUCCESS")
    print(f"Total shots: {len(keyframes)}")
    print(f"Total duration: {total_duration} seconds")


if __name__ == "__main__":
    main()
