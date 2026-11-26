import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
AUDIO_DIR = ROOT / "outputs" / "audio"
OUTPUT = AUDIO_DIR / "narration_70s.wav"

inputs = []
filters = []

for i in range(1, 11):
    path = AUDIO_DIR / f"shot_{i:02d}.wav"
    if not path.exists():
        raise FileNotFoundError(f"Missing narration: {path.name}")

    duration = float(subprocess.check_output([
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        str(path)
    ], text=True).strip())

    inputs.extend(["-i", str(path)])

    speed = duration / 6.95 if duration > 7 else 1.0
    speed_filter = f"atempo={speed:.6f}," if speed > 1 else ""

    filters.append(
        f"[{i-1}:a]{speed_filter}"
        f"apad=pad_dur=7,atrim=duration=7,"
        f"asetpts=PTS-STARTPTS[a{i-1}]"
    )

concat_inputs = "".join(f"[a{i}]" for i in range(10))
filters.append(f"{concat_inputs}concat=n=10:v=0:a=1[out]")

command = [
    "ffmpeg", "-y", *inputs,
    "-filter_complex", ";".join(filters),
    "-map", "[out]",
    "-ar", "24000", "-ac", "1",
    "-c:a", "pcm_s16le",
    str(OUTPUT)
]

subprocess.run(command, check=True)
print(f"\nSUCCESS: 70-second narration saved to {OUTPUT}")
