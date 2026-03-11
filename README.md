# worldscore_OCR

## Offline-first OCR behavior

`ocr_engine.py` now runs in an offline-first mode:

- It first looks for a sidecar OCR payload at `<image_path>.ocr.json`.
- If not found, it looks for cached payloads in `.ocr_cache/`.
- Gemini calls are disabled by default and only enabled when `OCR_ALLOW_AI=1`.

This lets you process scorecards without calling AI services while still returning the same structured results when sidecar/cache data is present.
