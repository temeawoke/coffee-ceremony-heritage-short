import re
from pathlib import Path
import torch
import soundfile as sf
from omnivoice import OmniVoice, OmniVoiceGenerationConfig

PROJECT_DIR = Path(__file__).resolve().parent.parent
SCRIPT_FILE = PROJECT_DIR / "narration_script_am.txt"
OUTPUT_DIR = PROJECT_DIR / "outputs" / "audio"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

lines = [
    re.sub(r"^\d+\.\s*", "", line.strip())
    for line in SCRIPT_FILE.read_text(encoding="utf-8").splitlines()
    if line.strip()
]

if len(lines) != 10:
    raise ValueError(f"Expected 10 narration lines, found {len(lines)}")

print("Loading Amharic model...")
model = OmniVoice.from_pretrained(
    "african-low-resource/omnivoice-amharic",
    device_map="cuda:0",
    dtype=torch.float16,
)

config = OmniVoiceGenerationConfig(num_step=32, guidance_scale=2.0)

for index, text in enumerate(lines, start=1):
    print(f"Generating narration {index}/10...")
    audio = model.generate(
        text=text,
        language="Amharic",
        generation_config=config,
    )
    output_file = OUTPUT_DIR / f"shot_{index:02d}.wav"
    sf.write(str(output_file), audio[0], 24000)
    print(f"Saved: {output_file.name}")

    del audio
    torch.cuda.empty_cache()

print("SUCCESS: All 10 narration clips generated.")
