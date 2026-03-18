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


_MAX_API_BYTES = 3_900_000  # Claude API base64 limit is 5MB; raw bytes must stay under ~3.9MB


def _resize_if_needed(image_bytes: bytes, media_type: str) -> tuple[bytes, str]:
    """Resize/recompress image so it fits within Claude's API size and dimension limits."""
    try:
        img = Image.open(io.BytesIO(image_bytes))
        w, h = img.size

        # Downscale if wider/taller than 2048px
        if max(w, h) > 2048:
            ratio = 2048 / max(w, h)
            img = img.resize((int(w * ratio), int(h * ratio)), Image.LANCZOS)
            w, h = img.size

        if img.mode == "RGBA":
            img = img.convert("RGB")

        # If already small enough as-is, return original bytes
        if len(image_bytes) <= _MAX_API_BYTES and max(w, h) <= 2048:
            # Still need to re-encode if we changed size/mode above
            if img.size == Image.open(io.BytesIO(image_bytes)).size:
                return image_bytes, media_type

        # Encode as JPEG, reducing quality until under the byte limit
        for quality in (90, 75, 60, 45):
            buf = io.BytesIO()
            img.save(buf, format="JPEG", quality=quality)
            if buf.tell() <= _MAX_API_BYTES:
                return buf.getvalue(), "image/jpeg"

        # Last resort: halve dimensions and encode at 60
        img = img.resize((w // 2, h // 2), Image.LANCZOS)
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=60)
        return buf.getvalue(), "image/jpeg"
    except Exception:
        return image_bytes, media_type


def analyze_image(image_bytes: bytes, media_type: str, exif_summary: str) -> dict:
    """Send image to Claude for fake detection analysis. Returns parsed JSON dict."""
    send_bytes, send_type = _resize_if_needed(image_bytes, media_type)
    b64 = base64.standard_b64encode(send_bytes).decode("utf-8")
    user_message = build_user_message(exif_summary)

    client = _get_client()
    model = os.environ.get("CLAUDE_MODEL", "claude-haiku-4-5")
    response = client.messages.create(
        model=model,
        max_tokens=1500,
        temperature=0.2,
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
