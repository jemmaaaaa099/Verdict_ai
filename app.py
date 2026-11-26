"""Verdict AI - Know Your Rights. Flask backend.

Privacy: user questions are never written to disk or logged.
Gemini (optional) only receives knowledge-base facts, never the user's question.
"""
import json
import logging
import os
import urllib.request

from flask import Flask, jsonify, render_template, request

from nlp import Engine, is_urgent

app = Flask(__name__)
logging.getLogger("werkzeug").setLevel(logging.ERROR)  # no request logging

with open(os.path.join(app.root_path, "data", "knowledge_base.json"), encoding="utf-8") as f:
    KB = json.load(f)
ENGINE = Engine(KB)

GEMINI_KEY = os.environ.get("GEMINI_API_KEY")
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")  # verify current model name

DISCLAIMER = ("This is general information, not legal advice. Verdict AI is not a lawyer or a court "
              "and cannot decide who is right or wrong. Answers may be incomplete or out of date.")
AID_LINKS = [
    {"label": "NALSA - free legal aid (helpline 15100)", "url": "https://nalsa.gov.in"},
    {"label": "Tele-Law", "url": "https://www.tele-law.in"},
]


def rephrase(entry):
    """Ask Gemini to simplify the wording of KB facts only. Returns None on any problem."""
    if not GEMINI_KEY:
        return None
    facts = {"explanation": entry["explanation"], "next_steps": entry["next_steps"]}
    prompt = ("Rewrite the text below in simpler everyday English for someone with little legal "
              "knowledge. Use ONLY the facts given. Do not add laws, numbers, names or advice. "
              "Keep the same number of next_steps. Return JSON with keys 'explanation' (string) "
              "and 'next_steps' (list of strings).\n" + json.dumps(facts, ensure_ascii=False))
    body = json.dumps({"contents": [{"parts": [{"text": prompt}]}],
                       "generationConfig": {"responseMimeType": "application/json",
                                            "temperature": 0.2}}).encode()
    req = urllib.request.Request(
        f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent",
        data=body, headers={"Content-Type": "application/json", "x-goog-api-key": GEMINI_KEY})
    try:
        with urllib.request.urlopen(req, timeout=8) as r:
            data = json.load(r)
        out = json.loads(data["candidates"][0]["content"]["parts"][0]["text"])
        steps = out["next_steps"]
        if (isinstance(out["explanation"], str) and isinstance(steps, list)
                and len(steps) == len(entry["next_steps"])
                and all(isinstance(s, str) for s in steps)):
            return {"explanation": out["explanation"][:1500], "next_steps": [s[:500] for s in steps]}
    except Exception:
        pass
    return None


@app.after_request
def headers(resp):
    resp.headers["Content-Security-Policy"] = (
        "default-src 'self'; style-src 'self'; script-src 'self'; img-src 'self' data:; "
        "connect-src 'self'; base-uri 'none'; form-action 'self'; frame-ancestors 'none'")
    resp.headers["X-Content-Type-Options"] = "nosniff"
    resp.headers["Referrer-Policy"] = "no-referrer"
    if request.path.startswith("/api/"):
        resp.headers["Cache-Control"] = "no-store"
    return resp


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/ask", methods=["POST"])
def ask():
    payload = request.get_json(silent=True) or {}
    q = payload.get("question")
    if not isinstance(q, str) or len(q.strip()) < 3:
        return jsonify(error="Please type a question."), 400
    q = q.strip()[:500]
    urgent = is_urgent(q)
    found = ENGINE.match(q)
    if not found:
        return jsonify(matched=False, urgent=urgent, mode="Demo", sources=AID_LINKS,
                       disclaimer=DISCLAIMER,
                       message=("I could not find a good match for this in my knowledge base, and I "
                                "would rather say so than guess. Try rewording with simple words, "
                                "or contact free legal aid (NALSA helpline 15100)."))
    entry, confidence = found
    simple = rephrase(entry)
    return jsonify(
        matched=True, urgent=urgent, mode="Live AI" if simple else "Demo", confidence=confidence,
        title=entry["title"], category=entry["category"],
        explanation=simple["explanation"] if simple else entry["explanation"],
        rights=entry["rights"],
        next_steps=simple["next_steps"] if simple else entry["next_steps"],
        professional=entry["professional"], sources=entry["sources"], disclaimer=DISCLAIMER)


if __name__ == "__main__":
    app.run(host=os.environ.get("HOST", "127.0.0.1"), port=int(os.environ.get("PORT", 5000)),
            debug=False)
