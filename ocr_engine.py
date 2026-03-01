#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar  1 15:37:50 2026

@author: daltonstout
"""

import os
import base64
import json
from io import BytesIO
from google import genai
from google.genai import types
from PIL import Image, ImageOps

client = genai.Client(
    api_key=os.environ.get("AI_INTEGRATIONS_GEMINI_API_KEY"),
    http_options={
        'api_version': '',
        'base_url': os.environ.get("AI_INTEGRATIONS_GEMINI_BASE_URL")
    }
)

MODEL_PRIMARY = "gemini-2.5-flash"
MODEL_FAST = "gemini-2.5-flash"

SCORECARD_PROMPT = """You are an expert golf scorecard OCR system. Extract every number and name from this golf scorecard photo with extreme precision.

SCORECARD LAYOUT (columns left to right):
NAME | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | OUT | 10 | 11 | 12 | 13 | 14 | 15 | 16 | 17 | 18 | IN | TOT | HCP | NET

KEY DEFINITIONS:
- OUT = front 9 subtotal (sum of holes 1-9), single column immediately after hole 9
- IN = back 9 subtotal (sum of holes 10-18), single column immediately after hole 18
- TOT = gross total (OUT + IN)
- HCP = handicap, NET = TOT minus HCP

STEP 1 — READ THE PAR ROW:
The PAR row is PRINTED text (not handwritten), labeled "Par" or "PAR". Read each of the 18 par values one cell at a time. Each MUST be 3, 4, or 5.
- Also read the printed OUT and IN subtotals for the par row.
- VERIFY: your 9 front par values MUST sum to the printed OUT. Your 9 back par values MUST sum to the printed IN. If not, re-read until they match.

STEP 2 — READ EACH PLAYER ROW:
For each player (handwritten row):
- Read the NAME from the leftmost column.
- Read EXACTLY 18 hole scores, one per column, left to right (holes 1-9 then 10-18). Scores are typically 2-9. Do NOT include OUT/IN/TOT as hole scores. You MUST output exactly 18 integers in the holes array for every player.
- Also read the written OUT, IN, TOT, HCP, NET values from their respective columns.
- IMPORTANT: Read each hole score exactly as written. Do NOT change any hole score to match the written OUT/IN/TOT — the player may have added incorrectly. The individual hole scores are what matter most.

STEP 3 — SCORING NOTATION (CRITICAL — read carefully):
There are TWO notation systems used on scorecards. Read BOTH:

SYSTEM A — PGA SHAPE MARKS (shapes drawn around scores):
- CIRCLE around a number = Birdie (1 under par). The score is the number INSIDE the circle.
- DOUBLE CIRCLE (two concentric circles, or a thick/bold circle) = Eagle (2 under par). If the circle line looks thick, doubled, or has TWO rings around the number, mark as double_circle. Check: does the score = par - 2? If yes, it's double_circle (eagle).
- SQUARE/BOX around a number = Bogey (1 over par). The score is the number INSIDE the box.
- DOUBLE SQUARE (two concentric boxes) = Double Bogey (2 over par).
- TRIANGLE around a number = Triple Bogey (3 over par). A triangle has 3 straight edges forming a clear triangular/tent shape around the number. Do NOT miss triangles — they are distinct from circles and squares.
- NO marking = Par or no special performance.
- The number NEVER changes because of the marking. A circled 3 is 3, not 2 or 4.
- When a circle makes a "3" look like "8", focus on the digit inside — it's 3.
- IMPORTANT: Carefully examine EVERY hole for EVERY player for notation marks. Do NOT skip any.

SYSTEM B — STROKE COUNT / RELATIVE-TO-PAR NOTATION:
Some golfers write "+1", "+2", "+3", "-1", "-2", "E", or "0" in the score box INSTEAD of the raw stroke count:
- "-1" = Birdie (par - 1). Record notation as "circle" and score as par - 1.
- "-2" = Eagle (par - 2). Record notation as "double_circle" and score as par - 2.
- "+1" = Bogey (par + 1). Record notation as "square" and score as par + 1.
- "+2" = Double Bogey (par + 2). Record notation as "double_square" and score as par + 2.
- "+3" = Triple Bogey (par + 3). Record notation as "triangle" and score as par + 3.
- "0" or "E" = Par. Record score as par, notation as "none".
- If you see these, convert to actual stroke counts using the par for that hole.

CROSS-CHECK: For every notation you detect, verify the math:
- circle: score should = par - 1
- double_circle: score should = par - 2
- square: score should = par + 1
- triangle: score should = par + 3
If the math doesn't match, re-examine both the score digit AND the notation shape — one of them may be misread.

STEP 4 — HANDWRITING TIPS:
- "4" vs "9": 4 has open angular top, 9 has closed round loop
- "5" vs "6": 5 has flat/angular top stroke, 6 has rounded top
- "3" vs "8": 3 has open curves, 8 has two closed loops. A circle drawn around "3" can make it look like "8" — if you see a circle notation, the digit is likely 3 not 8.
- "1" vs "7": 1 is simple vertical stroke, 7 has horizontal top bar
- "4" vs "1": Inside a circle, a "4" can look like "1" — if the score seems impossibly low (like 1 on a par 4 or par 5), re-examine whether it's actually a "4".
- Score of 0 is IMPOSSIBLE in golf
- Score of 1 (hole-in-one) is only realistic on par 3 holes. A "1" on a par 4 or par 5 is almost certainly a misread — look again carefully.

STEP 5 — FINAL VERIFICATION:
For EVERY player, read each hole score as accurately as possible. The player may have added the OUT/IN/TOT totals incorrectly — do NOT change a hole score just to match a written total. The individual hole scores are what matter most.
If any scores are uncertain, state which holes and why.

