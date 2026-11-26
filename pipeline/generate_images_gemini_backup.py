"""Generate storyboard images using the Gemini image-generation API."""

import argparse
import base64
import json
import os
from pathlib import Path

from dotenv import load_dotenv
from google import genai


PROJECT_ROOT = Path(__file__).resolve().parent.parent
KEYFRAMES_FILE = PROJECT_ROOT / "keyframes.json"
STORYBOARD_FILE = PROJECT_ROOT / "storyboard.json"
OUTPUT_DIR = PROJECT_ROOT / "outputs" / "images"

MODEL_NAME = "gemini-3.1-flash-image"


def load_shot(shot_id: str) -> tuple[dict, str]:
    """Load a keyframe and the project's visual style."""
    with KEYFRAMES_FILE.open("r", encoding="utf-8") as file:
        keyframes = json.load(file)

    with STORYBOARD_FILE.open("r", encoding="utf-8") as file:
        storyboard = json.load(file)

    shot = next(
        (item for item in keyframes if item["shot_id"] == shot_id),
        None,
    )

    if shot is None:
        available = [item["shot_id"] for item in keyframes]
        raise ValueError(
            f"Shot '{shot_id}' not found. Available shots: {available}"
        )

    visual_style = storyboard["project"]["visual_style"]
    return shot, visual_style


def generate_image(
    shot_id: str,
    aspect_ratio: str = "16:9",
    overwrite: bool = False,
) -> Path:
    """Generate one image and save it locally."""
    load_dotenv(PROJECT_ROOT / ".env")

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key == "your_gemini_api_key_here":
        raise RuntimeError(
            "GEMINI_API_KEY is missing or still contains the placeholder. "
            "Check your local .env file."
        )

    shot, visual_style = load_shot(shot_id)

    prompt = (
        f"{visual_style}\n\n"
        f"Scene: {shot['image_prompt']}\n\n"
        "Create a realistic, culturally respectful cinematic documentary "
        "photograph. Preserve authentic Ethiopian coffee ceremony details. "
        "Avoid text, captions, logos, watermarks, and artificial-looking objects."
    )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    ratio_suffix = aspect_ratio.replace(":", "x")
    output_path = OUTPUT_DIR / f"{shot_id}_{ratio_suffix}.jpg"

    if output_path.exists() and not overwrite:
        print(f"Image already exists: {output_path}")
        print("Use --overwrite to generate it again.")
        return output_path

    client = genai.Client(api_key=api_key)

    try:
        print(f"Generating {shot_id} using {MODEL_NAME}...")
        print(f"Aspect ratio: {aspect_ratio}")

        interaction = client.interactions.create(
            model=MODEL_NAME,
            input=prompt,
            response_format=[
    {
        "type": "image",
        "mime_type": "image/jpeg",
        "aspect_ratio": aspect_ratio,
        "image_size": "1K",
    }
],
        )

        generated_image = interaction.output_image

        if generated_image is None or not generated_image.data:
            raise RuntimeError("Gemini returned no image data.")

        image_bytes = base64.b64decode(
            generated_image.data,
            validate=True,
        )

        if not image_bytes.startswith(b"\xff\xd8\xff"):
            raise RuntimeError("The returned image is not a valid JPEG.")

        output_path.write_bytes(image_bytes)

        print("Image generation: SUCCESS")
        print(f"Shot: {shot_id}")
        print(f"Saved to: {output_path}")
        print(f"File size: {len(image_bytes):,} bytes")

        return output_path

    finally:
        client.close()


def main():
    parser = argparse.ArgumentParser(
        description="Generate Ethiopian coffee ceremony storyboard images."
    )

    parser.add_argument(
        "--shot",
        default="shot_01",
        help="Storyboard shot ID (default: shot_01).",
    )

    parser.add_argument(
        "--aspect-ratio",
        choices=["9:16", "16:9"],
        default="16:9",
        help="Image aspect ratio.",
    )

    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Replace an existing generated image.",
    )

    args = parser.parse_args()

    generate_image(
        shot_id=args.shot,
        aspect_ratio=args.aspect_ratio,
        overwrite=args.overwrite,
    )


if __name__ == "__main__":
    main()

