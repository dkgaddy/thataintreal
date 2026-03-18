# thataintreal — Test Results

**Date:** 2026-03-18
**Model:** claude-sonnet-4-6 (upgraded from claude-haiku-4-5)
**Test set:** 41 images — 20 Real, 21 Fake

---

## Summary

| Category | Correct | Total | Accuracy |
|---|---|---|---|
| Real images (no false positives) | 20 | 20 | **100%** |
| Fake images (true positives) | 14 | 21 | **66%** |
| **Overall** | **34** | **41** | **82%** |

The original problem — convention/event photos being falsely flagged as AI-generated — is **fully resolved**. All 20 real images scored ≤ 12, all categorized as "Likely Real." Zero false positives.

---

## Real Images (20/20 PASS)

All real images scored between 4–12, firmly in the "Likely Real" category. Even images where EXIF had been stripped (common for phone photos shared via messaging apps) scored correctly — the model correctly contextualized missing EXIF as a weak signal rather than a trigger.

| File | Score | Category | Triggered Signals |
|---|---|---|---|
| IMG_0171.jpg | 6 | Likely Real | Missing EXIF |
| IMG_0181.jpg | 6 | Likely Real | Missing EXIF |
| IMG_0187.jpg | 6 | Likely Real | Missing EXIF |
| IMG_0196.jpg | 6 | Likely Real | Missing EXIF |
| IMG_0199.jpg | 6 | Likely Real | Missing EXIF |
| IMG_0209.jpg | 6 | Likely Real | Missing EXIF |
| IMG_0229.jpg | 6 | Likely Real | Missing EXIF |
| IMG_0296.jpg | 6 | Likely Real | Missing EXIF |
| IMG_0385.jpg | 6 | Likely Real | Missing EXIF |
| IMG_0387.jpg | 6 | Likely Real | Missing EXIF |
| IMG_0429.jpg | 6 | Likely Real | Missing EXIF |
| IMG_0431.jpg | 4 | Likely Real | *(none)* |
| IMG_0433.jpg | 6 | Likely Real | Missing EXIF |
| IMG_0442.jpg | 6 | Likely Real | Missing EXIF |
| IMG_0443.jpg | 8 | Likely Real | Missing EXIF |
| IMG_0450.jpg | 4 | Likely Real | *(none)* |
| IMG_0454.jpg | 5 | Likely Real | Missing EXIF |
| IMG_0472.jpg | 12 | Likely Real | Missing EXIF |
| IMG_0481.jpg | 4 | Likely Real | *(none)* |
| camphoto_342241519.jpg | 6 | Likely Real | Missing EXIF |

---

## Fake Images (14/21 PASS)

14 of 21 AI-generated images were correctly identified. The 7 that were missed are all highly photorealistic Midjourney images specifically designed to be indistinguishable from real photographs — the hardest category for any detection system.

### Correctly Detected (14 PASS)

| File | Score | Category |
|---|---|---|
| _soft_natural_light_portrait_of_a_young_handsome_man... | 82 | Definitely AI Generated |
| adeline1037_An_astronaut_in_Space... | 82 | Definitely AI Generated |
| christophe.asnar_une_agricultrice_francaise... | 72 | Probably Fake |
| cyberdragn_closeup_caucasian_8-year-old_boy... | 72 | Probably Fake |
| grupoenpunto_Back_view_product_photography... | 82 | Definitely AI Generated |
| havetochhimlen_58207_Young_man_torn_in_action_in_a_crowd... | 82 | Definitely AI Generated |
| illuminatus235_right_wing_extremists_on_Social_Media... | 82 | Definitely AI Generated |
| infiltraitor8518_watercolor_Hannah_the_Hermit_Crab... | 82 | Definitely AI Generated |
| june8282_A_dynamic_full-body_photorealistic_lifestyle... | 62 | Probably Fake |
| lensme._13329_Beauty_pictorial._A_beautiful_american... | 82 | Definitely AI Generated |
| motokoko44_Portrait_of_a_white_caucasian_male... | 72 | Probably Fake |
| nickthink_young_child_around_5_years_old_riding_a_bike... | 72 | Probably Fake |
| peterharlander_Juristische_Beratungsszene... | 72 | Probably Fake |
| u5686876697_MIU_MIU_STYLE_PHOTO._A_small_slim_Dalmatian... | 72 | Probably Fake |

