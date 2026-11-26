
from pathlib import Path
import shutil
import subprocess
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
IMAGE_DIR = PROJECT_ROOT / "outputs" / "images"
VIDEO_DIR = PROJECT_ROOT / "outputs" / "videos"

SHOT_COUNT = 10
SHOT_DURATION = 7
TOTAL_DURATION = SHOT_COUNT * SHOT_DURATION
FPS = 30

FORMATS = {
    "16x9": (1280, 720),
    "9x16": (720, 1280),
}


def check_ffmpeg():
    """Confirm FFmpeg is installed and available."""
    if shutil.which("ffmpeg") is None:
        raise RuntimeError(
            "FFmpeg was not found. Restart VS Code and try again."
        )


def get_shot_images(aspect_ratio):
    """Find all 10 images for the requested aspect ratio."""
    images = []

    for number in range(1, SHOT_COUNT + 1):
        filename = f"shot_{number:02d}_{aspect_ratio}.jpg"
        image_path = IMAGE_DIR / filename

        if not image_path.exists():
            raise FileNotFoundError(
                f"Missing image: {image_path}"
            )

        images.append(image_path)

    return images


def create_concat_file(images, aspect_ratio):
    """Create an FFmpeg image-list file."""
    manifest = VIDEO_DIR / f"concat_{aspect_ratio}.txt"

    with manifest.open("w", encoding="utf-8") as file:
        for image_path in images:
            # FFmpeg concat files use forward slashes.
            image_name = image_path.resolve().as_posix()

            # Escape single quotes in file paths.
            image_name = image_name.replace("'", "'\\''")

            file.write(f"file '{image_name}'\n")
            file.write(f"duration {SHOT_DURATION}\n")

        # Repeat the final image so its duration is respected.
        final_image = images[-1].resolve().as_posix()
        final_image = final_image.replace("'", "'\\''")
        file.write(f"file '{final_image}'\n")

    return manifest


def assemble_video(aspect_ratio, resolution):
    """Assemble one MP4 video from the storyboard images."""
    width, height = resolution

    print(f"\nPreparing {aspect_ratio} video...")

    images = get_shot_images(aspect_ratio)
    manifest = create_concat_file(images, aspect_ratio)

    output_path = VIDEO_DIR / f"coffee_ceremony_{aspect_ratio}.mp4"

    video_filter = (
        f"scale={width}:{height}:force_original_aspect_ratio=decrease,"
        f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2,"
        f"setsar=1,fps={FPS},format=yuv420p"
    )

    command = [
        "ffmpeg",
        "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", str(manifest),
        "-vf", video_filter,
        "-t", str(TOTAL_DURATION),
        "-r", str(FPS),
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "23",
        "-movflags", "+faststart",
        str(output_path),
    ]

    print(f"Creating: {output_path.name}")

    subprocess.run(command, check=True)

    print(f"SUCCESS: {output_path}")
    print(f"Resolution: {width} x {height}")
    print(f"Planned duration: {TOTAL_DURATION} seconds")

    return output_path


def main():
    try:
        check_ffmpeg()
        VIDEO_DIR.mkdir(parents=True, exist_ok=True)

        for aspect_ratio, resolution in FORMATS.items():
            assemble_video(aspect_ratio, resolution)

        print("\nVIDEO ASSEMBLY COMPLETED SUCCESSFULLY.")
        print(f"Videos are saved in: {VIDEO_DIR}")

    except (FileNotFoundError, RuntimeError, subprocess.CalledProcessError) as error:
        print(f"\nERROR: {error}")
        sys.exit(1)


if __name__ == "__main__":
    main()