Return ONLY compact JSON (no extra whitespace or newlines):
{"course_name":"name or null","par":[18 ints],"par_front_9_total":N,"par_back_9_total":N,"players":[{"name":"str","holes":[18 ints],"hole_notations":["none"|"circle"|"double_circle"|"square"|"double_square"|"triangle"],"handicap":N_or_null,"front_9_total":N,"back_9_total":N,"gross_total":N,"notes":"str"}],"confidence":"HIGH"|"MEDIUM"|"LOW","issues":["str"],"card_type":"STANDARD_18"|"FRONT_9"|"BACK_9"|"OTHER","low_confidence_holes":[{"player":"str","hole":N,"extracted":N,"reason":"str"}]}"""


VERIFY_PROMPT = """You are verifying golf scorecard OCR results against the actual scorecard image. Re-examine EACH value.

PREVIOUSLY EXTRACTED DATA:
{extracted_data}

YOUR TASK: Make computed totals match written totals. If MISMATCH flags exist, find and fix the wrong hole scores.

VERIFICATION STEPS:
1. PAR ROW: Re-read every printed par value. Each must be 3, 4, or 5. Front 9 must sum to printed OUT, back 9 to printed IN.

2. FOR EACH PLAYER WITH MISMATCH:
   - Check FRONT_9_MISMATCH / BACK_9_MISMATCH to know which half has errors.
   - Re-read each hole score in the affected half from the image.
   - Common misreads: circled scores (circle makes 3 look like 8), 4↔9, 5↔6, 3↔8, 1↔7.
   - Find specific corrections that make the sum match the written total.

3. NOTATION CROSS-CHECK: For holes with notation markings:
   - "circle" → score should be par-1, "square" → score should be par+1
   - If there's a conflict and it says "LIKELY PAR ERROR", the par value may be wrong, not the score.

4. IMPORTANT GUARDRAIL: Do NOT change a score if it would WORSEN the half-subtotal match.

