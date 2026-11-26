"""Create an audio-first radio cut: black video + Amharic narration + quiet placeholder music.

Prerequisite: outputs/audio/narration.wav (generated in the TTS stage).
This script assembles supplied speech; it does not generate speech.
"""
from __future__ import annotations
import argparse
import json
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def main() -> None:
    parser = argparse.ArgumentParser(description="Build the black-screen radio cut.")
    parser.add_argument("--narration", default="outputs/audio/narration.wav")
    parser.add_argument("--output", default="outputs/final/radio_cut_vertical.mp4")
    args = parser.parse_args()

    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise SystemExit("FFmpeg not found. Install FFmpeg, add its bin folder to PATH, then reopen the terminal.")

    storyboard = json.loads((ROOT / "storyboard.json").read_text(encoding="utf-8"))
    duration = int(storyboard["project"]["target_duration_seconds"])
    narration = (ROOT / args.narration).resolve()
    output = (ROOT / args.output).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)

    if not narration.exists():
        raise SystemExit(
            f"Narration audio not found: {narration}\\n"
            "Generate the Amharic narration WAV in the TTS stage and save it as "
            "outputs/audio/narration.wav."
        )

    music = (
        "aevalsrc=0.012*sin(2*PI*220*t)+0.009*sin(2*PI*277.18*t)"
        "+0.007*sin(2*PI*329.63*t):s=48000:d=" + str(duration)
    )
    command = [
        ffmpeg, "-y",
        "-f", "lavfi", "-i", f"color=c=black:s=1080x1920:r=24:d={duration}",
        "-i", str(narration),
        "-f", "lavfi", "-i", music,
        "-filter_complex",
        (
            f"[1:a]aresample=48000,apad,atrim=0:{duration},volume=1.0[voice];"
            f"[2:a]afade=t=in:st=0:d=2,afade=t=out:st={max(0, duration-3)}:d=3,"
            "volume=0.35[music];"
            "[voice][music]amix=inputs=2:duration=longest:dropout_transition=0,"
            "alimiter=limit=0.95[a]"
        ),
        "-map", "0:v:0", "-map", "[a]", "-t", str(duration),
        "-c:v", "libx264", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart",
        str(output),
    ]
    print(f"Building {duration}-second radio cut...")
    subprocess.run(command, check=True)
    print(f"Radio cut created: {output}")
    print("Listen to the complete recording before audience testing.")

if __name__ == "__main__":
    main()
