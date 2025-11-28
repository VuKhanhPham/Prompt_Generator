from flask import Blueprint, request, jsonify
from services.prompt_service import compose_prompt, calculate_score
import json
import os
import datetime

composer_bp = Blueprint("composer", __name__)

DATA_DIR = "data"
DATA_FILE = os.path.join(DATA_DIR, "prompts.json")


def ensure_data_file():
    """Make sure the storage folder and file exist."""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump([], f)


def read_data():
    ensure_data_file()
    with open(DATA_FILE, encoding="utf-8") as f:
        return json.load(f)


def write_data(data):
    ensure_data_file()
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


@composer_bp.route("/compose", methods=["POST"])
def compose():
    """
    Build a prompt string from user inputs and return it with a score.
    """
    payload = request.get_json() or {}

    prompt = compose_prompt(payload)

    # Use the original input fields to know what was "expected"
    input_keywords = (payload.get("keywords") or "")
    freeform_input = (payload.get("freeform") or "")

    score = calculate_score(
        prompt,
        input_keywords=input_keywords,
        freeform_input=freeform_input,
    )

    return jsonify({"prompt": prompt, "score": score})



@composer_bp.route("/save", methods=["POST"])
def save_prompt():
    """
    Save a composed prompt and its metadata into a local JSON file.
    Library routes will read from this same file.
    """
    payload = request.get_json() or {}

    all_prompts = read_data()

    new_entry = {
        "id": datetime.datetime.utcnow().strftime("%Y%m%d%H%M%S%f"),
        "purpose": payload.get("purpose", ""),
        "audience": payload.get("audience", ""),
        "tone_label": payload.get("tone_label", ""),
        "tone": payload.get("tone", 0),
        "keywords": payload.get("keywords", ""),
        "freeform": payload.get("freeform", ""),
        "prompt": payload.get("prompt", ""),
        "score": payload.get("score", {}),
        "timestamp": datetime.datetime.utcnow().isoformat(),
    }

    all_prompts.append(new_entry)
    write_data(all_prompts)

    return jsonify({"status": "saved", "id": new_entry["id"]})


@composer_bp.route("/recalculate_score", methods=["POST"])
def recalc_score():
    """
    Recalculate the score based on the editable prompt text.
    """
    payload = request.get_json() or {}
    prompt = payload.get("prompt", "") or ""

    # Expected slots still come from the original form inputs
    input_keywords = (payload.get("input_keywords") or "")
    freeform_input = (payload.get("freeform_input") or "")

    score = calculate_score(
        prompt,
        input_keywords=input_keywords,
        freeform_input=freeform_input,
    )
    return jsonify(score)