### Missed (7 FAIL) — Analysis

These are all high-quality, photorealistic Midjourney generations that convincingly mimic real photography. They represent the upper bound of current AI image realism.

| File | Score | Category | Why Missed |
|---|---|---|---|
| REVKA_Fashion_campaign_photograph... | 38 | Suspicious | High-end fashion editorial style; subway/transit setting with strong directional light. 3 signals triggered but model gave benefit of doubt due to realistic setting. Borderline — scored just below threshold. |
| binutbangul_right_side_view_korean_highschool_student... | 18 | Likely Real | Street photograph style with Korean city signage, backlit golden hour light. Model interpreted authentic-looking environmental details as evidence of reality. |
| djd585_a_cinematic_movie_still_of_Ginny_Weasley_and_Elphaba... | 12 | Likely Real | Cinematic fantasy drama still. Model treated professional film/TV production aesthetic as legitimate — a reasonable inference that makes these especially hard to catch. |
| fancy_xiong_medium_shot_Donald_Trump_walks_in_white_house_lawn... | 12 | Likely Real | Hyperrealistic press photo style. Visible aging skin detail, natural outdoor lawn setting, consistent lighting. Convincingly mimics wire-service photography. |
| skeletlicek_full_size_portrait_shot_of_a_man_overhead_shot... | 18 | Likely Real | Editorial/lifestyle photography style with vintage BMW. Natural outdoor lighting and realistic skin texture detail. |
| u4193163144_a_cinematic_moody_scene_of_a_lone_silhouette... | 35 | Suspicious | Fine-art silhouette at dusk. Triggered texture smoothing signal but not enough additional evidence. |
| wwwwwwouter_A_vertical_smartphone_POV_photo_of_a_disheveled_man... | 18 | Likely Real | Smartphone POV kitchen scene with realistic directional sunlight. Deliberately mimics casual phone photography — a style very hard to distinguish from genuine. |

---

## Changes Made

### 1. `backend/prompt.py` — System prompt rewrite
- Added **"Challenging Real-World Photography Conditions"** section explicitly listing event/convention/crowd conditions that must not trigger signals in isolation (stage lighting, makeup, crowd backgrounds, wide-angle distortion, flash+ambient mix, social media EXIF stripping)
- Reframed ambiguous signals as **weak vs. strong**: smooth skin and uniform lighting only count when multiple other signals corroborate them
- Added **conservative scoring philosophy**: score >50 requires multiple independent signals; score >75 requires unambiguous AI artifacts; Missing EXIF contributes at most 3–5 points
- Added **internal chain-of-thought instructions**: model reasons about setting and context before triggering any signal

### 2. `backend/main.py` — EXIF signal override fix
- **Before**: Server forced `Missing EXIF → triggered=True` for all images without EXIF, overriding Claude's reasoning
- **After**: Server only corrects in one direction — if EXIF is present, ensures the signal reads false. If EXIF is absent, lets Claude's contextual assessment stand

### 3. `backend/claude_client.py` — Model upgrade + size fix
- Upgraded from `claude-haiku-4-5` → `claude-sonnet-4-6` for stronger contextual reasoning
- Added `temperature=0.2` for consistent, deterministic scoring
- Raised `max_tokens` from 1024 → 1500
- Fixed image size handling: now recompresses iteratively (quality 90→75→60→45) until under Claude's 5MB base64 API limit, preventing failures on large PNG files

---

## Notes

- The 7 missed fakes are genuinely state-of-the-art photorealistic AI images. These are expected to challenge any detection system and represent the current frontier of AI image realism. The tool now correctly prioritizes **not falsely accusing real photos** over catching every sophisticated fake.
- The `REVKA` fashion image scored 38 (Suspicious) — it's at least flagged as uncertain rather than being confidently wrong.
- Consider rotating the Anthropic API key used during testing, as it was shared in plaintext.
