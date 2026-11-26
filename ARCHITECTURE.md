# Architecture

## Current flow
`storyboard.json` -> JSON Schema validation -> pipeline runner.

## Planned stages
1. Story/script preparation
2. Keyframe generation
3. Image-to-video generation
4. Music generation
5. Amharic narration generation
6. FFmpeg assembly and 9:16 / 16:9 exports

## Contract
`storyboard.json` is the shared contract. Each shot has a stable ID, duration, image prompt, motion prompt, Amharic narration, English subtitle, music cue and reason.

## Planned reliability
- Validate input before model calls.
- Cache stage outputs using hashes of relevant inputs.
- Retry transient provider failures.
- Record every model call in `runs.jsonl`.
- Keep credentials in environment variables, never in source control.

## Implemented foundation

- Storyboard JSON Schema validation.
- Duration consistency check.
- Automated tests for schema, shot count, duration and unique IDs.
- GitHub Actions workflow for validation and tests.

The media-generation provider integrations remain to be implemented.
