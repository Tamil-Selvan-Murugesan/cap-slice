"""Generate one narration clip per scene with ElevenLabs.

    ELEVENLABS_API_KEY=... python3 tools/explainer_video/tts.py OUT_DIR [VOICE_ID]

Reads script.json next to this file; writes OUT_DIR/<scene id>.mp3. Skips clips
that already exist, so re-running only re-generates what's missing. The key is
read from the environment only and never written anywhere.
"""

from __future__ import annotations

import json
import os
import sys
import urllib.request
from pathlib import Path

HERE = Path(__file__).parent
MODEL = "eleven_multilingual_v2"
DEFAULT_VOICE = "21m00Tcm4TlvDq8ikWAM"  # "Rachel", an ElevenLabs premade voice


def main(out: Path, voice: str) -> None:
    key = os.environ["ELEVENLABS_API_KEY"]
    out.mkdir(parents=True, exist_ok=True)
    for scene in json.loads((HERE / "script.json").read_text()):
        path = out / f"{scene['id']}.mp3"
        if path.exists():
            continue
        req = urllib.request.Request(
            f"https://api.elevenlabs.io/v1/text-to-speech/{voice}?output_format=mp3_44100_64",
            data=json.dumps({"text": scene["say"], "model_id": MODEL,
                             "voice_settings": {"stability": 0.5, "similarity_boost": 0.75}}).encode(),
            headers={"xi-api-key": key, "Content-Type": "application/json", "Accept": "audio/mpeg"})
        with urllib.request.urlopen(req, timeout=60) as resp:
            path.write_bytes(resp.read())
        print("wrote", path.name)


if __name__ == "__main__":
    main(Path(sys.argv[1]), sys.argv[2] if len(sys.argv) > 2 else DEFAULT_VOICE)
