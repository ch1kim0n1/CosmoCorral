from __future__ import annotations

import json
import re
import time
from typing import Any, Dict, List, Optional, Tuple

try:
    from google import genai  # type: ignore
    from google.genai.types import GenerateContentConfig  # type: ignore
    _GENAI_AVAILABLE = True
except Exception:  # pragma: no cover - environment without SDK
    genai = None  # type: ignore
    GenerateContentConfig = object  # type: ignore
    _GENAI_AVAILABLE = False

# ------------------ Tunables ------------------

GEMINI_MODEL = "gemini-2.5-flash"  # swap to "gemini-1.5-pro" for deeper reasoning
GEMINI_TIMEOUT_S = 10

# Sensitivity knobs (0..1). Raise to be stricter, lower to be looser.
SENS: Dict[str, float] = {
    "education_student_base": 0.55,   # base score when edu+student is detected
    "cheating_signal": 0.15,          # per-strong-signal add
    "illegal_search_signal": 0.15,
    "ui_conflict_signal": 0.10,
    "context_consistency_bonus": 0.10,
    "llm_weight": 0.35,               # how much to weight the LLM's numeric score
    "flag_threshold": 0.75,           # final score above this => suspicious (conservative)
}

# Lightweight regexes & patterns (not keywords = truth; they’re weak signals only)
EDU_PAGE_HINTS: List[str] = [
    r"\b(proctor|exam|final|midterm|quiz|assessment|lockdown browser)\b",
    r"\b(lms|canvas|blackboard|moodle|gradescope|d2l)\b",
    r"\b(assignment|homework|syllabus|rubric|submission)\b",
]
CHEATING_BEHAVIOR_HINTS: List[str] = [
    r"\bopen book\b.*\bnot (allowed|permitted)\b",
    r"\btime remaining\b",
    r"\bflag question\b",
]
ILLEGAL_SEARCH_HINTS: List[str] = [
    r"\b(bypass|circumvent|crack|leak|dump)\b.*\b(restrictions?|answers?|solutions?)\b",
]

# ------------------ Utilities ------------------

def _safe_get(d: Dict[str, Any], path: List[str], default=None):
    cur: Any = d
    for k in path:
        if not isinstance(cur, dict) or k not in cur:
            return default
        cur = cur[k]
    return cur

def _collect_visible_text(payload: Dict[str, Any]) -> str:
    chunks: List[str] = []

    # Typed text (what the user is typing right now)
    typed = _safe_get(payload, ["enhanced_keystroke_data", "typed_text"], "")
    if typed:
        chunks.append(str(typed))

    # Screen text snapshot
    screen_snap = _safe_get(payload, ["enhanced_screen_data", "screen_text_snapshot"], "")
    if screen_snap:
        chunks.append(str(screen_snap))

    # Active window titles and visible_text
    active_windows = _safe_get(payload, ["enhanced_screen_data", "active_windows"], []) or []
    for win in active_windows:
        try:
            title = win.get("window_title") or win.get("application_name")
            vis = win.get("visible_text", "")
            if title:
                chunks.append(str(title))
            if vis:
                chunks.append(str(vis))

            # UI element texts (buttons, links, etc.)
            for el in win.get("ui_elements", []) or []:
                t = el.get("element_text") or el.get("value") or el.get("placeholder")
                if t:
                    chunks.append(str(t))
        except Exception:
            continue

    merged = "\n".join(c for c in chunks if c)
    # Collapsing whitespace
    merged = re.sub(r"[ \t]+", " ", merged)
    merged = re.sub(r"\n{3,}", "\n\n", merged).strip()
    return merged

def _collect_metrics(payload: Dict[str, Any]) -> Dict[str, Any]:
    ekd = payload.get("enhanced_keystroke_data", {}) or {}
    esd = payload.get("enhanced_screen_data", {}) or {}
    ctx = payload.get("context_metadata", {}) or {}

    metrics: Dict[str, Any] = {
        "typing_speed_wpm": ekd.get("typing_speed_wpm"),
        "error_correction_rate": ekd.get("error_correction_rate"),
        "paste_events": ekd.get("paste_events") or 0,
        "copy_events": ekd.get("copy_events") or 0,
        "app_switch_events": esd.get("app_switch_events") or 0,
        "click_count": esd.get("click_count"),
        "scroll_events": esd.get("scroll_events"),
        "interaction_speed": esd.get("interaction_speed"),
        "fatigue_indicator": ekd.get("fatigue_indicator"),
        "stress_indicator": ekd.get("stress_indicator"),
        "user_activity_state": ctx.get("user_activity_state"),
        "workflow_stage": ctx.get("workflow_stage"),
        "task_inference": ctx.get("task_inference"),
    }
    return metrics

def _match_any(patterns: List[str], text: str) -> List[str]:
    hits: List[str] = []
    for p in patterns:
        try:
            if re.search(p, text, flags=re.I | re.M):
                hits.append(p)
        except re.error:
            continue
    return hits

