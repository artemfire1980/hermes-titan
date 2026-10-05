---
name: voice-transcription
description: "Transcribe Telegram voice messages on Khadas VIM4."
version: 1.0.0
author: user
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [Audio, Transcription, Voice, faster-whisper, Opus]
prerequisites:
  commands: [ffmpeg, python3]
  pip: [faster-whisper, numpy]
---

# Voice Transcription

Transcribe Telegram voice messages and other audio files to text using faster-whisper on CPU (Khadas VIM4, ARM64).

## When to use

- A voice message arrives that Hermes cannot auto-transcribe (common on Telegram).
- Any audio file needs transcription: .ogg, .opus, .mp3, .m4a, .wav.

## Prerequisites

faster-whisper and numpy are installed in the Hermes Python environment:

```bash
/mnt/ai-ssd/hermes/tools/python-3.14.7+202****0901-linux-arm64/bin/pip install faster-whisper numpy
```

The `base` model is cached at `~/.cache/huggingface/hub/models--Systran--faster-whisper-base`.

## Procedure

### 1. Locate the audio file

Voice messages land in `/mnt/ai-ssd/hermes/cache/audio/` as `.ogg` (Opus, 48 kHz mono).

### 2. Convert to WAV (required)

faster-whisper's audio decoder (PyAV) is incompatible with the installed version on this system — it crashes on `.ogg`/`.opus` inputs. Always pre-convert with ffmpeg:

```bash
/mnt/ai-ssd/hermes/tools/ffmpeg-9.0.1-linux-arm64/bin/ffmpeg -y -i input.ogg -ar 16000 -ac 1 -c:a pcm_s16le output.wav
```

Use 16 kHz mono PCM — that is what faster-whisper expects and it keeps the file small.

### 3. Load as numpy array (required)

Passing a file path to `model.transcribe()` also fails (av `open()` signature mismatch). Load the WAV manually and pass the array:

```python
import wave, numpy as np

with wave.open("output.wav", "rb") as wf:
    raw = wf.readframes(wf.getnframes())
    audio = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
np.save("audio.npy", audio)
```

Then transcribe:

```python
from faster_whisper import WhisperModel

model = WhisperModel(
    "base", device="cpu", compute_type="int8", download_root="/mnt/ai-ssd/.cache/huggingface/hub"
)
segments, info = model.transcribe(np.load("audio.npy"), language="ru")
for seg in segments:
    print(f"[{seg.start:.1f}-{seg.end:.1f}] {seg.text}")
```

### 4. Report

Print the transcript plainly. Do not narrate the conversion steps unless the user asked.

## Pitfalls

- **Do NOT pass .ogg/.opus directly to faster-whisper.** The PyAV decoder raises `TypeError: open() got an unexpected keyword argument 'metadata_errors'`. Convert to WAV first.
- **Do NOT pass a file path to transcribe().** The same av incompatibility triggers on path input. Always load via `wave` + `numpy` and pass the float32 array.
- **Set timeout=300 on terminal calls.** Transcription of a ~4 s clip takes 1–2 minutes on VIM4 CPU. Shorter timeouts cause false failures.
- **The `base` model is sufficient** for short voice messages. Use `small` or `medium` only for long, noisy, or multi-speaker audio — they are much slower on CPU.

## Notes

- Language is auto-detected but pinning `language='ru'` for Russian voice messages avoids a detection round-trip.
- Clean up intermediate `.wav` and `.npy` files from `/mnt/ai-ssd/hermes/cache/scratch/` after transcription unless the user asks to keep them.
