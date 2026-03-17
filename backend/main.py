import os

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from claude_client import analyze_image
from exif_utils import extract_exif

app = FastAPI(title="thataintreal API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://thataintreal.explosiveconcepts.com",
        "http://localhost:8082",
        "http://127.0.0.1:8082",
        "http://localhost:8083",
        "http://127.0.0.1:8083",
        "http://localhost:8084",
        "http://127.0.0.1:8084",
    ],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=415,
            detail=f"Unsupported file type: {file.content_type}. Use JPEG, PNG, or WEBP.",
        )

    image_bytes = await file.read()

    if len(image_bytes) > MAX_SIZE_BYTES:
        raise HTTPException(
            status_code=413,
            detail="File too large. Maximum size is 10 MB.",
        )

    exif_summary, has_exif = extract_exif(image_bytes)

    try:
        result = analyze_image(image_bytes, file.content_type, exif_summary)
    except ValueError as e:
        raise HTTPException(status_code=422, detail="Image could not be analyzed. Please try a different image.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

    # Ensure Missing EXIF signal is correct based on server-side extraction
    if "signals" in result:
        for signal in result["signals"]:
            if signal.get("name") == "Missing EXIF":
                if not has_exif:
                    signal["triggered"] = True
                    if not signal.get("detail"):
                        signal["detail"] = "No EXIF metadata found in this image"
                break

    return JSONResponse(content=result)
