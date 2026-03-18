#!/usr/bin/env python3
"""
Test script: run all images in Testimages/ through the analyze_image pipeline.
Usage:
  python run_tests.py           # uses CLAUDE_MODEL env var (default: haiku)
  python run_tests.py haiku     # forces claude-haiku-4-5
  python run_tests.py sonnet    # forces claude-sonnet-4-6
"""
import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
load_dotenv()

# Allow overriding model via CLI arg; otherwise falls through to CLAUDE_MODEL env var
if len(sys.argv) > 1:
    arg = sys.argv[1].lower()
    os.environ["CLAUDE_MODEL"] = "claude-haiku-4-5" if "haiku" in arg else "claude-sonnet-4-6"

from claude_client import analyze_image
from exif_utils import extract_exif

MODEL = os.environ.get("CLAUDE_MODEL", "claude-haiku-4-5")

TESTIMAGES = Path(__file__).parent.parent / "Testimages"
REAL_DIR = TESTIMAGES / "Real"
FAKE_DIR = TESTIMAGES / "Fake"

results = []

def analyze_file(path: Path, expected: str):
    image_bytes = path.read_bytes()
    media_type = "image/jpeg" if path.suffix.lower() in (".jpg", ".jpeg") else "image/png"
    exif_summary, _ = extract_exif(image_bytes)
    result = analyze_image(image_bytes, media_type, exif_summary)
    score = result.get("fake_score", -1)
    category = result.get("category", "Unknown")
    correct = (expected == "Real" and score <= 50) or (expected == "Fake" and score > 50)
    triggered = [s["name"] for s in result.get("signals", []) if s.get("triggered")]
    entry = {
        "file": path.name,
        "expected": expected,
        "score": score,
        "category": category,
        "correct": correct,
        "triggered_signals": triggered,
        "explanation": result.get("explanation", ""),
    }
    results.append(entry)
    status = "PASS" if correct else "FAIL"
    print(f"[{status}] {expected:4s} | {path.name[:55]:<55s} | score={score:3d} | {category}")
    sys.stdout.flush()
    return entry

print("=" * 90)
print(f"MODEL: {MODEL}")
print("REAL IMAGES (expect score ≤ 50)")
print("=" * 90)
for img in sorted(REAL_DIR.iterdir()):
    if img.suffix.lower() in (".jpg", ".jpeg", ".png", ".webp"):
        analyze_file(img, "Real")

print()
print("=" * 90)
print("FAKE IMAGES (expect score > 50)")
print("=" * 90)
for img in sorted(FAKE_DIR.iterdir()):
    if img.suffix.lower() in (".jpg", ".jpeg", ".png", ".webp"):
        analyze_file(img, "Fake")

print()
print("=" * 90)
real_results = [r for r in results if r["expected"] == "Real"]
fake_results = [r for r in results if r["expected"] == "Fake"]
real_pass = sum(1 for r in real_results if r["correct"])
fake_pass = sum(1 for r in fake_results if r["correct"])
print(f"Real images:  {real_pass}/{len(real_results)} correct  ({100*real_pass//max(len(real_results),1)}%)")
print(f"Fake images:  {fake_pass}/{len(fake_results)} correct  ({100*fake_pass//max(len(fake_results),1)}%)")
print(f"Overall:      {real_pass+fake_pass}/{len(results)} correct  ({100*(real_pass+fake_pass)//max(len(results),1)}%)")

with open("test_results.json", "w") as f:
    json.dump(results, f, indent=2)
print("\nFull results saved to test_results.json")