# ------------------ Scenario inference ------------------

def _infer_context(context: Optional[Dict[str, Any]], text: str) -> Dict[str, Any]:
    ctx = context or {}
    domain = (ctx.get("application_domain") or "").lower()
    role = (ctx.get("user_role") or "").lower()
    assignment_type = (ctx.get("assignment_type") or "").lower()

    # weak inference from on-screen hints
    edu_hints = _match_any(EDU_PAGE_HINTS + CHEATING_BEHAVIOR_HINTS, text)
    if not domain and edu_hints:
        domain = "education"
    if not role and re.search(r"\b(student|undergrad|graduate|learner)\b", text, re.I):
        role = "student"

    return {
        "application_domain": domain or "unknown",
        "user_role": role or "unknown",
        "assignment_type": assignment_type or "unspecified",
        "edu_hints": edu_hints,
    }

# ------------------ Deterministic scoring ------------------

def _deterministic_scores(inf_ctx: Dict[str, Any], metrics: Dict[str, Any], text: str) -> Dict[str, Any]:
    score_cheat = 0.0
    score_illegal = 0.0
    reasons: List[str] = []

    is_edu_student = (inf_ctx["application_domain"] == "education" and inf_ctx["user_role"] == "student")
    if is_edu_student:
        score_cheat += SENS["education_student_base"]
        reasons.append("education+student context")

    # behavioral signals (contextual, not pure keywords)
    paste = metrics.get("paste_events", 0) or 0
    copies = metrics.get("copy_events", 0) or 0
    app_sw = metrics.get("app_switch_events", 0) or 0

    # elevated paste/copy during exam-like UI
    if is_edu_student and inf_ctx["edu_hints"]:
        if paste >= 2:
            score_cheat += SENS["cheating_signal"]
            reasons.append(f"multiple paste events ({paste}) during assessment-like UI")
        if copies >= 2:
            score_cheat += SENS["cheating_signal"]
            reasons.append(f"multiple copy events ({copies}) during assessment-like UI")
        if app_sw >= 3:
            score_cheat += SENS["cheating_signal"]
            reasons.append(f"frequent app switching ({app_sw}) during assessment-like UI")

    # illegal search cues (behavioral + phrasing intent)
    illegal_hits = _match_any(ILLEGAL_SEARCH_HINTS, text)
    if illegal_hits:
        score_illegal += SENS["illegal_search_signal"]
        reasons.append("phrasing suggests restriction circumvention")

    # UI conflicts (e.g., “proctoring/lockdown” visible while external resources also visible)
    conflict = bool(
        re.search(r"\b(lockdown|proctor)\b", text, re.I) and
        re.search(r"\b(chat|messenger|discord|whatsapp|telegram|notes|gpt|ai)\b", text, re.I)
    )
    if is_edu_student and conflict:
        score_cheat += SENS["ui_conflict_signal"]
        reasons.append("proctored UI + external comm/resource visible")

    # small consistency bonus if multiple edu hints agree
    if is_edu_student and len(inf_ctx["edu_hints"]) >= 2:
        score_cheat += SENS["context_consistency_bonus"]
        reasons.append("multiple independent education UI indicators")

    return {
        "score_cheating_det": min(1.0, score_cheat),
        "score_illegal_det": min(1.0, score_illegal),
        "deterministic_reasons": reasons,
    }

# ------------------ LLM reasoning ------------------

def _llm_prompt(text: str, inf_ctx: Dict[str, Any], metrics: Dict[str, Any]) -> str:
    return f"""
You analyze on-screen + typed context for risk in EDUCATION scenarios.

Context:
- application_domain: {inf_ctx['application_domain']}
- user_role: {inf_ctx['user_role']}
- assignment_type: {inf_ctx['assignment_type']}

Observed Text (from UI, pages, typed input, labels):
```
{text}
```

Behavioral/telemetry (may be noisy or partial):
{json.dumps(metrics, ensure_ascii=False, indent=2)}

Careful reasoning goals (be conservative; avoid false positives):
1) POSSIBLE_CHEATING: Using disallowed aids during an exam/quiz/graded task (e.g., consulting external resources while “exam/proctor/lockdown” UI is present; unusual copy/paste bursts).
2) POSSIBLE_ILLEGAL_SEARCH: Intent to circumvent restrictions or obtain prohibited materials (e.g., “bypass restriction to get answers”).
3) If evidence is weak/ambiguous, keep scores low.

Return STRICT JSON ONLY:
{{
  "score_cheating_llm": number,   // 0..1 cautious confidence
  "score_illegal_llm": number,    // 0..1 cautious confidence
  "reasons": string[],            // short neutral bullet points
  "user_message": string          // brief, neutral, non-accusatory summary
}}
""".strip()

