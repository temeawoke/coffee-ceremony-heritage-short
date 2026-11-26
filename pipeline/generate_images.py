
"""Generate Ethiopian coffee ceremony images using Cloudflare FLUX.1 schnell."""

import argparse
import base64
import json
import os
import urllib.error
import urllib.request
from io import BytesIO
from pathlib import Path

from dotenv import load_dotenv
from PIL import Image, ImageFilter, ImageOps


PROJECT_ROOT = Path(__file__).resolve().parent.parent
KEYFRAMES_FILE = PROJECT_ROOT / "keyframes.json"
STORYBOARD_FILE = PROJECT_ROOT / "storyboard.json"
OUTPUT_DIR = PROJECT_ROOT / "outputs" / "images"

MODEL_NAME = "@cf/black-forest-labs/flux-1-schnell"
API_URL = "https://api.cloudflare.com/client/v4/accounts/{}/ai/run/{}"

ASPECT_SIZES = {
    "16:9": (1280, 720),
    "9:16": (720, 1280),
}


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


def generate_source_image(prompt: str) -> bytes:
    """Request one original image from Cloudflare Workers AI."""

    load_dotenv(PROJECT_ROOT / ".env")

    token = os.getenv("CLOUDFLARE_API_TOKEN")
    account_id = os.getenv("CLOUDFLARE_ACCOUNT_ID")

    if not token or token == "your_cloudflare_api_token_here":
        raise RuntimeError("CLOUDFLARE_API_TOKEN is missing.")

    if not account_id or account_id == "your_cloudflare_account_id_here":
        raise RuntimeError("CLOUDFLARE_ACCOUNT_ID is missing.")

    url = API_URL.format(account_id, MODEL_NAME)

    payload = {
        "prompt": prompt,
        "steps": 4,
    }

    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=180) as response:
            content = response.read()
            content_type = response.headers.get("Content-Type", "")

            if content_type.startswith("image/"):
                image_bytes = content
            else:
                data = json.loads(content.decode("utf-8"))

                if not data.get("success", False):
                    raise RuntimeError(
                        f"Cloudflare API error: {data.get('errors')}"
                    )

                encoded_image = data.get("result", {}).get("image")

                if not encoded_image:
                    raise RuntimeError(
                        "Cloudflare returned no image data."
                    )

                image_bytes = base64.b64decode(
                    encoded_image,
                    validate=True,
                )

    except urllib.error.HTTPError as error:
        details = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(
            f"Cloudflare HTTP error {error.code}: {details[:1000]}"
        ) from error

    if not image_bytes.startswith(b"\xff\xd8\xff"):
        raise RuntimeError("Cloudflare did not return a valid JPEG.")

    return image_bytes


def create_aspect_variant(
    source_bytes: bytes,
    aspect_ratio: str,
    output_path: Path,
) -> Path:
    """Create a landscape or portrait version without cropping the subject."""

    target_width, target_height = ASPECT_SIZES[aspect_ratio]

    with Image.open(BytesIO(source_bytes)) as original:
        original = original.convert("RGB")

        # Create a full-size blurred background.
        background = ImageOps.fit(
            original,
            (target_width, target_height),
            method=Image.Resampling.LANCZOS,
        )
        background = background.filter(ImageFilter.GaussianBlur(radius=30))

        # Fit the complete original image inside the target frame.
        foreground = original.copy()
        foreground.thumbnail(
            (int(target_width * 0.94), int(target_height * 0.94)),
            Image.Resampling.LANCZOS,
        )

        x = (target_width - foreground.width) // 2
        y = (target_height - foreground.height) // 2

        background.paste(foreground, (x, y))
        background.save(
            output_path,
            format="JPEG",
            quality=92,
            optimize=True,
        )

    return output_path


def generate_image(
    shot_id: str,
    aspect_ratio: str = "16:9",
    overwrite: bool = False,
):
    """Generate one source image and create the requested output versions."""

    shot, visual_style = load_shot(shot_id)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    source_path = OUTPUT_DIR / f"{shot_id}_source.jpg"

    ratios = (
        list(ASPECT_SIZES)
        if aspect_ratio == "both"
        else [aspect_ratio]
    )

    output_paths = [
        OUTPUT_DIR / f"{shot_id}_{ratio.replace(':', 'x')}.jpg"
        for ratio in ratios
    ]

    if not overwrite and all(path.exists() for path in output_paths):
        print(f"Requested images already exist for {shot_id}.")
        return output_paths

    if source_path.exists() and not overwrite:
        print(f"Reusing existing source image: {source_path}")
        source_bytes = source_path.read_bytes()
    else:
        prompt = (
            f"{visual_style}\n\n"
            f"Scene: {shot['image_prompt']}\n\n"
            "Create a realistic, culturally respectful cinematic "
            "documentary photograph. Preserve authentic Ethiopian "
            "coffee ceremony details. Avoid text, captions, logos, "
            "watermarks, and artificial-looking objects."
        )

        print(f"Generating {shot_id} using {MODEL_NAME}...")
        source_bytes = generate_source_image(prompt)
        source_path.write_bytes(source_bytes)

        print(f"Original image saved: {source_path}")

    generated_paths = []

    for ratio, output_path in zip(ratios, output_paths):
        if output_path.exists() and not overwrite:
            print(f"Already exists: {output_path}")
            generated_paths.append(output_path)
            continue

        create_aspect_variant(source_bytes, ratio, output_path)

        print(f"Created {ratio}: {output_path}")
        print(f"File size: {output_path.stat().st_size:,} bytes")

        generated_paths.append(output_path)

    print(f"Image generation: SUCCESS ({shot_id})")

    return generated_paths


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
        choices=["9:16", "16:9", "both"],
        default="16:9",
        help="Output image format.",
    )

    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Regenerate the original image and replace existing outputs.",
    )

    args = parser.parse_args()

    generate_image(
        shot_id=args.shot,
        aspect_ratio=args.aspect_ratio,
        overwrite=args.overwrite,
    )


if __name__ == "__main__":
    main()
