# The Ethiopian Coffee Ceremony — AI Heritage Short

A reproducible Python pipeline for creating a 60–90 second short film about the Ethiopian coffee ceremony, narrated in Amharic with English subtitles.

## Current status

The starter project includes:
- A 10-shot storyboard in Amharic and English.
- JSON Schema validation.
- A Python project runner.
- Output folders for images, videos, audio, subtitles and final exports.

Image, video, music and TTS provider integrations are intentionally not connected yet.

## Requirements

- Python 3.10 or newer
- Windows 10/11
- VS Code
- PowerShell

## Setup (PowerShell)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
```

## Validate storyboard

```powershell
python -m pipeline.validate_storyboard
```

## Pipeline orchestration (Step 2)

Preview the stages without calling any AI provider:

```powershell
python -m pipeline.run --plan
```

Run the storyboard validation stage:

```powershell
python -m pipeline.run --stage validate
```

The runner records stage events in `logs/runs.jsonl` and writes a readable log to
`logs/pipeline.log`. Media stages are explicitly marked `not_implemented` until
their provider adapters are added; the runner will not pretend that media was generated.

The full pipeline command is:

```powershell
python -m pipeline.run
```

## Project structure

- `storyboard.json`: central source of truth for shots.
- `schema/storyboard.schema.json`: validation contract.
- `pipeline/`: Python pipeline stages.
- `outputs/`: generated media (ignored by Git by default).
- `DESIGN.md`, `ARCHITECTURE.md`, `EXPERIMENTS.md`, `FAILURES.md`, `COSTS.md`, `ETHICS.md`: project evidence and documentation.

## Secrets

Copy `.env.example` to `.env` and add credentials only when needed. Never commit `.env`.


## Storyboard review and radio cut

The primary audience is Ethiopian families and the young generation. Review
`storyboard.json` and `narration_script_am.txt` before generating media.

After generating Amharic narration as a WAV file, save it as
`outputs/audio/narration.wav`.

Install FFmpeg and ensure `ffmpeg` is available in your terminal PATH. Then run:

```powershell
python -m pipeline.create_radio_cut
```

This creates `outputs/final/radio_cut_vertical.mp4`: a black-screen prototype
with the supplied narration and a quiet synthetic placeholder audio bed. The
placeholder is for timing only, not the final original score. The script does
not generate speech; the narration WAV is created in the TTS stage.

Show the radio cut to at least three people from the intended audience. Record
their actual comments and the changes you make in `DESIGN.md`. Do not invent
test results.

## Automated checks

Run the project checks from the repository root:

```powershell
python -m pipeline.validate_storyboard
python -m pytest -q
```

GitHub Actions runs the same storyboard validation and tests on pushes and pull requests.

## Current implementation boundary

The current runner orchestrates and logs stages. Storyboard validation is executable; image generation, video generation, music generation, text-to-speech and final film assembly remain pending provider integrations and must not be considered complete until implemented and tested. Never add fabricated audience feedback, experiment results,
latency or cost measurements to the evidence files.
