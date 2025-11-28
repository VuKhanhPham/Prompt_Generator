"""
Prompt composition + simple scoring utilities.

Keep this logic very lightweight and transparent so
Vu can easily tweak the rating rules later.
"""

def compose_prompt(data: dict) -> str:
    """Build a structured prompt string from form fields."""
    purpose = (data.get("purpose") or "General message").strip()
    audience = (data.get("audience") or "a broad audience").strip()
    tone = (data.get("tone_label") or "Neutral").strip()
    keywords = (data.get("keywords") or "").strip()
    freeform = (data.get("freeform") or "").strip()

    parts = [
        f"Purpose: {purpose}.",
        f"Audience: {audience}.",
        f"Tone: {tone}."
    ]

    if keywords:
        parts.append(f"Keywords: {keywords}.")

    # Short, friendly instruction for the LLM
    parts.append("Please generate a clear, well-structured response.")

    if freeform:
        parts.append(freeform)

    return " ".join(parts)



def calculate_score(prompt: str,
                    input_keywords: str = "",
                    freeform_input: str = "") -> dict:
    """
    Scoring rule based on:
    - Clarity (0–30): Purpose + Audience (15 each)
    - Specificity (0–40): proportional to how many expected
      keyword/free-form “slots” are actually filled in the prompt
    - Tone match (0–30): has Tone
    - Length bonus (0–10): unchanged
    """
    import re

    # ----- Clarity & tone presence -----
    has_purpose = "Purpose:" in prompt
    has_audience = "Audience:" in prompt
    has_tone = "Tone:" in prompt

    # ----- Parse expected items from user input -----
    def parse_keywords(s: str):
        if not s:
            return []
        parts = re.split(r"[;,]", s)
        return [p.strip() for p in parts if p.strip()]

    expected_keywords = parse_keywords(input_keywords)
    expected_keywords_count = len(expected_keywords)

    # Free-form in the *input* counts as one expected “slot”
    expected_freeform = bool(freeform_input and freeform_input.strip())
    expected_items = expected_keywords_count + (1 if expected_freeform else 0)

    # ----- Parse what’s actually in the generated/edited prompt -----
    marker = "Please generate a clear, well-structured response."

    # Keywords actually present in the current prompt
    current_keywords = []
    if "Keywords:" in prompt:
        # Take everything after "Keywords:"
        after_kw = prompt.split("Keywords:", 1)[1]
        # Stop at the marker so we don't accidentally include the instruction text
        if marker in after_kw:
            after_kw = after_kw.split(marker, 1)[0]
        # Strip periods and split on comma/semicolon
        kw_text = after_kw.replace(".", " ")
        current_keywords = [
            kw.strip()
            for kw in re.split(r"[;,]", kw_text)
            if kw.strip()
        ]

    # Free-form present in the *prompt* (text after the marker)
    current_freeform_present = False
    if marker in prompt:
        after = prompt.split(marker, 1)[1]
        if after.strip():
            current_freeform_present = True

        current_items = len(current_keywords) + (1 if (current_freeform_present and expected_freeform) else 0)

    # ----- Clarity: max 30 -----
    clarity = 0
    if has_purpose:
        clarity += 15
    if has_audience:
        clarity += 15

    # ----- Specificity: max 40 -----
    # - expected_items comes from the Input Keywords + free-form input
    # - current_items is how many of those “slots” are actually filled now
    # - ratio = current / expected, capped at 1.0
    if expected_items > 0:
        matched_items = min(current_items, expected_items)
        ratio = matched_items / expected_items
        specificity = round(40.0 * min(ratio, 1.0), 2)
    else:
        # No expected specifics: just reward any specifics present, 10 pts each up to 40
        specificity = min(40.0, 10.0 * current_items)

    # ----- Tone match: max 30 -----
    tone_match = 30 if has_tone else 0

    # ----- Length bonus: unchanged (0–10) -----
    length_bonus = min(10, max(0, len(prompt) // 120))

    total = round(clarity + specificity + tone_match + length_bonus)

    return {
        "total": total,
        "details": {
            "clarity": clarity,
            "specificity": specificity,
            "tone_match": tone_match,
            "length_bonus": length_bonus,
        },
    }

def simulate_preview(prompt: str, tone_value: int) -> dict:
    """
    Optional helper if you ever want separate tone preview.
    Not currently used by composer.js but kept for future use.
    """
    if tone_value < 25:
        tone_name = "Formal"
        text = (
            f"This version keeps a professional, structured tone based on: "
            f"{prompt[:80]}..."
        )
    elif tone_value < 60:
        tone_name = "Friendly"
        text = (
            f"Here's a friendly, accessible version of your idea: "
            f"{prompt[:80]}..."
        )
    else:
        tone_name = "Witty"
        text = (
            f"Here's a more playful take on your idea: "
            f"{prompt[:80]}..."
        )

    return {"tone": tone_name, "text": text}