import base64
import io
import json
import os

import anthropic
from PIL import Image

from prompt import SYSTEM_PROMPT, build_user_message

_client = None


def _get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        _client = anthropic.Anthropic(api_key=os.environ["CLAUDE_API_KEY"])
    return _client


def _resize_if_needed(image_bytes: bytes, media_type: str) -> tuple[bytes, str]:
    """Resize image to max 2048px on longest side if needed. Returns (bytes, media_type)."""
    try:
        img = Image.open(io.BytesIO(image_bytes))
        w, h = img.size
        if max(w, h) <= 2048:
            return image_bytes, media_type

        ratio = 2048 / max(w, h)
        new_size = (int(w * ratio), int(h * ratio))
        img = img.resize(new_size, Image.LANCZOS)

        if img.mode == "RGBA":
            img = img.convert("RGB")

        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=90)
        return buf.getvalue(), "image/jpeg"
    except Exception:
        return image_bytes, media_type


def analyze_image(image_bytes: bytes, media_type: str, exif_summary: str) -> dict:
    """Send image to Claude for fake detection analysis. Returns parsed JSON dict."""
    send_bytes, send_type = _resize_if_needed(image_bytes, media_type)
    b64 = base64.standard_b64encode(send_bytes).decode("utf-8")
    user_message = build_user_message(exif_summary)

    client = _get_client()
    response = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": send_type,
                            "data": b64,
                        },
                    },
                    {"type": "text", "text": user_message},
                ],
            }
        ],
    )

    raw_text = response.content[0].text.strip()

    # Strip markdown code fences if Claude wraps in them
    if raw_text.startswith("```"):
        lines = raw_text.split("\n")
        raw_text = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])

    try:
        return json.loads(raw_text)
    except json.JSONDecodeError as e:
        raise ValueError(f"Claude returned non-JSON response: {raw_text[:200]}") from e