def _llm_reason(text: str, inf_ctx: Dict[str, Any], metrics: Dict[str, Any]) -> Dict[str, Any]:
    if not _GENAI_AVAILABLE:
        return {
            "score_cheating_llm": 0.0,
            "score_illegal_llm": 0.0,
            "reasons": ["LLM unavailable: google-genai SDK not installed"],
            "user_message": "No model reasoning available; used deterministic signals only.",
        }

    try:
        client = genai.Client()  # assumes environment is configured with credentials
        model = client.models.get(name=GEMINI_MODEL)
        cfg = GenerateContentConfig(response_mime_type="application/json", temperature=0.0)
        prompt = _llm_prompt(text, inf_ctx, metrics)
        t0 = time.time()
        resp = client.models.generate_content(model=model.name, contents=prompt, config=cfg)
        if (time.time() - t0) > GEMINI_TIMEOUT_S:
            raise TimeoutError("LLM timeout")
        raw = resp.text if hasattr(resp, "text") else str(resp)
        data = json.loads(raw)
        # basic schema guard
        for k in ["score_cheating_llm", "score_illegal_llm", "reasons", "user_message"]:
            if k not in data:
                raise ValueError(f"missing {k}")
        # clamp
        data["score_cheating_llm"] = max(0.0, min(1.0, float(data["score_cheating_llm"])) )
        data["score_illegal_llm"] = max(0.0, min(1.0, float(data["score_illegal_llm"])) )
        # ensure shapes
        data["reasons"] = list(data.get("reasons") or [])
        data["user_message"] = str(data.get("user_message") or "")
        return data
    except Exception as e:  # pragma: no cover - network/timing dependent
        return {
            "score_cheating_llm": 0.0,
            "score_illegal_llm": 0.0,
            "reasons": [f"LLM unavailable: {e.__class__.__name__}"],
            "user_message": "No model reasoning available; used deterministic signals only.",
        }

# ------------------ Public API ------------------

async def analyze(data: Any, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Reasoning-first suspicion detection.

    Focus: EDUCATION + STUDENT scenarios (cheating / illegal search).

    Args:
        data: Rich telemetry payload (dict-like). Expected keys (optional):
              enhanced_keystroke_data, enhanced_screen_data, context_metadata.
        context: Optional dict overriding/informing context inference with keys:
                 {application_domain, user_role, assignment_type}.

    Returns:
        Dict[str, Any]: Stable schema with scores, reasons, message, context, and signals.
    """
    # Persist raw input in a simple audit file, mirroring your existing behavior
    try:
        with open("data.json", "w", encoding="utf-8") as f:
            json.dump({"value": data}, f, ensure_ascii=False, indent=2)
        print("Saved to data.json:", type(data).__name__)
    except TypeError:
        with open("data.json", "w", encoding="utf-8") as f:
            json.dump({"value": str(data)}, f, ensure_ascii=False, indent=2)
        print("Saved to data.json (as str)")

    payload: Dict[str, Any] = data if isinstance(data, dict) else {}
    text = _collect_visible_text(payload)
    metrics = _collect_metrics(payload)
    inf_ctx = _infer_context(context, text)

    det = _deterministic_scores(inf_ctx, metrics, text)
    llm = _llm_reason(text, inf_ctx, metrics)

    # Blend scores (careful weighting)
    score_cheating = (
        (1 - SENS["llm_weight"]) * det["score_cheating_det"] +
        SENS["llm_weight"] * llm["score_cheating_llm"]
    )
    score_illegal = (
        (1 - SENS["llm_weight"]) * det["score_illegal_det"] +
        SENS["llm_weight"] * llm["score_illegal_llm"]
    )

    suspicious = (max(score_cheating, score_illegal) >= SENS["flag_threshold"])

    # Build reasons & message (dedup, concise)
    reasons = list(dict.fromkeys(det["deterministic_reasons"] + (llm.get("reasons") or [])))
    user_message = llm.get("user_message") or (
        "Observed education context; some behaviors may conflict with typical assessment rules."
        if suspicious else
        "No clear evidence of misconduct; signals appear within normal bounds."
    )

    result: Dict[str, Any] = {
        "suspicious": bool(suspicious),
        "categories": {
            "possible_cheating": {
                "score": round(float(score_cheating), 3),
                "deterministic": round(float(det["score_cheating_det"]), 3),
                "llm": round(float(llm["score_cheating_llm"]), 3),
            },
            "possible_illegal_search": {
                "score": round(float(score_illegal), 3),
                "deterministic": round(float(det["score_illegal_det"]), 3),
                "llm": round(float(llm["score_illegal_llm"]), 3),
            },
        },
        "reasons": reasons,
        "message": user_message,
        "context": inf_ctx,
        "signals": {
            "text_sample": text[:4000],  # cap to keep payload sane
            "metrics": metrics,
        },
        "meta": {
            "model_used": GEMINI_MODEL if _GENAI_AVAILABLE else None,
            "llm_weight": SENS["llm_weight"],
            "flag_threshold": SENS["flag_threshold"],
        },
    }

    return result

__all__ = ["analyze"]
