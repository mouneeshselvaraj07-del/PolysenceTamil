import streamlit as st
import json
import random
import os
import re
import time

try:
    from groq import Groq as GroqClient
    GROQ_PKG = True
except ImportError:
    GROQ_PKG = False

st.set_page_config(page_title="PolySense Tamil", page_icon="🌿",
                   layout="wide", initial_sidebar_state="collapsed")

# ─────────────────────────── CSS ────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Tamil:wght@400;600;700&family=Sora:wght@400;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');

html, body, [class*="css"] { font-family:'Sora',sans-serif; }

/* ── Core palette ── */
:root {
  --bg: #0d0f1a;
  --surface: #151827;
  --surface2: #1c2035;
  --border: #2a2f4a;
  --accent: #6c63ff;
  --accent2: #ff6b9d;
  --gold: #ffd166;
  --green: #06d6a0;
  --red: #ef233c;
  --text: #e8eaf6;
  --muted: #7b82a6;
}

.stApp { background: var(--bg) !important; color: var(--text) !important; }

/* ── Tamil fonts ── */
.tamil-word     { font-family:'Noto Sans Tamil',sans-serif; font-size:2.8rem; font-weight:700; color:#fff; letter-spacing:-1px; }
.tamil-text     { font-family:'Noto Sans Tamil',sans-serif; font-size:1.05rem; line-height:2; }
.tamil-sentence { font-family:'Noto Sans Tamil',sans-serif; font-size:1.4rem; font-weight:600; line-height:2.2; color:#fff; }

/* ── Hero ── */
.hero-header {
  background: linear-gradient(135deg, #1a1040 0%, #0d0f1a 40%, #0a1628 100%);
  border: 1px solid var(--border);
  border-radius: 20px; padding: 2.5rem 3rem;
  text-align: center; margin-bottom: 1.5rem;
  position: relative; overflow: hidden;
}
.hero-header::before {
  content: ''; position: absolute; top: -60px; left: -60px;
  width: 220px; height: 220px; background: radial-gradient(circle, #6c63ff33, transparent 70%);
  border-radius: 50%;
}
.hero-header h1 { color: #fff; font-size: 2.4rem; font-weight: 800; margin: 0.3rem 0; }
.hero-header p  { color: var(--muted); margin: 0; font-size: 0.95rem; }
.hero-badge     { display:inline-block; background:var(--accent); color:white; padding:0.2rem 0.9rem; border-radius:20px; font-size:0.75rem; font-weight:700; margin-bottom:0.6rem; letter-spacing:1px; }
.ai-badge       { display:inline-block; background:#1c2035; color:var(--green); border:1px solid var(--green); border-radius:20px; padding:0.25rem 0.9rem; font-size:0.78rem; font-weight:600; margin-top:0.6rem; }

/* ── Cards ── */
.word-card {
  background: var(--surface); border: 1px solid var(--border);
  border-radius: 16px; padding: 1.5rem 2rem; text-align: center; margin-bottom: 1.2rem;
}
.transliteration { color: var(--muted); font-size: 1rem; font-style: italic; margin-top: 0.3rem; font-family: 'JetBrains Mono', monospace; }

/* ── Sentence box ── */
.sentence-box {
  background: var(--surface2); border-left: 4px solid var(--gold);
  border-radius: 0 14px 14px 0; padding: 1.2rem 1.5rem; margin: 1rem 0;
}
.blank-word { color: var(--gold); font-weight: 700; letter-spacing: 1px; }

/* ── POS pills ── */
.pill-pos  { border-radius: 20px; padding: 0.15rem 0.65rem; font-size: 0.72rem; font-weight: 700; letter-spacing: 0.5px; }
.pill-noun { background: #1a2f4a; color: #60b0ff; border: 1px solid #2a4a6a; }
.pill-verb { background: #2d1a0a; color: #ffb347; border: 1px solid #4a3a1a; }

/* ── Score pill ── */
.score-pill { background: var(--accent); color: white; border-radius: 20px; padding: 0.3rem 1.2rem; font-weight: 700; font-size: 1.1rem; display: inline-block; }

/* ── Feedback ── */
.feedback-card {
  background: linear-gradient(135deg, #1a1040, #0d0f1a);
  border: 1px solid var(--accent);
  color: white; border-radius: 20px; padding: 2.5rem; text-align: center; margin-bottom: 1.2rem;
}
.feedback-stat  { font-size: 3rem; font-weight: 800; color: var(--gold); }
.feedback-label { font-size: 0.9rem; color: var(--muted); }

/* ── Tip cards ── */
.improve-card {
  background: #1a0d0d; border: 1.5px solid #4a1a1a;
  border-radius: 14px; padding: 1rem 1.3rem; margin: 0.5rem 0;
}
.improve-card h4 { color: #ff8a80; margin: 0 0 0.4rem 0; font-size: 0.95rem; }
.improve-card p  { color: #ccb0b0; margin: 0; font-size: 0.88rem; line-height: 1.6; }
.tip-box {
  background: #0d1a11; border: 1.5px solid #1a4a28;
  border-radius: 14px; padding: 1rem 1.3rem; margin: 0.5rem 0;
}
.tip-box h4 { color: var(--green); margin: 0 0 0.4rem 0; font-size: 0.95rem; }
.tip-box p  { color: #a0ccb0; margin: 0; font-size: 0.88rem; line-height: 1.6; }

/* ── Semantic web nodes ── */
.sem-node-root    { background: var(--accent); color: white; border-radius: 50px; padding: 0.5rem 1.8rem; font-family: 'Noto Sans Tamil', sans-serif; font-size: 1.2rem; font-weight: 700; display: inline-block; box-shadow: 0 0 20px #6c63ff55; }
.sem-node-meaning { background: var(--accent2); color: white; border-radius: 12px; padding: 0.5rem 1rem; font-size: 0.9rem; font-weight: 700; display: inline-block; }
.sem-node-context { background: var(--surface2); border: 1.5px solid var(--border); border-radius: 12px; padding: 0.7rem 1rem; font-size: 0.82rem; color: var(--text); }

/* ── Hallucination badge ── */
.halu-ok   { background:#0d1a11; color:var(--green); border:1px solid var(--green); border-radius:8px; padding:0.2rem 0.7rem; font-size:0.75rem; font-weight:700; }
.halu-warn { background:#1a1000; color:var(--gold);  border:1px solid var(--gold);  border-radius:8px; padding:0.2rem 0.7rem; font-size:0.75rem; font-weight:700; }
.halu-flag { background:#1a0d0d; color:#ff6b6b;      border:1px solid #ff6b6b;      border-radius:8px; padding:0.2rem 0.7rem; font-size:0.75rem; font-weight:700; }

/* ── Sem tip ── */
.sem-tip { background: var(--surface2); border: 1px solid var(--accent); border-radius: 16px; padding: 1.3rem 1.8rem; margin: 1rem 0; text-align: center; }
.sem-tip h3 { color: var(--gold); margin: 0 0 0.4rem 0; font-size: 1.1rem; }
.sem-tip p  { color: var(--muted); margin: 0; font-size: 0.9rem; }

/* ── Morph table ── */
.morph-table { width: 100%; border-collapse: collapse; }
.morph-table th { background: var(--surface2); color: var(--muted); font-size: 0.8rem; font-weight: 600; padding: 0.5rem 1rem; text-align: left; border-bottom: 1px solid var(--border); }
.morph-table td { padding: 0.55rem 1rem; border-bottom: 1px solid #1a1f35; font-size: 0.88rem; }
.morph-table tr:hover td { background: var(--surface2); }
.morph-form { font-family: 'Noto Sans Tamil', sans-serif; font-size: 1rem; color: #fff; font-weight: 600; }

/* ── Progress bar ── */
.stProgress > div > div { background: var(--accent) !important; }

/* ── Streamlit overrides ── */
div[data-testid='stHorizontalBlock'] button {
    font-family:'Noto Sans Tamil',sans-serif !important;
    font-size:1.05rem !important; font-weight:600 !important;
    min-height:62px !important; border-radius:12px !important;
    white-space:normal !important; word-wrap:break-word !important;
    background: var(--surface2) !important; border: 1.5px solid var(--border) !important;
    color: var(--text) !important;
}
div[data-testid='stHorizontalBlock'] button:hover {
    border-color: var(--accent) !important; color: #fff !important;
}
.stButton > button[kind="primary"] {
    background: var(--accent) !important; border: none !important; color: #fff !important;
}
.stTextInput input, .stSelectbox select {
    background: var(--surface2) !important; border: 1.5px solid var(--border) !important;
    color: var(--text) !important; border-radius: 10px !important;
}
#MainMenu, footer { visibility: hidden; }

/* ── Word grid buttons ── */
.word-btn-wrap button {
    background: var(--surface) !important; border: 1.5px solid var(--border) !important;
    border-radius: 14px !important; color: var(--text) !important;
    transition: border-color 0.2s !important;
}
.word-btn-wrap button:hover { border-color: var(--accent) !important; }

/* ── HITL Panel ── */
.hitl-panel {
  background: #0d1220; border: 1.5px solid #2a3a5a;
  border-radius: 14px; padding: 1rem 1.3rem; margin: 0.5rem 0;
}
.hitl-panel h4 { color: #60b0ff; margin: 0 0 0.4rem 0; font-size: 0.92rem; }
.hitl-panel p  { color: #8aa0c0; margin: 0; font-size: 0.84rem; line-height: 1.6; }
.hitl-rule-pass { color: var(--green); font-weight: 700; }
.hitl-rule-fail { color: #ff6b6b; font-weight: 700; }
.hitl-rule-warn { color: var(--gold); font-weight: 700; }
</style>
""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════
# ██  API KEY  ██
GROQ_API_KEY = "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"
# ════════════════════════════════════════════════════

GROQ_MODEL    = "llama-3.3-70b-versatile"
NUM_QUESTIONS = 5


# ──────────────────────────── Dataset ─────────────────────────────────────────
@st.cache_data
def load_dataset():
    path = os.path.join(os.path.dirname(__file__), "tamil_words.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

DATASET = load_dataset()


# ──────────────────────────── AI helpers ──────────────────────────────────────
def call_ai(prompt: str, retries: int = 3):
    import http.client, ssl
    key = GROQ_API_KEY or os.environ.get("GROQ_API_KEY", "")
    if not key:
        st.error("No API key found.")
        return None

    if GROQ_PKG:
        for attempt in range(retries):
            try:
                client = GroqClient(api_key=key)
                chat   = client.chat.completions.create(
                    model=GROQ_MODEL,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7, max_tokens=1200,
                )
                return chat.choices[0].message.content
            except Exception as e:
                err = str(e)
                if "429" in err or "rate" in err.lower():
                    wait = 5 * (attempt + 1)
                    st.toast(f"Rate limit — waiting {wait}s…")
                    time.sleep(wait); continue
                st.error(f"❌ AI error: {err[:200]}")
                return None
        st.error("Too many requests. Please wait 30s and try again.")
        return None

    body = json.dumps({"model": GROQ_MODEL,
                       "messages": [{"role": "user", "content": prompt}],
                       "temperature": 0.7, "max_tokens": 1200})
    headers = {"Content-Type": "application/json",
               "Authorization": "Bearer " + key,
               "User-Agent": "polysense/1.0", "Accept": "application/json"}
    for attempt in range(retries):
        try:
            conn = http.client.HTTPSConnection(
                "api.groq.com", timeout=30, context=ssl.create_default_context())
            conn.request("POST", "/openai/v1/chat/completions",
                         body=body, headers=headers)
            resp      = conn.getresponse()
            resp_body = resp.read().decode("utf-8")
            conn.close()
            if resp.status == 200:
                return json.loads(resp_body)["choices"][0]["message"]["content"]
            elif resp.status == 429:
                time.sleep(5 * (attempt + 1)); continue
            else:
                st.error(f"❌ AI error {resp.status}: {resp_body[:200]}")
                return None
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(3); continue
            st.error(f"❌ Connection error: {e}")
            return None
    return None


def clean_json(raw: str) -> str:
    raw = raw.strip()
    raw = re.sub(r"^```json\s*", "", raw)
    raw = re.sub(r"^```\s*",     "", raw)
    raw = re.sub(r"\s*```$",     "", raw)
    return raw.strip()


# ══════════════════════════════════════════════════════════════════════════════
# ██  HUMAN-IN-THE-LOOP VALIDATION ENGINE  ██
# Rule-based + AI self-check to catch hallucinations before showing to user
# ══════════════════════════════════════════════════════════════════════════════

def rule_based_checks(sentence: str, correct_answer: str, distractors: list) -> dict:
    """
    Fast, deterministic rule checks that run BEFORE AI validation.
    Returns a structured report of pass/warn/fail per rule.
    """
    rules = []

    # Rule 1: Sentence must contain a blank marker
    has_blank = "_____" in sentence or "______" in sentence or "___" in sentence
    rules.append({
        "rule": "Blank marker present",
        "status": "pass" if has_blank else "fail",
        "detail": "Sentence must contain _____ for the learner to fill in."
    })

    # Rule 2: Correct answer must not be empty
    rules.append({
        "rule": "Correct answer non-empty",
        "status": "pass" if correct_answer and correct_answer.strip() else "fail",
        "detail": "The correct answer field cannot be blank."
    })

    # Rule 3: Must have at least 3 distractors
    valid_distractors = [d for d in (distractors or []) if d and d.strip()]
    rules.append({
        "rule": "Sufficient distractors (≥3)",
        "status": "pass" if len(valid_distractors) >= 3 else "warn",
        "detail": f"Found {len(valid_distractors)} distractor(s). Need at least 3."
    })

    # Rule 4: Correct answer must differ from all distractors
    answer_unique = correct_answer.strip() not in [d.strip() for d in valid_distractors]
    rules.append({
        "rule": "Correct answer ≠ distractors",
        "status": "pass" if answer_unique else "fail",
        "detail": "The correct answer must not appear in the distractor list."
    })

    # Rule 5: Sentence length sanity (Tamil sentences should be reasonable)
    words = sentence.split()
    rules.append({
        "rule": "Sentence length reasonable (3–30 words)",
        "status": "pass" if 3 <= len(words) <= 30 else "warn",
        "detail": f"Sentence has {len(words)} word tokens."
    })

    # Rule 6: All options should be unique
    all_opts = [correct_answer.strip()] + [d.strip() for d in valid_distractors]
    all_unique = len(all_opts) == len(set(all_opts))
    rules.append({
        "rule": "All 4 options are unique",
        "status": "pass" if all_unique else "fail",
        "detail": "Duplicate options detected — each choice must be distinct."
    })

    # Rule 7: Tamil script presence in sentence
    tamil_chars = sum(1 for ch in sentence if '\u0B80' <= ch <= '\u0BFF')
    rules.append({
        "rule": "Tamil script detected in sentence",
        "status": "pass" if tamil_chars >= 3 else "warn",
        "detail": f"Found {tamil_chars} Tamil Unicode characters in sentence."
    })

    # Aggregate
    fail_count = sum(1 for r in rules if r["status"] == "fail")
    warn_count = sum(1 for r in rules if r["status"] == "warn")

    if fail_count > 0:
        verdict = "reject"
        confidence = max(10, 40 - fail_count * 10)
    elif warn_count > 1:
        verdict = "warn"
        confidence = 65
    else:
        verdict = "valid"
        confidence = 88

    return {
        "rules": rules,
        "verdict": verdict,
        "confidence": confidence,
        "fail_count": fail_count,
        "warn_count": warn_count
    }


def validate_sentence(word: str, sentence: str, meaning: str, correct_form: str,
                      distractors: list = None) -> dict:
    """
    Two-stage Human-in-the-Loop validation:
    Stage 1 — deterministic rule checks (fast, free)
    Stage 2 — AI self-review (slower, catches semantic issues)
    Results are merged into a unified confidence score.
    """
    # Stage 1: Rule-based
    rule_report = rule_based_checks(sentence, correct_form, distractors or [])

    # If rule checks already reject it, skip expensive AI call
    if rule_report["verdict"] == "reject":
        return {
            "confidence": rule_report["confidence"],
            "issues": [r["detail"] for r in rule_report["rules"] if r["status"] == "fail"],
            "verdict": "reject",
            "rule_report": rule_report,
            "stage": "rules_only"
        }

    # Stage 2: AI self-check
    prompt = f"""You are a Tamil language expert and quality checker. Evaluate this AI-generated quiz item:

Tamil root word: {word}
Correct form used: {correct_form}
Meaning being tested: {meaning}
Sentence: {sentence}
Distractors: {', '.join(distractors or [])}

Check ALL of the following:
1. Is the Tamil sentence grammatically correct? (gender agreement, verb agreement)
2. Does _____ in the sentence clearly need '{correct_form}' specifically (not the distractors)?
3. Is the meaning of '{correct_form}' actually '{meaning}' in this context?
4. Are the distractors plausible but clearly wrong in this sentence?
5. Is the sentence natural and non-awkward Tamil?

Return ONLY this JSON, no extra text:
{{
  "grammar_ok": true or false,
  "answer_fits": true or false,
  "meaning_correct": true or false,
  "distractors_plausible": true or false,
  "natural": true or false,
  "issues": ["list any specific issues found, empty array if none"],
  "ai_confidence": 0-100,
  "verdict": "valid" or "warn" or "reject"
}}"""

    raw = call_ai(prompt)
    ai_result = {"ai_confidence": 70, "issues": [], "verdict": "warn",
                 "grammar_ok": None, "answer_fits": None,
                 "meaning_correct": None, "distractors_plausible": None,
                 "natural": None}
    if raw:
        try:
            ai_result = json.loads(clean_json(raw))
        except Exception:
            m = re.search(r'\{.*\}', raw, re.DOTALL)
            if m:
                try: ai_result = json.loads(m.group())
                except: pass

    # Merge Stage 1 + Stage 2
    rule_conf = rule_report["confidence"]
    ai_conf   = ai_result.get("ai_confidence", 70)
    merged_conf = int(rule_conf * 0.4 + ai_conf * 0.6)

    all_issues = ([r["detail"] for r in rule_report["rules"] if r["status"] == "fail"]
                  + ai_result.get("issues", []))

    # Final verdict: take the worse of the two
    verdict_rank = {"reject": 0, "warn": 1, "valid": 2}
    rule_v = rule_report["verdict"]
    ai_v   = ai_result.get("verdict", "warn")
    final_verdict = rule_v if verdict_rank[rule_v] <= verdict_rank[ai_v] else ai_v

    return {
        "confidence": merged_conf,
        "issues": all_issues,
        "verdict": final_verdict,
        "rule_report": rule_report,
        "ai_checks": {
            "grammar_ok": ai_result.get("grammar_ok"),
            "answer_fits": ai_result.get("answer_fits"),
            "meaning_correct": ai_result.get("meaning_correct"),
            "distractors_plausible": ai_result.get("distractors_plausible"),
            "natural": ai_result.get("natural"),
        },
        "stage": "full_validation"
    }


def render_hitl_badge(validation: dict):
    """Render a compact Human-in-the-Loop badge with tooltip info."""
    verdict = validation.get("verdict", "warn")
    conf    = validation.get("confidence", 70)
    stage   = validation.get("stage", "")
    stage_label = "2-Stage HITL" if stage == "full_validation" else "Rules Only"

    if verdict == "valid":
        return f"<span class='halu-ok'>✓ Validated {conf}% · {stage_label}</span>"
    elif verdict == "warn":
        return f"<span class='halu-warn'>⚠ Review {conf}% · {stage_label}</span>"
    else:
        return f"<span class='halu-flag'>✗ Flagged · {stage_label}</span>"


def render_hitl_detail_panel(validation: dict):
    """Show full HITL validation breakdown in an expander."""
    rule_report = validation.get("rule_report", {})
    ai_checks   = validation.get("ai_checks", {})
    rules       = rule_report.get("rules", [])

    status_icon = {"pass": "✅", "warn": "⚠️", "fail": "❌"}
    status_cls  = {"pass": "hitl-rule-pass", "warn": "hitl-rule-warn", "fail": "hitl-rule-fail"}

    rows = "".join(
        f"<tr><td>{r['rule']}</td>"
        f"<td class='{status_cls.get(r['status'], '')}' style='font-size:0.82rem;'>"
        f"{status_icon.get(r['status'], '?')}</td>"
        f"<td style='color:var(--muted);font-size:0.78rem;'>{r['detail']}</td></tr>"
        for r in rules
    )

    ai_rows = ""
    if ai_checks:
        check_map = {
            "grammar_ok": "Grammar correct",
            "answer_fits": "Answer fits blank",
            "meaning_correct": "Meaning matches",
            "distractors_plausible": "Distractors plausible",
            "natural": "Sentence natural",
        }
        for key, label in check_map.items():
            val = ai_checks.get(key)
            icon = "✅" if val is True else "❌" if val is False else "❓"
            ai_rows += f"<tr><td>{label}</td><td>{icon}</td><td></td></tr>"

    st.markdown(f"""
    <div class='hitl-panel'>
      <h4>🔍 Human-in-the-Loop Validation Report</h4>
      <p style='margin-bottom:0.5rem;font-size:0.78rem;'>
        Stage 1: Deterministic Rule Checks &nbsp;|&nbsp; Stage 2: AI Self-Review
      </p>
      <table style='width:100%;border-collapse:collapse;font-size:0.82rem;'>
        <thead><tr>
          <th style='text-align:left;color:var(--muted);padding:0.3rem 0.5rem;'>Check</th>
          <th style='color:var(--muted);padding:0.3rem 0.5rem;'>Status</th>
          <th style='text-align:left;color:var(--muted);padding:0.3rem 0.5rem;'>Detail</th>
        </tr></thead>
        <tbody>{rows}{ai_rows}</tbody>
      </table>
    </div>""", unsafe_allow_html=True)

    issues = validation.get("issues", [])
    if issues:
        st.caption("Issues found: " + " · ".join(issues[:3]))


# ──────────────────────────── Custom word analysis ───────────────────────────
def analyze_custom_word(word_ta: str, word_translit: str = ""):
    prompt = f"""You are an expert Tamil linguist. Analyze the Tamil word '{word_ta}' ({word_translit}).

Identify 2-4 distinct polysemous meanings (different POS categories if applicable).

Return ONLY this JSON, no extra text:
{{
  "word": "{word_ta}",
  "transliteration": "{word_translit or word_ta}",
  "senses": [
    {{
      "meaning_en": "English meaning",
      "meaning_ta": "Tamil definition (5-8 words)",
      "pos": "noun" or "verb" or "adjective",
      "example_sentence_ta": "Short Tamil example sentence using this word"
    }}
  ]
}}

Include only genuine, distinct meanings. No hallucination."""

    raw = call_ai(prompt)
    if not raw:
        return None
    try:
        return json.loads(clean_json(raw))
    except Exception:
        m = re.search(r'\{.*\}', raw, re.DOTALL)
        if m:
            try: return json.loads(m.group())
            except: pass
        return None


# ──────────────────────────── Morphological variants ─────────────────────────
def generate_morphological_variants(word_obj, sense):
    word    = word_obj["word"]
    translit = word_obj["transliteration"]
    meaning  = sense["meaning_en"]
    pos      = sense["pos"]

    if pos == "verb":
        prompt = f"""For the Tamil verb root '{word}' ({translit}) meaning '{meaning}',
generate 6 morphological conjugation forms covering:
- past tense masculine, past tense feminine, present tense plural,
  future tense, infinitive, verbal noun.

Return ONLY JSON array, no extra text:
[
  {{"form": "Tamil form", "label": "Past masc.", "transliteration": "...", "example": "Short Tamil sentence"}}
]"""
    else:
        prompt = f"""For the Tamil noun '{word}' ({translit}) meaning '{meaning}',
generate 6 morphological case forms:
- nominative, accusative (-ஐ), dative (-க்கு), locative (-இல்), instrumental (-ஆல்), sociative (-உடன்).

Return ONLY JSON array, no extra text:
[
  {{"form": "Tamil form", "label": "Nominative", "transliteration": "...", "example": "Short Tamil sentence"}}
]"""

    raw = call_ai(prompt)
    if not raw:
        return None
    try:
        return json.loads(clean_json(raw))
    except Exception:
        m = re.search(r'\[.*\]', raw, re.DOTALL)
        if m:
            try: return json.loads(m.group())
            except: pass
        return None


# ──────────────────────────── Question generator ─────────────────────────────
def generate_question(word_obj, sense, validate=True):
    word     = word_obj["word"]
    translit = word_obj["transliteration"]
    meaning  = sense["meaning_en"]
    pos      = sense["pos"]
    other    = ", ".join(s["meaning_en"] for s in word_obj["senses"] if s["meaning_en"] != meaning)

    # ── Inject user corrections so AI avoids past mistakes ──
    corrections = st.session_state.get("user_corrections", [])
    corrections_block = ""
    if corrections:
        lines = "\n".join(f"  • {c['feedback']}" for c in corrections[-8:])
        corrections_block = f"""

⚠️ USER-REPORTED CORRECTIONS (apply these lessons to every question you generate):
{lines}
Make sure NONE of the above errors occur in the new question."""

    prompt = f"""You are an expert Tamil language teacher creating a polysemy quiz.

Tamil root word: {word} ({translit})
Meaning to test: "{meaning}" (POS: {pos})
Other meanings of same word: {other}

Create a fill-in-the-blank sentence. ALL 4 options must be different grammatical/case forms of the SAME root word {word}.

Examples:
- Root ஆறு → ஆற்றில், ஆற்றை, ஆற்றுக்கு, ஆறாக
- Root படி → படிக்கிறான், படித்தான், படிப்பான், படிப்பதற்கு
- Root கல் → கல்லை, கல்லில், கல்லுக்கு, கல்லாக
{corrections_block}
Return ONLY this JSON, no extra text:
{{
  "sentence": "Tamil sentence with _____ where the correct form of {word} meaning '{meaning}' fits",
  "sentence_translation": "English translation of full sentence",
  "correct_answer": "correct Tamil form of {word}",
  "distractors": ["form2 of {word}", "form3 of {word}", "form4 of {word}"],
  "explanation": "1-2 English sentences: why this form fits and why others do not"
}}

RULES:
- sentence in Tamil script only
- ALL 4 options = different suffixes/forms of root word {word}
- Return ONLY valid JSON"""

    raw = call_ai(prompt)
    if not raw:
        return None
    try:
        q = json.loads(clean_json(raw))
    except Exception:
        m = re.search(r'\{.*\}', raw, re.DOTALL)
        if not m:
            return None
        try:
            q = json.loads(m.group())
        except:
            return None

    # ── Human-in-the-Loop: Two-stage validation ──
    if validate:
        check = validate_sentence(
            word,
            q.get("sentence", ""),
            meaning,
            q.get("correct_answer", ""),
            q.get("distractors", [])
        )
        q["validation"] = check
    else:
        q["validation"] = {"confidence": 85, "issues": [], "verdict": "valid",
                           "stage": "skipped"}

    return q


# ──────────────────────────── Semantic web data ───────────────────────────────
def generate_semantic_web(word_obj):
    word = word_obj["word"]
    senses_text = "\n".join(
        f"  {i+1}. {s['meaning_en']} ({s['pos']})"
        for i, s in enumerate(word_obj["senses"])
    )
    prompt = f"""For the Tamil word '{word}', give rich context for each meaning.

Meanings:
{senses_text}

Return ONLY a JSON array (same order, one object per meaning):
[
  {{
    "meaning_en": "...",
    "example_ta": "Short Tamil phrase/sentence (5-8 words) using this meaning",
    "example_en": "English translation of the example",
    "context_clue": "One English sentence about when/where this meaning is used",
    "related_words": ["1-2 Tamil related words (transliteration ok)"]
  }}
]"""

    raw = call_ai(prompt)
    if not raw:
        return None
    try:
        return json.loads(clean_json(raw))
    except Exception:
        m = re.search(r'\[.*\]', raw, re.DOTALL)
        if m:
            try: return json.loads(m.group())
            except: pass
        return None


def generate_feedback(word, score, total, wrong_senses):
    pct = int((score / total) * 100) if total else 0
    wrong_str = ", ".join(wrong_senses) if wrong_senses else "none"
    prompt = f"""A student completed a Tamil polysemy quiz on the word '{word}'.
Score: {score}/{total} ({pct}%)
Meanings they got wrong: {wrong_str}

Give 2-3 short, specific, encouraging improvement tips in English.
Return ONLY a JSON array:
[
  {{"title": "short tip title", "tip": "one or two sentence explanation"}},
  ...
]
No extra text."""
    raw = call_ai(prompt)
    if not raw:
        return None
    try:
        return json.loads(clean_json(raw))
    except Exception:
        m = re.search(r'\[.*\]', raw, re.DOTALL)
        if m:
            try: return json.loads(m.group())
            except: pass
        return None


# ──────────────────────────── Session state ──────────────────────────────────
_DEFAULTS = {
    "screen": "home", "selected_word": None,
    "questions": [], "current_q": 0, "score": 0, "answers": [],
    "shuffled_options": [], "answered": False, "chosen": None,
    "sem_web_data": None, "ai_feedback": None,
    "drag_mode": False,
    "drag_placed": {},
    "drag_submitted": False,
    "drag_questions": [],
    "drag_shuffled": None,
    "morph_data": {},
    "custom_word_data": None,
    # Drag & Drop (Streamlit-native click-to-place)
    "drag_selected_chip": None,   # currently "held" chip
    "drag_placements": {},         # {sentence_index: word_text}
    # User feedback / AI corrections
    "user_corrections": [],        # [{question, feedback, timestamp}]
}
for k, v in _DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ──────────────────────────── Header ─────────────────────────────────────────
st.markdown("""
<div class="hero-header">
  <div class="hero-badge">AI POWERED · LLaMA 3.3</div>
  <h1>🌿 PolySense Tamil</h1>
  <p>Context-Aware Tamil Polysemy Game Engine · Morphology · Semantic Web · Drag &amp; Drop</p>
  <div><span class="ai-badge">✦ 2-Stage Human-in-the-Loop Validation · Dynamic Generation</span></div>
</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# HOME
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.screen == "home":

    st.markdown("### 📚 Choose a Tamil Word to Learn")

    cols = st.columns(4)
    for i, w in enumerate(DATASET["words"]):
        with cols[i % 4]:
            st.markdown('<div class="word-btn-wrap">', unsafe_allow_html=True)
            if st.button(
                f"**{w['word']}**\n\n_{w['transliteration']}_\n\n`{len(w['senses'])} meanings`",
                key=f"w_{i}", use_container_width=True
            ):
                st.session_state.selected_word = w
                st.session_state.screen = "word_detail"
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")

    st.markdown("### 🔍 Analyse Your Own Tamil Word")
    st.caption("Enter any polysemous Tamil word to generate senses, quiz, and semantic web on-the-fly using AI.")

    col_w, col_t, col_b = st.columns([2, 2, 1])
    with col_w:
        custom_ta     = st.text_input("Tamil word (Tamil script)", placeholder="e.g. வேர்", key="custom_ta_input")
    with col_t:
        custom_translit = st.text_input("Transliteration (optional)", placeholder="e.g. vēr", key="custom_translit_input")
    with col_b:
        st.markdown("<div style='margin-top:1.7rem;'></div>", unsafe_allow_html=True)
        if st.button("🧠 Analyse", use_container_width=True, type="primary"):
            if custom_ta.strip():
                with st.spinner("✨ AI is analysing the word…"):
                    result = analyze_custom_word(custom_ta.strip(), custom_translit.strip())
                if result and result.get("senses"):
                    st.session_state.custom_word_data = result
                    st.session_state.selected_word = result
                    st.session_state.screen = "word_detail"
                    st.rerun()
                else:
                    st.error("Could not analyse word. Try again or check spelling.")
            else:
                st.warning("Please enter a Tamil word.")

    st.markdown("---")
    st.caption("PolySense Tamil · AI-Powered · Tamil Polysemy Research · © Maadhyamik Technologies")


# ══════════════════════════════════════════════════════════════════════════════
# WORD DETAIL
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.screen == "word_detail":
    w = st.session_state.selected_word

    st.markdown(f"""
    <div class="word-card">
      <div class="tamil-word">{w['word']}</div>
      <div class="transliteration">/{w['transliteration']}/</div>
    </div>""", unsafe_allow_html=True)

    st.markdown(f"**{len(w['senses'])} meanings identified by AI:**")
    for s in w["senses"]:
        pc = "pill-verb" if s["pos"] == "verb" else "pill-noun"
        st.markdown(f"""
        <div style='background:var(--surface);border-radius:10px;padding:0.8rem 1.2rem;
                    margin:0.4rem 0;border:1px solid var(--border);'>
          <span class='pill-pos {pc}'>{s['pos'].upper()}</span>&nbsp;&nbsp;
          <strong>{s['meaning_en']}</strong>
          <span style='color:var(--muted);font-size:0.9rem;margin-left:0.5rem;'>
            — <span class='tamil-text'>{s['meaning_ta']}</span>
          </span>
        </div>""", unsafe_allow_html=True)

    with st.expander("📐 View Morphological Variants (tense/case forms)", expanded=False):
        for s in w["senses"]:
            sense_key = s["meaning_en"]
            if st.button(f"Generate forms for: {s['meaning_en']} ({s['pos']})", key=f"morph_{sense_key}"):
                with st.spinner(f"Generating {s['pos']} forms…"):
                    variants = generate_morphological_variants(w, s)
                    st.session_state.morph_data[sense_key] = variants

            if sense_key in st.session_state.morph_data:
                variants = st.session_state.morph_data[sense_key]
                if variants:
                    pc = "pill-verb" if s["pos"] == "verb" else "pill-noun"
                    st.markdown(f"<span class='pill-pos {pc}'>{s['pos'].upper()}</span> **{sense_key}**", unsafe_allow_html=True)
                    st.markdown("""
                    <table class='morph-table'>
                      <thead><tr>
                        <th>Form</th><th>Label</th><th>Transliteration</th><th>Example</th>
                      </tr></thead><tbody>""" +
                    "".join(
                        f"<tr><td class='morph-form'>{v.get('form','')}</td>"
                        f"<td style='color:var(--muted);'>{v.get('label','')}</td>"
                        f"<td style='font-family:monospace;color:#7b82a6;font-size:0.82rem;'>{v.get('transliteration','')}</td>"
                        f"<td class='tamil-text' style='font-size:0.85rem;'>{v.get('example','')}</td></tr>"
                        for v in variants
                    ) +
                    "</tbody></table>", unsafe_allow_html=True)
                else:
                    st.info("Could not generate variants. Try again.")

    st.markdown("""
    <div class="sem-tip">
      <h3>💡 Before you play the quiz…</h3>
      <p>Explore the <strong>Semantic Web</strong> first to understand contexts,<br>
      or jump straight into <strong>Drag &amp; Drop</strong> / <strong>Multiple Choice</strong> mode.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        if st.button("🌐 Semantic Web", use_container_width=True, type="primary"):
            st.session_state.sem_web_data = None
            st.session_state.screen = "semantic"
            st.rerun()
    with c2:
        if st.button("🎮 Multiple Choice Quiz", use_container_width=True):
            st.session_state.update({
                "questions": [], "current_q": 0, "score": 0,
                "answers": [], "answered": False, "chosen": None,
                "shuffled_options": [], "ai_feedback": None,
                "drag_mode": False, "screen": "game"
            })
            st.rerun()
    with c3:
        if st.button("🖱️ Drag & Drop Quiz", use_container_width=True):
            st.session_state.update({
                "questions": [], "current_q": 0, "score": 0,
                "answers": [], "answered": False, "chosen": None,
                "shuffled_options": [], "ai_feedback": None,
                "drag_mode": True,
                "drag_placed": {}, "drag_submitted": False,
                "drag_questions": [], "drag_shuffled": None,
                "screen": "drag_game"
            })
            st.rerun()
    with c4:
        if st.button("← Back", use_container_width=True):
            st.session_state.screen = "home"
            st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# MULTIPLE CHOICE GAME
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.screen == "game":
    w = st.session_state.selected_word

    if not st.session_state.questions:
        with st.spinner("✨ Preparing quiz…"):
            senses = w["senses"]
            sense_pool = [senses[i % len(senses)] for i in range(NUM_QUESTIONS)]
            random.shuffle(sense_pool)
            qs = []
            for i, sense in enumerate(sense_pool):
                q = generate_question(w, sense, validate=False)
                if q:
                    q["sense"] = sense
                    qs.append(q)
                if len(qs) >= NUM_QUESTIONS:
                    break

        if not qs:
            st.error("❌ Could not generate questions. Please try again.")
            if st.button("← Back"):
                st.session_state.screen = "word_detail"
                st.rerun()
            st.stop()
        st.session_state.questions = qs
        st.rerun()

    questions = st.session_state.questions
    qi        = st.session_state.current_q

    if qi >= len(questions):
        st.session_state.screen = "result"
        st.rerun()

    q = questions[qi]

    while len(st.session_state.shuffled_options) <= qi:
        opts = [q["correct_answer"]] + q.get("distractors", [])[:3]
        random.shuffle(opts)
        st.session_state.shuffled_options.append(opts)
    options = st.session_state.shuffled_options[qi]

    st.markdown(f"<div style='color:var(--muted);font-size:0.85rem;'>Question {qi+1} of {len(questions)}</div>",
                unsafe_allow_html=True)
    st.progress(qi / len(questions))

    sc, vbadge, _ = st.columns([1, 2, 3])
    with sc:
        st.markdown(f"<span class='score-pill'>⭐ {st.session_state.score}/{qi}</span>",
                    unsafe_allow_html=True)
    with vbadge:
        val = q.get("validation", {})
        st.markdown(render_hitl_badge(val), unsafe_allow_html=True)

    st.markdown("")
    st.markdown(f"""
    <div class="word-card" style='margin-bottom:0.8rem;'>
      <div style='font-size:0.85rem;color:var(--muted);margin-bottom:0.3rem;'>
        Choose the correct form for this sentence
      </div>
      <div class='tamil-word' style='font-size:2rem;'>{w['word']}</div>
    </div>""", unsafe_allow_html=True)

    st.markdown("**Fill in the blank:**")
    st.markdown(f"""
    <div class='sentence-box'>
      <div class='tamil-sentence'>{q['sentence']}</div>
    </div>""", unsafe_allow_html=True)

    val = q.get("validation", {})
    if val.get("issues"):
        with st.expander("⚠️ HITL flagged potential issues with this question"):
            render_hitl_detail_panel(val)

    st.markdown("**Choose the correct word form:**")
    labels = ["A", "B", "C", "D"]

    if not st.session_state.answered:
        cols = st.columns(4)
        for idx, opt in enumerate(options):
            with cols[idx]:
                if st.button(labels[idx] + ". " + opt,
                             key=f"opt_{qi}_{idx}", use_container_width=True):
                    correct  = q["correct_answer"]
                    is_right = (opt.strip() == correct.strip())
                    if is_right:
                        st.session_state.score += 1
                    st.session_state.answers.append({
                        "question":    q["sentence"],
                        "translation": q.get("sentence_translation", ""),
                        "correct":     correct,
                        "chosen":      opt,
                        "is_right":    is_right,
                        "explanation": q.get("explanation", ""),
                        "sense":       q["sense"]["meaning_en"],
                        "validation":  q.get("validation", {})
                    })
                    st.session_state.answered = True
                    st.session_state.chosen   = opt
                    st.rerun()

        # ── Navigation buttons always visible ──
        st.markdown("")
        nb1, nb2 = st.columns([1, 1])
        with nb1:
            if st.button("🏠 Home", key=f"home_pre_{qi}", use_container_width=True):
                st.session_state.screen = "home"
                st.rerun()
        with nb2:
            if st.button("← Back to Word", key=f"back_pre_{qi}", use_container_width=True):
                st.session_state.screen = "word_detail"
                st.rerun()
    else:
        chosen   = st.session_state.chosen
        correct  = q["correct_answer"]
        is_right = (chosen.strip() == correct.strip())

        cols = st.columns(4)
        for idx, opt in enumerate(options):
            with cols[idx]:
                lbl = labels[idx] + ". " + opt
                if opt.strip() == correct.strip():
                    st.success("✅ " + lbl)
                elif opt == chosen and not is_right:
                    st.error("❌ " + lbl)
                else:
                    st.button(lbl, disabled=True, key=f"d_{qi}_{idx}", use_container_width=True)

        if is_right:
            st.success("🎉 Correct!")
        else:
            st.error(f"❌ Correct answer: **{correct}**")
            if q.get("sentence_translation"):
                st.caption(f"📖 Meaning: {q['sentence_translation']}")

        if q.get("explanation"):
            st.info("💡 " + q["explanation"])

        st.markdown("")
        c1, c2, c3 = st.columns([1, 1, 2])
        with c1:
            if st.button("🏠 Home", key=f"home_post_{qi}", use_container_width=True):
                st.session_state.screen = "home"
                st.rerun()
        with c2:
            if st.button("← Back", key=f"back_post_{qi}", use_container_width=True):
                st.session_state.screen = "word_detail"
                st.rerun()
        with c3:
            lbl = "Next Question →" if qi + 1 < len(questions) else "See Results 🏆"
            if st.button(lbl, use_container_width=True, type="primary", key=f"next_{qi}"):
                st.session_state.current_q += 1
                st.session_state.answered   = False
                st.session_state.chosen     = None
                st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# DRAG & DROP GAME  — Real HTML5 drag-and-drop via Streamlit component
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.screen == "drag_game":
    w = st.session_state.selected_word

    # ── Generate questions ──────────────────────────────────────────────────
    if not st.session_state.drag_questions:
        with st.spinner("✨ Preparing Drag & Drop challenges…"):
            senses = w["senses"]
            dqs    = []
            for i, sense in enumerate(senses):
                q = generate_question(w, sense, validate=False)
                if q:
                    q["sense"] = sense
                    dqs.append(q)
        if not dqs:
            st.error("❌ Could not generate questions.")
            if st.button("← Back"):
                st.session_state.screen = "word_detail"
                st.rerun()
            st.stop()
        st.session_state.drag_questions = dqs
        st.session_state.drag_placements = {}
        st.session_state.drag_selected_chip = None
        st.rerun()

    dqs = st.session_state.drag_questions

    # ── Build options pool ──────────────────────────────────────────────────
    all_options_raw = []
    for q in dqs:
        correct = q.get("correct_answer") or ""
        distractors = q.get("distractors") or []
        for opt in [correct] + distractors[:3]:
            if opt and opt.strip() and opt not in all_options_raw:
                all_options_raw.append(opt)

    if not all_options_raw:
        st.error("❌ No valid options could be generated. Please go back and try again.")
        if st.button("← Back"):
            st.session_state.screen = "word_detail"
            st.rerun()
        st.stop()

    if st.session_state.drag_shuffled is None:
        shuffled = all_options_raw.copy()
        random.shuffle(shuffled)
        st.session_state.drag_shuffled = shuffled

    all_options = st.session_state.drag_shuffled

    # ── Word card header ────────────────────────────────────────────────────
    st.markdown(f"""
    <div class="word-card" style='margin-bottom:1rem;'>
      <div style='font-size:0.85rem;color:var(--muted);margin-bottom:0.3rem;'>
        🖱️ Click a word chip to pick it up, then click a blank to place it
      </div>
      <div class='tamil-word' style='font-size:2rem;'>{w['word']}</div>
    </div>""", unsafe_allow_html=True)

    # ── Navigation buttons always visible ───────────────────────────────────
    nav1, nav2, nav3 = st.columns([1, 1, 4])
    with nav1:
        if st.button("🏠 Home", key="drag_home_top", use_container_width=True):
            st.session_state.screen = "home"
            st.rerun()
    with nav2:
        if st.button("← Back", key="drag_back_top", use_container_width=True):
            st.session_state.screen = "word_detail"
            st.rerun()

    if not st.session_state.drag_submitted:

        placements = st.session_state.drag_placements
        selected   = st.session_state.drag_selected_chip
        placed_words = set(placements.values())

        # ── STEP 1 – Word chip pool ─────────────────────────────────────────
        st.markdown("""
        <div style='font-size:0.9rem;color:#7b82a6;margin:0.8rem 0 0.3rem;'>
          🏷️ <strong style='color:#e8eaf6;'>Word Chips</strong> — click to pick up
        </div>""", unsafe_allow_html=True)

        chip_cols = st.columns(min(len(all_options), 5))
        for ci, chip in enumerate(all_options):
            is_placed   = chip in placed_words
            is_selected = selected == chip
            with chip_cols[ci % len(chip_cols)]:
                if is_placed:
                    st.markdown(
                        f"<div style='background:#0d2018;border:1.5px solid #06d6a0;"
                        f"border-radius:30px;padding:0.4rem 0.8rem;text-align:center;"
                        f"font-family:\"Noto Sans Tamil\",sans-serif;font-size:0.95rem;"
                        f"color:#06d6a0;margin:0.2rem 0;'>✓ {chip}</div>",
                        unsafe_allow_html=True)
                else:
                    btn_style = "primary" if is_selected else "secondary"
                    label = f"▶ {chip}" if is_selected else chip
                    if st.button(label, key=f"chip_{ci}_{chip}",
                                 type=btn_style, use_container_width=True):
                        if is_selected:
                            st.session_state.drag_selected_chip = None
                        else:
                            st.session_state.drag_selected_chip = chip
                        st.rerun()

        # ── STEP 2 – Sentences with blank slots ────────────────────────────
        st.markdown("""
        <div style='font-size:0.9rem;color:#7b82a6;margin:1.2rem 0 0.5rem;'>
          📝 <strong style='color:#e8eaf6;'>Sentences</strong> — click a blank to place the selected chip
        </div>""", unsafe_allow_html=True)

        for qi2, q2 in enumerate(dqs):
            sense  = q2["sense"]
            placed = placements.get(qi2)
            pc     = "pill-verb" if sense["pos"] == "verb" else "pill-noun"
            val    = q2.get("validation", {})

            with st.container():
                st.markdown(
                    f"<div style='background:var(--surface);border:1px solid var(--border);"
                    f"border-radius:14px;padding:0.9rem 1.2rem;margin-bottom:0.6rem;'>",
                    unsafe_allow_html=True)

                # Header row
                hdr1, hdr2 = st.columns([3, 1])
                with hdr1:
                    st.markdown(
                        f"<span class='pill-pos {pc}'>{sense['pos'].upper()}</span>"
                        f"&nbsp;<small style='color:var(--muted);'>{sense['meaning_en']}</small> "
                        f"{render_hitl_badge(val)}",
                        unsafe_allow_html=True)
                with hdr2:
                    pass

                # Sentence text
                parts = q2["sentence"].split("_____")
                if len(parts) < 2:
                    # Try any sequence of underscores
                    import re as _re
                    parts = _re.split(r'_{3,}', q2["sentence"])
                if len(parts) >= 2:
                    before, after = parts[0], parts[1] if len(parts) > 1 else ""
                    st.markdown(
                        f"<div class='tamil-sentence' style='font-size:1.2rem;margin:0.4rem 0;'>"
                        f"{before}"
                        f"<span style='display:inline-block;min-width:90px;border-bottom:2.5px solid #6c63ff;"
                        f"color:#6c63ff;font-size:0.9rem;padding:0 0.5rem;margin:0 0.3rem;'>"
                        f"{'&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;' if not placed else placed}"
                        f"</span>"
                        f"{after}</div>",
                        unsafe_allow_html=True)
                else:
                    st.markdown(
                        f"<div class='tamil-sentence' style='font-size:1.2rem;margin:0.4rem 0;'>"
                        f"{q2['sentence']}</div>",
                        unsafe_allow_html=True)

                if q2.get("sentence_translation"):
                    st.caption(q2["sentence_translation"])

                # Place / Clear buttons
                bc1, bc2 = st.columns([1, 3])
                with bc1:
                    if placed:
                        if st.button(f"✕ Clear", key=f"clear_{qi2}", use_container_width=True):
                            del st.session_state.drag_placements[qi2]
                            st.rerun()
                    else:
                        btn_label = f"Place → {selected}" if selected else "[ select a chip first ]"
                        btn_disabled = selected is None
                        if st.button(btn_label, key=f"blank_{qi2}",
                                     disabled=btn_disabled, use_container_width=True,
                                     type="primary" if selected else "secondary"):
                            st.session_state.drag_placements[qi2] = selected
                            st.session_state.drag_selected_chip   = None
                            st.rerun()

                st.markdown("</div>", unsafe_allow_html=True)

        # ── STEP 3 – Progress & Submit ─────────────────────────────────────
        total_q    = len(dqs)
        filled_q   = len(placements)
        all_filled = filled_q >= total_q

        st.markdown("")
        st.progress(filled_q / total_q if total_q else 0)
        st.markdown(
            f"<div style='text-align:center;color:{'#06d6a0' if all_filled else '#7b82a6'};"
            f"font-size:0.9rem;margin-bottom:0.5rem;'>"
            f"{filled_q} / {total_q} blanks filled</div>",
            unsafe_allow_html=True)

        sub1, sub2, sub3 = st.columns([1, 2, 1])
        with sub2:
            if st.button("✅ Submit Answers", use_container_width=True,
                         type="primary", disabled=not all_filled, key="drag_submit"):
                st.session_state.drag_submitted = True
                drag_score   = 0
                drag_answers = []
                for qi2, q2 in enumerate(dqs):
                    chosen  = placements.get(qi2, "")
                    correct = q2.get("correct_answer", "")
                    is_right = chosen.strip() == correct.strip()
                    if is_right:
                        drag_score += 1
                    drag_answers.append({
                        "question":    q2["sentence"],
                        "translation": q2.get("sentence_translation", ""),
                        "correct":     correct,
                        "chosen":      chosen,
                        "is_right":    is_right,
                        "explanation": q2.get("explanation", ""),
                        "sense":       q2["sense"]["meaning_en"],
                        "validation":  q2.get("validation", {})
                    })
                st.session_state.score   = drag_score
                st.session_state.answers = drag_answers
                st.rerun()

    else:
        # ── Drag & Drop Results ─────────────────────────────────────────────
        answers = st.session_state.answers
        score   = st.session_state.score
        total   = len(answers)
        pct     = int((score / total) * 100) if total else 0

        if pct == 100:  grade, emoji = "Perfect!", "🏆"
        elif pct >= 80: grade, emoji = "Excellent!", "🌟"
        elif pct >= 60: grade, emoji = "Good Job!", "👍"
        else:           grade, emoji = "Keep Practising!", "📚"

        st.markdown(f"""
        <div class='feedback-card'>
          <div style='font-size:3rem;'>{emoji}</div>
          <div style='font-size:1.4rem;font-weight:700;'>{grade}</div>
          <div class='feedback-stat'>{score}/{total}</div>
          <div class='feedback-label'>{pct}% Score · Drag &amp; Drop Mode</div>
        </div>""", unsafe_allow_html=True)

        st.markdown("### 📋 Answer Review")
        for i, a in enumerate(answers):
            icon = "✅" if a["is_right"] else "❌"
            with st.expander(f"{icon} Sentence {i+1} — {a['sense']}"):
                val = a.get("validation", {})
                st.markdown(render_hitl_badge(val), unsafe_allow_html=True)
                st.markdown(f"""
                <div class='sentence-box'>
                  <div class='tamil-sentence'>{a['question']}</div>
                  <div style='font-size:0.85rem;color:var(--muted);'>{a['translation']}</div>
                </div>""", unsafe_allow_html=True)
                ca, cb = st.columns(2)
                with ca: st.markdown(f"**Your answer:** `{a['chosen']}`")
                with cb: st.markdown(f"**Correct:** `{a['correct']}`")
                if a.get("explanation"):
                    st.info("💡 " + a["explanation"])
                if val.get("verdict") in ["warn", "reject"]:
                    with st.expander("🔍 View HITL validation details"):
                        render_hitl_detail_panel(val)

        # ── User Feedback Panel ─────────────────────────────────────────────
        st.markdown("---")
        st.markdown("### 🔔 Spot an AI Mistake? Help Us Improve!")
        with st.expander("📝 Report incorrect question / answer"):
            st.caption("Your feedback is used to correct the AI in future quiz generations.")
            fb_options = [f"Sentence {i+1}: {a['question'][:60]}…" for i, a in enumerate(answers)]
            fb_sel = st.selectbox("Which question had an issue?", ["— select —"] + fb_options, key="drag_fb_sel")
            fb_text = st.text_area(
                "Describe the mistake (e.g. 'wrong correct answer', 'grammatically incorrect sentence', 'distractor is the same as answer')",
                key="drag_fb_text", height=100)
            if st.button("✅ Submit Feedback", key="drag_fb_submit", type="primary"):
                if fb_sel != "— select —" and fb_text.strip():
                    st.session_state.user_corrections.append({
                        "question": fb_sel,
                        "feedback": fb_text.strip(),
                        "timestamp": time.time()
                    })
                    st.success("✅ Feedback saved! The AI will learn from this in future questions.")
                else:
                    st.warning("Please select a question and describe the mistake.")

        if st.session_state.user_corrections:
            st.markdown(
                f"<div style='color:var(--green);font-size:0.85rem;margin-top:0.3rem;'>"
                f"📚 {len(st.session_state.user_corrections)} correction(s) on record — "
                f"AI will avoid these patterns in new questions.</div>",
                unsafe_allow_html=True)

        st.markdown("")
        c1, c2, c3 = st.columns(3)
        with c1:
            if st.button("🔄 Try Again", use_container_width=True, type="primary"):
                st.session_state.update({
                    "drag_placed": {}, "drag_submitted": False,
                    "drag_questions": [], "drag_shuffled": None,
                    "drag_placements": {}, "drag_selected_chip": None,
                    "score": 0, "answers": [], "screen": "drag_game"
                })
                st.rerun()
        with c2:
            if st.button("🌐 Semantic Web", use_container_width=True):
                st.session_state.sem_web_data = None
                st.session_state.screen = "semantic"
                st.rerun()
        with c3:
            if st.button("🏠 Home", use_container_width=True):
                st.session_state.screen = "home"
                st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# RESULT (Multiple Choice)
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.screen == "result":
    score   = st.session_state.score
    answers = st.session_state.answers
    total   = len(answers)
    pct     = int((score / total) * 100) if total else 0
    w       = st.session_state.selected_word

    if pct == 100:  grade, msg, emoji = "Perfect!", "You have mastered all meanings!", "🏆"
    elif pct >= 80: grade, msg, emoji = "Excellent!", "Outstanding contextual understanding.", "🌟"
    elif pct >= 60: grade, msg, emoji = "Good Job!", "You understand most contexts well.", "👍"
    elif pct >= 40: grade, msg, emoji = "Keep Going!", "You are getting there — practise more.", "📚"
    else:           grade, msg, emoji = "Need Practice", "Review the Semantic Web and try again.", "💪"

    st.markdown(f"""
    <div class='feedback-card'>
      <div style='font-size:3rem;'>{emoji}</div>
      <div style='font-size:1.4rem;font-weight:700;margin:0.3rem 0;'>{grade}</div>
      <div style='color:var(--muted);margin-bottom:1rem;'>{msg}</div>
      <div class='feedback-stat'>{score}/{total}</div>
      <div class='feedback-label'>Correct Answers &nbsp;|&nbsp; {pct}% Score</div>
    </div>""", unsafe_allow_html=True)

    # ── Performance by meaning ──
    st.markdown("### 📊 Performance by Meaning")
    sense_stats = {}
    for a in answers:
        s = a["sense"]
        if s not in sense_stats:
            sense_stats[s] = {"correct": 0, "total": 0}
        sense_stats[s]["total"] += 1
        if a["is_right"]:
            sense_stats[s]["correct"] += 1

    for sense, stat in sense_stats.items():
        p = int((stat["correct"] / stat["total"]) * 100)
        bar_col = "#06d6a0" if p >= 70 else "#ffd166" if p >= 40 else "#ef233c"
        st.markdown(f"""
        <div style='margin:0.5rem 0;'>
          <div style='display:flex;justify-content:space-between;font-size:0.9rem;margin-bottom:0.3rem;'>
            <span><strong>{sense}</strong></span>
            <span style='color:{bar_col};font-weight:700;'>{stat["correct"]}/{stat["total"]} ({p}%)</span>
          </div>
          <div style='background:#1c2035;border-radius:8px;height:10px;'>
            <div style='background:{bar_col};width:{p}%;height:10px;border-radius:8px;'></div>
          </div>
        </div>""", unsafe_allow_html=True)

    # ── HITL summary ──
    flagged   = [a for a in answers if a.get("validation", {}).get("verdict") == "reject"]
    warned    = [a for a in answers if a.get("validation", {}).get("verdict") == "warn"]
    validated = [a for a in answers if a.get("validation", {}).get("verdict") == "valid"]
    st.markdown(f"""
    <div class='hitl-panel' style='margin:1rem 0;'>
      <h4>🔍 Human-in-the-Loop Validation Summary</h4>
      <p>
        <span class='hitl-rule-pass'>✅ {len(validated)} fully validated</span> &nbsp;|&nbsp;
        <span class='hitl-rule-warn'>⚠ {len(warned)} reviewed</span> &nbsp;|&nbsp;
        <span class='hitl-rule-fail'>✗ {len(flagged)} flagged</span>
        &nbsp;— out of {total} questions generated.
      </p>
      <p style='margin-top:0.4rem;font-size:0.8rem;'>
        Our 2-stage pipeline (deterministic rules + AI self-review) ensures question quality
        before showing them to learners. Flagged questions are marked so you can identify them.
      </p>
    </div>""", unsafe_allow_html=True)

    # ── AI personalised tips ──
    st.markdown("### 💡 AI Analysis & Improvement Tips")
    wrong_senses = [a["sense"] for a in answers if not a["is_right"]]

    if not st.session_state.ai_feedback:
        with st.spinner("✨ Analysing your performance…"):
            tips = generate_feedback(w["word"], score, total, wrong_senses)
            st.session_state.ai_feedback = tips

    if st.session_state.ai_feedback:
        for tip in st.session_state.ai_feedback:
            if wrong_senses:
                st.markdown(f"""
                <div class="improve-card">
                  <h4>⚠️ {tip.get('title','Tip')}</h4>
                  <p>{tip.get('tip','')}</p>
                </div>""", unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="tip-box">
                  <h4>✅ {tip.get('title','Well done')}</h4>
                  <p>{tip.get('tip','')}</p>
                </div>""", unsafe_allow_html=True)
    else:
        if pct < 60:
            st.markdown("""
            <div class="improve-card">
              <h4>⚠️ Review the Semantic Web</h4>
              <p>Study the example sentences for each meaning carefully before retrying.</p>
            </div>
            <div class="improve-card">
              <h4>⚠️ Focus on Case Suffixes</h4>
              <p>Pay attention to endings like -இல், -க்கு, -ஐ, -ஆக — they change meaning entirely.</p>
            </div>""", unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="tip-box">
              <h4>✅ Great contextual understanding!</h4>
              <p>Try words with more senses to challenge yourself further.</p>
            </div>""", unsafe_allow_html=True)

    # ── Answer breakdown ──
    st.markdown("### 📋 Detailed Answer Review")
    for i, a in enumerate(answers):
        icon = "✅" if a["is_right"] else "❌"
        with st.expander(f"{icon} Q{i+1} — {a['sense']}"):
            val_info = a.get("validation", {})
            st.markdown(render_hitl_badge(val_info), unsafe_allow_html=True)
            st.markdown(f"""
            <div class='sentence-box'>
              <div class='tamil-sentence'>{a['question']}</div>
              <div style='font-size:0.85rem;color:var(--muted);font-style:italic;'>{a['translation']}</div>
            </div>""", unsafe_allow_html=True)
            cA, cB = st.columns(2)
            with cA: st.markdown(f"**Your answer:** `{a['chosen']}`")
            with cB: st.markdown(f"**Correct:** `{a['correct']}`")
            if a.get("explanation"):
                st.info("💡 " + a["explanation"])
            if val_info.get("verdict") in ["warn", "reject"]:
                with st.expander("🔍 HITL Validation Details"):
                    render_hitl_detail_panel(val_info)

    st.markdown("")
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("🔄 Try Again", use_container_width=True, type="primary"):
            st.session_state.update({
                "questions": [], "current_q": 0, "score": 0,
                "answers": [], "answered": False,
                "shuffled_options": [], "ai_feedback": None, "screen": "game"
            })
            st.rerun()
    with c2:
        if st.button("🌐 Semantic Web", use_container_width=True):
            st.session_state.sem_web_data = None
            st.session_state.screen = "semantic"
            st.rerun()
    with c3:
        if st.button("🏠 Home", use_container_width=True):
            st.session_state.screen = "home"
            st.rerun()

    # ── User Feedback Panel ─────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("### 🔔 Spot an AI Mistake? Help Us Improve!")
    with st.expander("📝 Report incorrect question / answer"):
        st.caption("Your feedback trains the AI to avoid similar errors in future quizzes.")
        fb_options_mc = [f"Q{i+1}: {a['question'][:60]}…" for i, a in enumerate(answers)]
        fb_sel_mc = st.selectbox("Which question had an issue?",
                                  ["— select —"] + fb_options_mc, key="mc_fb_sel")
        fb_text_mc = st.text_area(
            "Describe the mistake (e.g. 'wrong correct answer', 'grammatically incorrect', 'distractor same as answer')",
            key="mc_fb_text", height=100)
        if st.button("✅ Submit Feedback", key="mc_fb_submit", type="primary"):
            if fb_sel_mc != "— select —" and fb_text_mc.strip():
                st.session_state.user_corrections.append({
                    "question": fb_sel_mc,
                    "feedback": fb_text_mc.strip(),
                    "timestamp": time.time()
                })
                st.success("✅ Feedback saved! The AI will learn from this in future questions.")
            else:
                st.warning("Please select a question and describe the mistake.")

    if st.session_state.user_corrections:
        st.markdown(
            f"<div style='color:var(--green);font-size:0.85rem;margin-top:0.3rem;'>"
            f"📚 {len(st.session_state.user_corrections)} correction(s) on record — "
            f"AI will avoid these patterns in new questions.</div>",
            unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# SEMANTIC WEB
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.screen == "semantic":
    w = st.session_state.selected_word

    st.markdown(f"""
    <div class="word-card">
      <div style='font-size:0.85rem;color:var(--muted);margin-bottom:0.3rem;'>Meaning Map for</div>
      <div class="tamil-word">{w['word']}</div>
      <div class="transliteration">/{w['transliteration']}/</div>
    </div>""", unsafe_allow_html=True)

    if not st.session_state.sem_web_data:
        with st.spinner("✨ Building meaning map…"):
            st.session_state.sem_web_data = generate_semantic_web(w)

    sem_data = st.session_state.sem_web_data
    senses   = w["senses"]

    tab1, tab2 = st.tabs(["🌐 Interactive Graph", "📋 Text Overview"])

    with tab1:
        nodes = [{"id": "root", "label": w["word"], "type": "root", "group": 0}]
        links = []
        for i, s in enumerate(senses):
            sense_id = f"sense_{i}"
            nodes.append({"id": sense_id, "label": s["meaning_en"], "type": "sense",
                          "pos": s["pos"], "group": 1})
            links.append({"source": "root", "target": sense_id})

            if sem_data and i < len(sem_data):
                sd = sem_data[i]
                ex_id = f"ex_{i}"
                example_label = sd.get("example_ta", "")[:30]
                nodes.append({"id": ex_id, "label": example_label, "type": "example", "group": 2})
                links.append({"source": sense_id, "target": ex_id})

                for ri, rw in enumerate(sd.get("related_words", [])[:2]):
                    rw_id = f"rw_{i}_{ri}"
                    nodes.append({"id": rw_id, "label": rw, "type": "related", "group": 3})
                    links.append({"source": sense_id, "target": rw_id})

        nodes_json = json.dumps(nodes)
        links_json = json.dumps(links)

        graph_html = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
  @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Tamil:wght@400;600;700&family=Sora:wght@500;700&display=swap');
  body {{ margin:0; background:#0d0f1a; overflow:hidden; }}
  svg {{ width:100%; height:520px; }}
  .node circle {{ cursor:pointer; transition:r 0.2s; }}
  .node text {{ font-family:'Noto Sans Tamil','Sora',sans-serif; pointer-events:none; fill:#e8eaf6; }}
  .link {{ stroke:#2a2f4a; stroke-opacity:0.8; }}
  .tooltip {{
    position:absolute; background:#1c2035; border:1px solid #2a2f4a;
    border-radius:10px; padding:0.6rem 1rem; font-family:'Sora',sans-serif;
    font-size:0.82rem; color:#e8eaf6; pointer-events:none;
    max-width:220px; line-height:1.5;
  }}
</style>
</head>
<body>
<div id="tooltip" class="tooltip" style="opacity:0;position:absolute;"></div>
<svg id="graph"></svg>
<script src="https://cdnjs.cloudflare.com/ajax/libs/d3/7.8.5/d3.min.js"></script>
<script>
const nodes = {nodes_json};
const links = {links_json};
const semData = {json.dumps(sem_data or [])};
const senses  = {json.dumps(senses)};

const width  = window.innerWidth;
const height = 520;
const svg    = d3.select("#graph").attr("viewBox", [0, 0, width, height]);

const colorMap  = {{ root:"#6c63ff", sense:"#ff6b9d", example:"#ffd166", related:"#06d6a0" }};
const radiusMap = {{ root:34, sense:22, example:14, related:12 }};

const sim = d3.forceSimulation(nodes)
  .force("link",      d3.forceLink(links).id(d => d.id).distance(d => d.source.type === "root" ? 130 : 90))
  .force("charge",    d3.forceManyBody().strength(-300))
  .force("center",    d3.forceCenter(width/2, height/2))
  .force("collision", d3.forceCollide().radius(d => radiusMap[d.type] + 12));

const link = svg.append("g").selectAll("line").data(links).join("line")
  .attr("class","link").attr("stroke-width",1.5);

const node = svg.append("g").selectAll("g").data(nodes).join("g")
  .attr("class","node")
  .call(d3.drag()
    .on("start", (event,d) => {{ if(!event.active) sim.alphaTarget(0.3).restart(); d.fx=d.x; d.fy=d.y; }})
    .on("drag",  (event,d) => {{ d.fx=event.x; d.fy=event.y; }})
    .on("end",   (event,d) => {{ if(!event.active) sim.alphaTarget(0); d.fx=null; d.fy=null; }})
  );

node.append("circle")
  .attr("r",      d => radiusMap[d.type])
  .attr("fill",   d => colorMap[d.type])
  .attr("stroke", d => d.type==="root" ? "#fff" : "none")
  .attr("stroke-width", 2)
  .attr("filter", d => d.type==="root" ? "url(#glow)" : "");

const defs = svg.append("defs");
const filter = defs.append("filter").attr("id","glow");
filter.append("feGaussianBlur").attr("stdDeviation","4").attr("result","coloredBlur");
const feMerge = filter.append("feMerge");
feMerge.append("feMergeNode").attr("in","coloredBlur");
feMerge.append("feMergeNode").attr("in","SourceGraphic");

node.append("text")
  .attr("text-anchor","middle").attr("dy","0.3em")
  .attr("font-size", d => d.type==="root" ? "13px" : d.type==="sense" ? "10px" : "9px")
  .attr("font-weight", d => d.type==="root" || d.type==="sense" ? "700" : "400")
  .text(d => d.label.length > 18 ? d.label.slice(0,16)+"…" : d.label);

const tooltip = d3.select("#tooltip");
node.on("mouseover", (event, d) => {{
  let html = `<strong>${{d.label}}</strong>`;
  if (d.type === "sense") {{
    const idx = parseInt(d.id.split("_")[1]);
    const s = senses[idx];
    if (s) html += `<br/><span style="color:#7b82a6;">${{s.pos.toUpperCase()}}</span><br/><span style="font-family:'Noto Sans Tamil',sans-serif;">${{s.meaning_ta}}</span>`;
    if (semData[idx]) html += `<br/><span style="color:#a8c7e8;">${{semData[idx].context_clue || ""}}</span>`;
  }} else if (d.type === "example") {{
    const idx = parseInt(d.id.split("_")[1]);
    if (semData[idx]) html += `<br/><span style="color:#ffd166;font-size:0.78rem;">${{semData[idx].example_en || ""}}</span>`;
  }}
  tooltip.html(html)
    .style("opacity","1")
    .style("left",(event.pageX+14)+"px")
    .style("top",(event.pageY-28)+"px");
}}).on("mouseout", () => tooltip.style("opacity","0"));

sim.on("tick", () => {{
  link.attr("x1",d=>d.source.x).attr("y1",d=>d.source.y)
      .attr("x2",d=>d.target.x).attr("y2",d=>d.target.y);
  node.attr("transform",d=>`translate(${{d.x}},${{d.y}})`);
}});
</script>
</body>
</html>"""

        st.components.v1.html(graph_html, height=540, scrolling=False)
        st.caption("🟣 Root word  |  🩷 Meanings  |  🟡 Example phrases  |  🟢 Related words  ·  Drag nodes to rearrange")

    with tab2:
        st.markdown(
            f"<div style='text-align:center;margin-bottom:0.8rem;'>"
            f"<span class='sem-node-root'>{w['word']} — {w['transliteration']}</span></div>",
            unsafe_allow_html=True
        )
        cols = st.columns(len(senses))
        for i, s in enumerate(senses):
            with cols[i]:
                st.markdown("<div style='text-align:center;font-size:1.3rem;color:#2a2f4a;'>│</div>",
                            unsafe_allow_html=True)
                st.markdown(
                    f"<div style='text-align:center;margin-bottom:0.5rem;'>"
                    f"<span class='sem-node-meaning'>{s['meaning_en']}</span></div>",
                    unsafe_allow_html=True)
                pc = "pill-verb" if s["pos"] == "verb" else "pill-noun"
                st.markdown(f"""
                <div class='sem-node-context'>
                  <div class='tamil-text' style='font-size:0.95rem;'>{s['meaning_ta']}</div>
                  <div style='font-size:0.7rem;color:var(--muted);margin-top:0.2rem;'>
                    <span class='pill-pos {pc}'>{s['pos'].upper()}</span>
                  </div>
                </div>""", unsafe_allow_html=True)

                if sem_data and i < len(sem_data):
                    sd = sem_data[i]
                    st.markdown("<div style='text-align:center;color:#2a2f4a;margin:0.4rem 0;'>↓</div>",
                                unsafe_allow_html=True)
                    st.markdown(f"""
                    <div style='background:var(--surface2);border:1px solid var(--border);
                                border-radius:10px;padding:0.7rem;font-size:0.82rem;'>
                      <div class='tamil-text' style='font-size:0.9rem;margin-bottom:0.3rem;'>
                        {sd.get('example_ta','')}
                      </div>
                      <div style='color:var(--muted);font-style:italic;font-size:0.78rem;'>
                        {sd.get('example_en','')}
                      </div>
                      <div style='color:#a8c7e8;font-size:0.78rem;margin-top:0.3rem;'>
                        {sd.get('context_clue','')}
                      </div>
                      {('<div style="color:var(--green);font-size:0.75rem;margin-top:0.3rem;">🔗 ' + ', '.join(sd.get('related_words',[])) + '</div>') if sd.get('related_words') else ''}
                    </div>""", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("""
    <div class="sem-tip">
      <h3>🎮 Ready to test yourself?</h3>
      <p>Explore the graph, then take the quiz in Multiple Choice or Drag &amp; Drop mode.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("")
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("🎮 Multiple Choice Quiz", use_container_width=True, type="primary"):
            st.session_state.update({
                "questions": [], "current_q": 0, "score": 0,
                "answers": [], "answered": False,
                "shuffled_options": [], "ai_feedback": None,
                "drag_mode": False, "screen": "game"
            })
            st.rerun()
    with c2:
        if st.button("🖱️ Drag & Drop Quiz", use_container_width=True):
            st.session_state.update({
                "questions": [], "current_q": 0, "score": 0,
                "answers": [], "answered": False,
                "shuffled_options": [], "ai_feedback": None,
                "drag_mode": True,
                "drag_placed": {}, "drag_submitted": False,
                "drag_questions": [], "drag_shuffled": None,
                "screen": "drag_game"
            })
            st.rerun()
    with c3:
        if st.button("← Back", use_container_width=True):
            st.session_state.screen = "word_detail"
            st.rerun()