Return ONLY this JSON:
{{
  "verified": true/false,
  "corrections": [{{"player":"name","hole":N,"old_value":X,"new_value":Y,"reason":"why"}}],
  "par_corrections": [{{"hole":N,"old_value":X,"new_value":Y}}],
  "name_corrections": [{{"old_name":"old","new_name":"new"}}],
  "notation_corrections": [{{"player":"name","hole":N,"old_notation":"old","new_notation":"new","reason":"why"}}],
  "confidence": "HIGH"|"MEDIUM"|"LOW",
  "notes": "observations"
}}"""


def strip_subtotal_columns(values):
    if not values or not isinstance(values, list):
        return values
    if len(values) == 18:
        return values

    def is_subtotal(val, expected_sum):
        if val is None or not isinstance(val, (int, float)):
            return False
        return val > 9 or abs(val - expected_sum) <= 3

    if len(values) == 21:
        return values[:9] + values[10:19]

    if len(values) == 20:
        front_9 = values[:9]
        front_sum = sum(v for v in front_9 if isinstance(v, (int, float)) and v is not None)
        if is_subtotal(values[9], front_sum):
            return front_9 + values[10:19]
        back_check = values[9:18]
        back_sum = sum(v for v in back_check if isinstance(v, (int, float)) and v is not None)
        if is_subtotal(values[18], back_sum):
            return values[:9] + values[9:18]
        return values[:9] + values[10:19]

    if len(values) == 19:
        front_9 = values[:9]
        front_sum = sum(v for v in front_9 if isinstance(v, (int, float)) and v is not None)
        if is_subtotal(values[9], front_sum):
            return front_9 + values[10:19]
        back_9 = values[9:18]
        back_sum = sum(v for v in back_9 if isinstance(v, (int, float)) and v is not None)
        if is_subtotal(values[18], back_sum):
            return values[:9] + back_9
        return values[:9] + values[10:19]

    if len(values) > 18:
        return values[:9] + values[len(values)-9:]
    return values


def _normalize_image_orientation(image_bytes):
    try:
        img = Image.open(BytesIO(image_bytes))
        img = ImageOps.exif_transpose(img)
        w, h = img.size
        if h > w:
            img = img.rotate(90, expand=True)
            w, h = img.size
        MAX_DIM = 3000
        if w > MAX_DIM or h > MAX_DIM:
            scale = MAX_DIM / max(w, h)
            img = img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
        if img.mode == 'RGBA':
            img = img.convert('RGB')
        buf = BytesIO()
        img.save(buf, format='JPEG', quality=90)
        return buf.getvalue(), 'image/jpeg'
    except Exception:
        return image_bytes, None


def encode_image_to_base64(image_path):
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def get_image_media_type(image_path):
    ext = os.path.splitext(image_path)[1].lower()
    media_types = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".gif": "image/gif",
        ".webp": "image/webp",
        ".bmp": "image/bmp"
    }
    return media_types.get(ext, "image/jpeg")


def _parse_json_response(raw_text):
    if raw_text.startswith("```json"):
        raw_text = raw_text[7:]
    if raw_text.startswith("```"):
        raw_text = raw_text[3:]
    if raw_text.endswith("```"):
        raw_text = raw_text[:-3]
    raw_text = raw_text.strip()
    json_start = raw_text.find('{')
    json_end = raw_text.rfind('}')
    if json_start >= 0 and json_end > json_start:
        raw_text = raw_text[json_start:json_end + 1]
    try:
        return json.loads(raw_text)
    except json.JSONDecodeError:
        try:
            repaired = _repair_truncated_json(raw_text)
            return json.loads(repaired)
        except (json.JSONDecodeError, Exception):
            raise json.JSONDecodeError("Could not parse or repair JSON", raw_text[:200], 0)


def _repair_truncated_json(text):
    open_braces = 0
    open_brackets = 0
    in_string = False
    escape = False
    last_good = 0
    for i, c in enumerate(text):
        if escape:
            escape = False
            continue
        if c == '\\':
            escape = True
            continue
        if c == '"' and not escape:
            in_string = not in_string
            continue
        if in_string:
            continue
        if c == '{':
            open_braces += 1
        elif c == '}':
            open_braces -= 1
        elif c == '[':
            open_brackets += 1
        elif c == ']':
            open_brackets -= 1
        if open_braces >= 0 and open_brackets >= 0:
            last_good = i
    result = text[:last_good + 1]
    if in_string:
        result += '"'
    while open_brackets > 0:
        result += ']'
        open_brackets -= 1
    while open_braces > 0:
        result += '}'
        open_braces -= 1
    return result


def _call_gemini(prompt_text, image_bytes, media_type, model=None, max_tokens=8192):
    import time as _time
    if model is None:
        model = MODEL_PRIMARY
    last_err = None
    for attempt in range(3):
        try:
            if attempt > 0:
                _time.sleep(3 + attempt * 2)
            response = client.models.generate_content(
                model=model,
                contents=[
                    types.Content(
                        role="user",
                        parts=[
                            types.Part.from_text(text=prompt_text),
                            types.Part.from_bytes(data=image_bytes, mime_type=media_type),
                        ]
                    )
                ],
                config=types.GenerateContentConfig(
                    max_output_tokens=max_tokens,
                    temperature=0.0,
                    thinking_config=types.ThinkingConfig(
                        thinking_budget=0,
                    ),
                )
            )
            text = ""
            if hasattr(response, 'text') and response.text:
                text = response.text
            elif hasattr(response, 'candidates') and response.candidates:
                for candidate in response.candidates:
                    if hasattr(candidate, 'content') and candidate.content:
                        for part in candidate.content.parts:
                            if hasattr(part, 'text') and part.text:
                                text += part.text
            if not text:
                raise ValueError("Empty response from Gemini")
            return text
        except Exception as e:
            last_err = e
            err_str = str(e)
            if "429" in err_str or "rate" in err_str.lower() or "ApiKeyNotApproved" in err_str or "401" in err_str:
                continue
            if "Empty response" in err_str:
                continue
            raise
    raise last_err


def _normalize_name(n):
    return (n or "").strip().lower().replace(".", "").replace("-", " ")


def _match_player(sp_name, result_players):
    sp_norm = _normalize_name(sp_name)
    for p in result_players:
        if _normalize_name(p.get("name")) == sp_norm:
            return p
    for p in result_players:
        rn = _normalize_name(p.get("name"))
        if sp_norm and rn and (sp_norm in rn or rn in sp_norm):
            return p
    return None


def ocr_scorecard(image_path):
    if not os.path.exists(image_path):
        return {
            "error": f"Image file not found: {image_path}",
            "players": [],
            "confidence": "LOW",
            "issues": ["File not found"]
        }

    try:
        with open(image_path, "rb") as f:
            image_bytes = f.read()
        image_bytes, normalized_media_type = _normalize_image_orientation(image_bytes)
        media_type = normalized_media_type or get_image_media_type(image_path)

        raw_text = _call_gemini(SCORECARD_PROMPT, image_bytes, media_type, model=MODEL_PRIMARY)
        try:
            result = _parse_json_response(raw_text)
        except json.JSONDecodeError:
            import time as _t0
            _t0.sleep(3)
            raw_text = _call_gemini(
                SCORECARD_PROMPT + "\n\nIMPORTANT: Return ONLY valid JSON. No markdown, no extra text.",
                image_bytes, media_type, model=MODEL_PRIMARY
            )
            result = _parse_json_response(raw_text)

        par = result.get("par", [])
        if len(par) != 18:
            par = strip_subtotal_columns(par)
            result["par"] = par

        for player in result.get("players", []):
            if player.get("name"):
                player["name"] = player["name"].upper()
            holes = player.get("holes", [])
            notations = player.get("hole_notations", [])
            cleaned_holes = []
            for h in holes:
                if h is None:
                    cleaned_holes.append(None)
                elif isinstance(h, (int, float)):
                    cleaned_holes.append(int(h))
                else:
                    cleaned_holes.append(None)
            if len(cleaned_holes) != 18:
                cleaned_holes = strip_subtotal_columns(cleaned_holes)
            if len(cleaned_holes) < 18:
                if "issues" not in result:
                    result["issues"] = []
                result["issues"].append(
                    f"Warning: {player.get('name','?')} only has {len(cleaned_holes)} holes extracted (expected 18)"
                )
                while len(cleaned_holes) < 18:
                    cleaned_holes.append(None)
            rel_to_par_map = {-1: "circle", -2: "double_circle", 0: "none",
                              1: "square", 2: "double_square", 3: "triangle"}
            if "issues" not in result:
                result["issues"] = []
            for i in range(min(len(cleaned_holes), len(par))):
                score = cleaned_holes[i]
                if score is not None and score <= 0:
                    hole_par = par[i] if i < len(par) else 4
                    real_score = hole_par + score
                    if real_score >= 1:
                        result["issues"].append(
                            f"Relative-to-par: {player.get('name','?')} hole {i+1} "
                            f"'{score}' -> {real_score} (par {hole_par} + ({score}))"
                        )
                        cleaned_holes[i] = real_score
                        if i < len(notations):
                            new_notation = rel_to_par_map.get(score, "none")
                            if new_notation != "none":
                                notations[i] = new_notation
            player["holes"] = cleaned_holes

            if player.get("handicap") is not None:
                try:
                    player["handicap"] = int(player["handicap"])
                except (ValueError, TypeError):
                    player["handicap"] = None

            if player.get("gross_total") is not None:
                try:
                    player["gross_total"] = int(player["gross_total"])
                except (ValueError, TypeError):
                    player["gross_total"] = None

            if player.get("front_9_total") is not None:
                try:
                    player["front_9_total"] = int(player["front_9_total"])
                except (ValueError, TypeError):
                    player["front_9_total"] = None
            if player.get("back_9_total") is not None:
                try:
                    player["back_9_total"] = int(player["back_9_total"])
                except (ValueError, TypeError):
                    player["back_9_total"] = None

        result = _fix_swapped_subtotals(result)

        for player in result.get("players", []):
            holes = player.get("holes", [])
            if len(holes) != 18:
                holes = strip_subtotal_columns(holes)
                player["holes"] = holes
            valid = [h for h in holes if h is not None]
            if valid:
                computed_total = sum(valid)
                written_total = player.get("gross_total")
                player["written_gross_total"] = written_total
                player["gross_total"] = computed_total
                if player.get("front_9_total"):
                    player["front_9_total"] = int(player["front_9_total"])
                if player.get("back_9_total"):
                    player["back_9_total"] = int(player["back_9_total"])

        par = result.get("par", [])
        if len(par) == 18:
            par_front_printed = result.get("par_front_9_total")
            par_back_printed = result.get("par_back_9_total")
            if par_front_printed and par_back_printed:
                pf = int(par_front_printed)
                pb = int(par_back_printed)
                comp_pf = sum(par[:9])
                comp_pb = sum(par[9:18])
                cur_diff = abs(comp_pf - pf) + abs(comp_pb - pb)
                swap_diff = abs(comp_pf - pb) + abs(comp_pb - pf)
                if swap_diff < cur_diff:
                    result["par_front_9_total"] = par_back_printed
                    result["par_back_9_total"] = par_front_printed
                    par_front_printed = par_back_printed
                    par_back_printed = result["par_back_9_total"]
            if par_front_printed:
                par_front_printed = int(par_front_printed)
                par_front_computed = sum(par[:9])
                if par_front_computed != par_front_printed:
                    diff = par_front_computed - par_front_printed
                    if abs(diff) <= 2:
                        for i in range(9):
                            alt = par[i] - diff
                            if alt in (3, 4, 5) and alt != par[i]:
                                par[i] = alt
                                break
                            if sum(par[:9]) == par_front_printed:
                                break
            if par_back_printed:
                par_back_printed = int(par_back_printed)
                par_back_computed = sum(par[9:18])
                if par_back_computed != par_back_printed:
                    diff = par_back_computed - par_back_printed
                    if abs(diff) <= 2:
                        for i in range(9, 18):
                            alt = par[i] - diff
                            if alt in (3, 4, 5) and alt != par[i]:
                                par[i] = alt
                                break
                            if sum(par[9:18]) == par_back_printed:
                                break
            result["par"] = par

        for p in result.get("players", []):
            notations = p.get("hole_notations", [])
            p["_has_notation"] = any(n in NOTATION_OFFSET for n in notations)
            p["_pre_notation_total"] = p.get("gross_total")

        result = _notation_crosscheck(result)
        result = _programmatic_crosscheck(result)

        for p in result.get("players", []):
            holes = p.get("holes", [])
            computed = sum(h for h in holes if h is not None)
            p["gross_total"] = computed
            wt = p.get("written_gross_total")
            if wt and computed != wt:
                if "issues" not in result:
                    result["issues"] = []
                result["issues"].append(
                    f"Note: {p.get('name', '?')} hole sum={computed}, card total={wt} "
                    f"(diff={computed - wt}). Hole scores are authoritative."
                )

        return result

    except json.JSONDecodeError as e:
        return {
            "error": f"Failed to parse OCR response: {str(e)}",
            "raw_response": raw_text if 'raw_text' in dir() else "No response",
            "players": [],
            "confidence": "LOW",
            "issues": ["JSON parse error from AI response"]
        }
    except Exception as e:
        return {
            "error": f"OCR processing failed: {str(e)}",
            "players": [],
            "confidence": "LOW",
            "issues": [str(e)]
        }


def verify_ocr_results(initial_result, image_bytes, media_type):
    try:
        extracted_summary = {
            "par": initial_result.get("par", []),
            "players": []
        }
        for p in initial_result.get("players", []):
            holes = p.get("holes", [])
            valid_holes = [h for h in holes if h is not None]
            computed_total = sum(valid_holes) if valid_holes else 0
            front_9 = sum(h for h in holes[:9] if h is not None)
            back_9 = sum(h for h in holes[9:18] if h is not None)
            written_total = p.get("gross_total")
            written_front = p.get("front_9_total")
            written_back = p.get("back_9_total")
            notations = p.get("hole_notations", [])
            player_entry = {
                "name": p.get("name"),
                "holes": holes,
                "hole_notations": notations,
                "gross_total": written_total,
                "written_front_9": written_front,
                "written_back_9": written_back,
                "computed_total_from_holes": computed_total,
                "computed_front_9": front_9,
                "computed_back_9": back_9,
                "handicap": p.get("handicap")
            }
            par_vals = initial_result.get("par", [])
            notation_issues = []
            notation_map = {"circle": -1, "double_circle": -2, "square": 1, "double_square": 2, "triangle": 3}
            for idx, notation in enumerate(notations):
                if notation in notation_map and idx < len(holes) and idx < len(par_vals):
                    offset = notation_map[notation]
                    expected_score = par_vals[idx] + offset
                    actual_score = holes[idx]
                    if actual_score is not None and actual_score != expected_score:
                        implied_par = actual_score - offset
                        if implied_par in (3, 4, 5):
                            notation_issues.append(
                                f"Hole {idx+1}: notation='{notation}' with current par={par_vals[idx]} implies score={expected_score}, but extracted score={actual_score}. "
                                f"LIKELY PAR ERROR: if par were {implied_par}, the score {actual_score} with {notation} would be correct."
                            )
                        else:
                            notation_issues.append(
                                f"Hole {idx+1}: notation='{notation}' implies score={expected_score} (par {par_vals[idx]}{offset:+d}), but extracted score={actual_score}. Re-read the digit."
                            )
            if notation_issues:
                player_entry["NOTATION_CONFLICTS"] = notation_issues
            if written_total and computed_total != written_total:
                player_entry["MISMATCH"] = f"Written total {written_total} != computed {computed_total} (diff={written_total - computed_total}). Find and fix errors."
            if written_front and front_9 != written_front:
                player_entry["FRONT_9_MISMATCH"] = f"Written OUT {written_front} != computed front 9 {front_9} (diff={written_front - front_9}). Error is in holes 1-9."
            if written_back and back_9 != written_back:
                player_entry["BACK_9_MISMATCH"] = f"Written IN {written_back} != computed back 9 {back_9} (diff={written_back - back_9}). Error is in holes 10-18."
            extracted_summary["players"].append(player_entry)

        low_conf = initial_result.get("low_confidence_holes", [])
        if low_conf:
            extracted_summary["low_confidence_holes"] = low_conf

        verify_prompt_filled = VERIFY_PROMPT.format(
            extracted_data=json.dumps(extracted_summary, indent=2)
        )

        raw_text = _call_gemini(verify_prompt_filled, image_bytes, media_type, model=MODEL_FAST)
        verify_result = _parse_json_response(raw_text)

        corrections_applied = []

        for corr in verify_result.get("corrections", []):
            player_name = corr.get("player")
            hole_num = corr.get("hole")
            new_val = corr.get("new_value")
            if player_name and hole_num is not None:
                for p in initial_result.get("players", []):
                    if p.get("name") == player_name:
                        idx = hole_num - 1
                        if 0 <= idx < len(p["holes"]):
                            old_val = p["holes"][idx]
                            int_new = int(new_val) if new_val is not None else None

                            w_front = p.get("front_9_total")
                            w_back = p.get("back_9_total")
                            if int_new is not None and old_val is not None and w_front and w_back:
                                holes_copy = p["holes"][:]
                                half = "front" if idx < 9 else "back"
                                h_start, h_end = (0, 9) if half == "front" else (9, 18)
                                w_half = w_front if half == "front" else w_back
                                old_half_sum = sum(h for h in holes_copy[h_start:h_end] if h is not None)
                                holes_copy[idx] = int_new
                                new_half_sum = sum(h for h in holes_copy[h_start:h_end] if h is not None)
                                if abs(new_half_sum - w_half) > abs(old_half_sum - w_half):
                                    continue

                            p["holes"][idx] = int_new
                            corrections_applied.append(
                                f"{player_name} hole {hole_num}: {old_val} -> {new_val} ({corr.get('reason', '')})"
                            )

        for corr in verify_result.get("par_corrections", []):
            hole_num = corr.get("hole")
            new_val = corr.get("new_value")
            if hole_num is not None:
                par = initial_result.get("par", [])
                idx = hole_num - 1
                if 0 <= idx < len(par):
                    par[idx] = int(new_val) if new_val is not None else 4

        for corr in verify_result.get("name_corrections", []):
            old_name = corr.get("old_name")
            new_name = corr.get("new_name")
            if old_name and new_name:
                for p in initial_result.get("players", []):
                    if p.get("name") == old_name:
                        p["name"] = new_name

        for corr in verify_result.get("notation_corrections", []):
            player_name = corr.get("player")
            hole_num = corr.get("hole")
            new_notation = corr.get("new_notation")
            if player_name and hole_num is not None and new_notation:
                for p in initial_result.get("players", []):
                    if p.get("name") == player_name:
                        notations = p.get("hole_notations", [])
                        idx = hole_num - 1
                        if 0 <= idx < len(notations):
                            notations[idx] = new_notation

        if verify_result.get("confidence"):
            initial_result["confidence"] = verify_result["confidence"]

        if corrections_applied:
            if "issues" not in initial_result:
                initial_result["issues"] = []
            initial_result["issues"].append(
                f"Verification pass corrected {len(corrections_applied)} value(s): " +
                "; ".join(corrections_applied)
            )
            initial_result["verification_corrections"] = corrections_applied

        initial_result["verified"] = verify_result.get("verified", True)

        par = initial_result.get("par", [])
        if len(par) != 18:
            par = strip_subtotal_columns(par)
            initial_result["par"] = par

        par = initial_result.get("par", [])
        if len(par) == 18:
            par_front_printed = initial_result.get("par_front_9_total")
            par_back_printed = initial_result.get("par_back_9_total")
            if par_front_printed and par_back_printed:
                pf = int(par_front_printed)
                pb = int(par_back_printed)
                comp_pf = sum(par[:9])
                comp_pb = sum(par[9:18])
                cur_diff = abs(comp_pf - pf) + abs(comp_pb - pb)
                swap_diff = abs(comp_pf - pb) + abs(comp_pb - pf)
                if swap_diff < cur_diff:
                    initial_result["par_front_9_total"] = par_back_printed
                    initial_result["par_back_9_total"] = par_front_printed
                    par_front_printed = par_back_printed
                    par_back_printed = initial_result["par_back_9_total"]
                    if "issues" not in initial_result:
                        initial_result["issues"] = []
                    initial_result["issues"].append(
                        f"Par subtotal swap fix: OUT/IN par totals were swapped"
                    )
            if par_front_printed:
                par_front_printed = int(par_front_printed)
                par_front_computed = sum(par[:9])
                if par_front_computed != par_front_printed:
                    diff = par_front_computed - par_front_printed
                    if abs(diff) <= 2:
                        for i in range(9):
                            for alt in [par[i] - diff]:
                                if alt in (3, 4, 5) and alt != par[i]:
                                    if "issues" not in initial_result:
                                        initial_result["issues"] = []
                                    initial_result["issues"].append(
                                        f"Par fix: hole {i+1} par {par[i]}->{alt} "
                                        f"(front 9 printed total={par_front_printed})"
                                    )
                                    par[i] = alt
                                    break
                            if sum(par[:9]) == par_front_printed:
                                break
            if par_back_printed:
                par_back_printed = int(par_back_printed)
                par_back_computed = sum(par[9:18])
                if par_back_computed != par_back_printed:
                    diff = par_back_computed - par_back_printed
                    if abs(diff) <= 2:
                        for i in range(9, 18):
                            for alt in [par[i] - diff]:
                                if alt in (3, 4, 5) and alt != par[i]:
                                    if "issues" not in initial_result:
                                        initial_result["issues"] = []
                                    initial_result["issues"].append(
                                        f"Par fix: hole {i+1} par {par[i]}->{alt} "
                                        f"(back 9 printed total={par_back_printed})"
                                    )
                                    par[i] = alt
                                    break
                            if sum(par[9:18]) == par_back_printed:
                                break
            initial_result["par"] = par

        for player in initial_result.get("players", []):
            holes = player.get("holes", [])
            if len(holes) != 18:
                holes = strip_subtotal_columns(holes)
                player["holes"] = holes
            valid = [h for h in holes if h is not None]
            if valid:
                computed_total = sum(valid)
                written_total = player.get("gross_total")
                player["written_gross_total"] = written_total
                player["gross_total"] = computed_total
                if player.get("front_9_total"):
                    player["front_9_total"] = int(player["front_9_total"])
                if player.get("back_9_total"):
                    player["back_9_total"] = int(player["back_9_total"])

        initial_result = _programmatic_crosscheck(initial_result)
        initial_result = _notation_crosscheck(initial_result)

        has_remaining_mismatch = False
        for p in initial_result.get("players", []):
            wt = p.get("written_gross_total")
            if wt and p.get("gross_total") != wt:
                has_remaining_mismatch = True
                break

        if has_remaining_mismatch:
            import time as _t2
            _t2.sleep(2)
            initial_result = _targeted_recheck(initial_result, image_bytes, media_type)
            initial_result = _programmatic_crosscheck(initial_result)
            initial_result = _notation_crosscheck(initial_result)

        for p in initial_result.get("players", []):
            wt = p.get("written_gross_total")
            gt = p.get("gross_total")
            if wt and gt != wt:
                p["total_mismatch"] = True
                p["mismatch_diff"] = gt - wt
                if "issues" not in initial_result:
                    initial_result["issues"] = []
                initial_result["issues"].append(
                    f"UNRESOLVED: {p.get('name', '?')} computed total {gt} "
                    f"still doesn't match written total {wt} (diff={gt - wt})"
                )
                initial_result["confidence"] = "MEDIUM"

        return initial_result

    except Exception as e:
        if "issues" not in initial_result:
            initial_result["issues"] = []
        initial_result["issues"].append(f"Verification pass failed: {str(e)}")
        initial_result["verified"] = False

        for player in initial_result.get("players", []):
            holes = player.get("holes", [])
            if len(holes) != 18:
                holes = strip_subtotal_columns(holes)
                player["holes"] = holes
            valid = [h for h in holes if h is not None]
            if valid:
                computed_total = sum(valid)
                written_total = player.get("gross_total")
                player["written_gross_total"] = written_total
                player["gross_total"] = computed_total
                if player.get("front_9_total"):
                    player["front_9_total"] = int(player["front_9_total"])
                if player.get("back_9_total"):
                    player["back_9_total"] = int(player["back_9_total"])

        initial_result = _programmatic_crosscheck(initial_result)
        initial_result = _notation_crosscheck(initial_result)
        return initial_result


def _fix_swapped_subtotals(result):
    if "issues" not in result:
        result["issues"] = []

    has_clear_swap = False
    player_data = []

    for player in result.get("players", []):
        written_front = player.get("front_9_total")
        written_back = player.get("back_9_total")
        written_total = player.get("gross_total")
        holes = player.get("holes", [])

        if written_front is None or written_back is None or len(holes) < 18:
            player_data.append(None)
            continue

        if written_total and written_front + written_back != written_total:
            player_data.append(None)
            continue

        comp_front = sum(h for h in holes[:9] if h is not None)
        comp_back = sum(h for h in holes[9:18] if h is not None)

        current_diff = abs(comp_front - written_front) + abs(comp_back - written_back)
        swapped_diff = abs(comp_front - written_back) + abs(comp_back - written_front)

        if swapped_diff < current_diff:
            has_clear_swap = True

        player_data.append({
            "player": player,
            "written_front": written_front,
            "written_back": written_back,
            "comp_front": comp_front,
            "comp_back": comp_back,
            "current_diff": current_diff,
            "swapped_diff": swapped_diff,
        })

    swap_direction = None
    for pd in player_data:
        if pd is None:
            continue
        if pd["swapped_diff"] < pd["current_diff"]:
            wf = pd["written_front"]
            wb = pd["written_back"]
            if wf > wb:
                swap_direction = "big_first"
            elif wb > wf:
                swap_direction = "small_first"
            break

    for pd in player_data:
        if pd is None:
            continue

        player = pd["player"]
        name = player.get("name", "?")
        wf = pd["written_front"]
        wb = pd["written_back"]

        do_swap = False
        if pd["swapped_diff"] < pd["current_diff"]:
            do_swap = True
        elif has_clear_swap and wf != wb and swap_direction:
            if swap_direction == "big_first" and wf < wb:
                do_swap = True
            elif swap_direction == "small_first" and wb < wf:
                do_swap = True

        if do_swap:
            player["front_9_total"], player["back_9_total"] = wb, wf
            result["issues"].append(
                f"Subtotal swap fix: {name} front/back subtotals were swapped "
                f"(OUT={wf}→{wb}, IN={wb}→{wf}). "
                f"Computed F9={pd['comp_front']}, B9={pd['comp_back']}."
            )

    return result


NOTATION_OFFSET = {
    "circle": -1,
    "double_circle": -2,
    "square": 1,
    "double_square": 2,
    "triangle": 3,
}


def _notation_crosscheck(result):
    par = result.get("par", [])
    if not par or len(par) < 18:
        return result

    if "issues" not in result:
        result["issues"] = []

    par_front_total = result.get("par_front_9_total")
    par_back_total = result.get("par_back_9_total")

    notation_par_votes = {}

    for player in result.get("players", []):
        notations = player.get("hole_notations", [])
        if not notations:
            continue

        holes = player.get("holes", [])
        name = player.get("name", "?")

        notation_count = sum(1 for n in notations if n in NOTATION_OFFSET)
        if notation_count > 10:
            result["issues"].append(
                f"Notation flood: {name} has {notation_count}/18 holes marked — "
                f"likely grid lines misread as shapes. Clearing all notations."
            )
            for i in range(len(notations)):
                notations[i] = "none"
            continue

        for idx, notation in enumerate(notations):
            if notation not in NOTATION_OFFSET:
                continue
            if idx >= len(holes) or idx >= len(par):
                continue
            if holes[idx] is None:
                continue

            if notation == "circle" and holes[idx] == par[idx] - 2:
                notations[idx] = "double_circle"
                notation = "double_circle"
                result["issues"].append(
                    f"Notation upgrade: {name} hole {idx+1} circle->double_circle "
                    f"(score {holes[idx]} = par {par[idx]} - 2 = eagle)"
                )

            offset = NOTATION_OFFSET[notation]
            actual = holes[idx]
            expected_from_par = par[idx] + offset

            implied_par = actual - offset
            if implied_par in (3, 4, 5) and implied_par != par[idx]:
                if idx not in notation_par_votes:
                    notation_par_votes[idx] = {}
                notation_par_votes[idx][implied_par] = notation_par_votes[idx].get(implied_par, 0) + 1

            if actual == expected_from_par:
                continue

            if expected_from_par >= 1 and expected_from_par <= 12:
                old_val = holes[idx]
                holes[idx] = expected_from_par
                player["gross_total"] = sum(h for h in holes if h is not None)
                result["issues"].append(
                    f"Notation fix: {name} hole {idx+1} {old_val}->{expected_from_par} "
                    f"(notation='{notation}' on par {par[idx]} implies score {expected_from_par})"
                )

    for player in result.get("players", []):
        notations = player.get("hole_notations", [])
        if not notations:
            continue
        holes = player.get("holes", [])
        name = player.get("name", "?")
        other_players = [p for p in result.get("players", []) if p.get("name") != name]

        for idx, notation in enumerate(notations):
            if notation != "circle" or idx >= len(par):
                continue
            if holes[idx] != par[idx] - 1:
                continue
            eagle_score = par[idx] - 2
            if eagle_score < 1:
                continue
            has_other_eagle = False
            for op in other_players:
                on = op.get("hole_notations", [])
                oh = op.get("holes", [])
                if idx < len(on) and idx < len(oh):
                    if on[idx] == "double_circle" or (on[idx] == "circle" and oh[idx] == eagle_score):
                        has_other_eagle = True
                        break
            if has_other_eagle:
                old_score = holes[idx]
                holes[idx] = eagle_score
                notations[idx] = "double_circle"
                player["gross_total"] = sum(h for h in holes if h is not None)
                result["issues"].append(
                    f"Eagle upgrade: {name} hole {idx+1} circle->double_circle, "
                    f"score {old_score}->{eagle_score} (another player also has eagle here)"
                )

    for idx, votes in notation_par_votes.items():
        if idx < len(par):
            best_par = max(votes, key=votes.get)
            vote_count = votes[best_par]
            if best_par != par[idx] and best_par in (3, 4, 5) and vote_count >= 1:
                old_par = par[idx]
                half = "front" if idx < 9 else "back"
                half_start, half_end = (0, 9) if half == "front" else (9, 18)
                printed_half_total = par_front_total if half == "front" else par_back_total

                if printed_half_total:
                    test_par = par[:]
                    test_par[idx] = best_par
                    new_half_sum = sum(test_par[half_start:half_end])
                    if new_half_sum != printed_half_total:
                        continue

                par[idx] = best_par
                result["issues"].append(
                    f"Notation-based par fix: hole {idx+1} par {old_par}->{best_par} "
                    f"(PGA notation on {vote_count} player score(s) implies par {best_par})"
                )

    return result


DIGIT_CONFUSIONS = {
    1: [7],
    3: [5, 8],
    4: [9, 7],
    5: [6, 3],
    6: [5, 8],
    7: [1, 4],
    8: [3, 6],
    9: [4],
}


def _programmatic_crosscheck(result):
    par = result.get("par", [])
    if "issues" not in result:
        result["issues"] = []

    for player in result.get("players", []):
        holes = player.get("holes", [])
        notations = player.get("hole_notations", [])

        for i in range(min(len(holes), len(par))):
            if holes[i] is None:
                continue
            hole_par = par[i] if i < len(par) else 4
            score = holes[i]
            if score < 1:
                holes[i] = 1
                result["issues"].append(
                    f"Floor fix: {player.get('name','?')} hole {i+1} {score}->1 (min score)"
                )
            elif score == 1 and hole_par >= 4:
                holes[i] = 4
                if i < len(notations):
                    notations[i] = "circle" if hole_par == 5 else "none"
                result["issues"].append(
                    f"Sanity fix: {player.get('name','?')} hole {i+1} 1->4 "
                    f"(hole-in-one on par {hole_par} is unrealistic, likely misread '4')"
                )
        player["holes"] = holes
        player["gross_total"] = sum(h for h in holes if h is not None)

    return result


TARGETED_RECHECK_PROMPT = """You are doing a FOCUSED re-examination of specific player scores on this golf scorecard.

FOR EACH PLAYER LISTED BELOW, re-read EVERY hole score from the image and provide the complete corrected set of 18 scores.

{player_details}

INSTRUCTIONS:
- Re-read each hole score fresh from the image. Do not assume the previous extraction was correct.
- The sum of the 18 hole scores IS the total. Do NOT rely on any written OUT/IN/TOT values on the card — the player may have added wrong.
- Read each digit carefully: 4 vs 9, 5 vs 6, 3 vs 8, 1 vs 7, column alignment.
- PGA NOTATION: Circle = birdie (par-1), Square = bogey (par+1). The score IS the digit inside the marking.
- Return ONLY compact JSON, no markdown.

Return this JSON:
{{"players":[{{"name":"player name","holes":[18 scores],"hole_notations":["none","circle",...],"notes":"what you changed"}}]}}"""


def _targeted_recheck(result, image_bytes, media_type):
    try:
        par = result.get("par", [])
        recheck_players = []
        for p in result.get("players", []):
            holes = p.get("holes", [])
            entry = {
                "name": p.get("name"),
                "current_holes": holes,
                "current_notations": p.get("hole_notations", []),
                "computed_total": sum(h for h in holes if h is not None),
            }
            recheck_players.append(entry)

        if not recheck_players:
            return result

        player_details = ""
        for mp in recheck_players:
            player_details += (
                f"\nPlayer: {mp['name']}\n"
                f"Current extracted holes: {mp['current_holes']}\n"
                f"Current notations: {mp['current_notations']}\n"
                f"Computed total (sum of holes): {mp['computed_total']}\n"
                f"Please re-read each hole score carefully from the image.\n"
            )

        prompt = TARGETED_RECHECK_PROMPT.format(player_details=player_details)

        raw_text = _call_gemini(prompt, image_bytes, media_type, model=MODEL_PRIMARY)

        try:
            recheck = _parse_json_response(raw_text)
        except json.JSONDecodeError:
            import time as _t3
            _t3.sleep(2)
            raw_text = _call_gemini(
                prompt + "\n\nIMPORTANT: Return ONLY valid JSON. No markdown, no extra text.",
                image_bytes, media_type, model=MODEL_PRIMARY
            )
            recheck = _parse_json_response(raw_text)

        if "issues" not in result:
            result["issues"] = []

        for rp in recheck.get("players", []):
            rp_name = rp.get("name")
            rp_holes = rp.get("holes", [])
            if len(rp_holes) != 18:
                rp_holes = strip_subtotal_columns(rp_holes)
            if len(rp_holes) != 18:
                continue

            for p in result.get("players", []):
                if p.get("name") != rp_name:
                    continue

                existing_notations = p.get("hole_notations", [])
                notation_locked = set()
                for ni, nn in enumerate(existing_notations):
                    if nn in NOTATION_OFFSET:
                        notation_locked.add(ni)

                old_holes = p.get("holes", [])
                merged_holes = list(old_holes)
                changes = []
                for i in range(min(18, len(rp_holes), len(old_holes))):
                    if rp_holes[i] is not None and rp_holes[i] != old_holes[i] and i not in notation_locked:
                        new_s = int(rp_holes[i])
                        if 1 <= new_s <= 12:
                            changes.append(f"hole {i+1}: {old_holes[i]}->{new_s}")
                            merged_holes[i] = new_s
                if changes:
                    merged_total = sum(h for h in merged_holes if h is not None)
                    p["holes"] = merged_holes
                    p["gross_total"] = merged_total
                    result["issues"].append(
                        f"Recheck corrected {rp_name}: {'; '.join(changes)} "
                        f"(total now {merged_total})"
                    )

                rp_notations = rp.get("hole_notations", [])
                if rp_notations and len(rp_notations) == 18:
                    p["hole_notations"] = rp_notations

        return result

    except Exception as e:
        if "issues" not in result:
            result["issues"] = []
        result["issues"].append(f"Targeted recheck failed: {str(e)}")
        return result


def process_ocr_for_round(image_path, round_data):
    result = ocr_scorecard(image_path)

    if result.get("error") and not result.get("players"):
        return result

    processed_players = []
    for player in result.get("players", []):
        holes = player.get("holes", [])

        valid_holes = [h for h in holes if h is not None]
        null_count = holes.count(None)

        calculated_gross = sum(valid_holes) if valid_holes else 0

        if player.get("gross_total") and valid_holes:
            if player["gross_total"] != calculated_gross and null_count == 0:
                if "issues" not in result:
                    result["issues"] = []
                result["issues"].append(
                    f"{player['name']}: Written total ({player['gross_total']}) "
                    f"doesn't match hole sum ({calculated_gross})"
                )

        while len(holes) < 18:
            holes.append(None)

        readable_holes = [h for h in holes[:18] if h is not None]
        calculated_gross = sum(readable_holes) if readable_holes else 0

        processed_player = {
            "name": player.get("name", "Unknown"),
            "holes": holes[:18],
            "gross_total": calculated_gross,
            "handicap": player.get("handicap"),
            "null_holes": null_count,
            "ocr_notes": player.get("notes", "")
        }
        processed_players.append(processed_player)

    result["processed_players"] = processed_players
    return result