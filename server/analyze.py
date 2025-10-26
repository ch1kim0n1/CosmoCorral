# chrome_tiny_gemini_analyzer.py
from __future__ import annotations
from typing import Any, Dict, List, Optional

# ---- Simple threshold: "tiny" if < 10% of screen area
TINY_AREA_RATIO = 0.10

# ---- Optional Gemini (graceful fallback if not installed/configured)
try:
    from google import genai  # type: ignore
    from google.genai.types import GenerateContentConfig  # type: ignore
    _GENAI = True
except Exception:
    genai = None  # type: ignore
    GenerateContentConfig = object  # type: ignore
    _GENAI = False

GEMINI_MODEL = "gemini-1.5-flash"
GEMINI_TIMEOUT_S = 10.0


def _lower(x: Optional[str]) -> str:
    return (x or "").strip().lower()


def _is_chrome(win: Dict[str, Any]) -> bool:
    app = _lower(win.get("application_name"))
    proc = _lower(win.get("process_name"))
    title = _lower(win.get("window_title"))
    return ("chrome" in app) or ("chrome" in proc) or ("google chrome" in title)


def _area_ratio(bounds: Optional[Dict[str, Any]], screen: Optional[Dict[str, Any]]) -> Optional[float]:
    if not bounds or not screen:
        return None
    try:
        bw = float(bounds.get("width") or 0)
        bh = float(bounds.get("height") or 0)
        sw = float(screen.get("width") or 0)
        sh = float(screen.get("height") or 0)
        if bw <= 0 or bh <= 0 or sw <= 0 or sh <= 0:
            return None
        return (bw * bh) / (sw * sh)
    except Exception:
        return None


def _is_foreground(win: Dict[str, Any]) -> bool:
    visible = bool(win.get("is_visible", True)) and not bool(win.get("is_minimized", False))
    if not visible:
        return False
    if bool(win.get("is_focused", False)):
        return True
    try:
        return int(win.get("z_index")) == 0
    except Exception:
        return False


def _make_model_facts(hits: List[Dict[str, Any]], tiny_foreground: bool, screen_size: Dict[str, Any]) -> str:
    """Compact, factual string for Gemini to summarize."""
    lines: List[str] = []
    sw, sh = screen_size.get("width"), screen_size.get("height")
    for i, w in enumerate(hits, 1):
        ar = w.get("area_ratio")
        ar_str = "n/a" if ar is None else f"{ar:.3f}"
        lines.append(
            f"[Chrome#{i}] title={w.get('window_title')!r} focused={w.get('is_focused')} "
            f"z_index={w.get('z_index')} visible={w.get('is_visible')} minimized={w.get('is_minimized')} "
            f"bounds={w.get('bounds')} area_ratio={ar_str} tiny={w.get('is_tiny')} foreground={w.get('is_foreground')}"
        )
    header = f"screen_size={{'width': {sw}, 'height': {sh}}}; tiny_foreground={tiny_foreground}; tiny_area_ratio<{TINY_AREA_RATIO}"
    return header + "\n" + ("\n".join(lines) if lines else "No Chrome windows found.")


def _gemini_prompt(model_facts: str) -> str:
    # STRICT JSON schema with exactly the fields requested.
    return f"""
You are writing a concise report entry.

Given these facts:
```
{model_facts}
```

Return STRICT JSON ONLY in this exact schema (no extra keys, no prose, no trailing comments):
{{
  "suspicious": boolean,           // true if Chrome is a tiny foreground window (per facts)
  "reason": string,                // short machine-friendly code, e.g. "chrome_tiny_foreground" or "no_chrome_tiny"
  "message": string,               // 1-2 sentence human summary, neutral and factual
  "confidence": number             // 0..1 conservative confidence
}}
""".strip()


def _gemini_reason(model_facts: str) -> Dict[str, Any]:
    if not _GENAI:
        # Fallback: simple rule-based message
        suspicious = "tiny_foreground=True" in model_facts or "tiny_foreground=True".lower() in model_facts.lower()
        return {
            "suspicious": bool(suspicious),
            "reason": "chrome_tiny_foreground" if suspicious else "no_chrome_tiny",
            "message": (
                "Chrome appears on screen as a tiny foreground window (<10% of screen area)."
                if suspicious else
                "No tiny foreground Chrome window detected."
            ),
            "confidence": 0.6 if suspicious else 0.5,
        }

    try:
        client = genai.Client()
        model = client.models.get(name=GEMINI_MODEL)
        cfg = GenerateContentConfig(response_mime_type="application/json", temperature=0.0)
        prompt = _gemini_prompt(model_facts)
        resp = client.models.generate_content(model=model.name, contents=prompt, config=cfg)
        raw = resp.text if hasattr(resp, "text") else str(resp)
        data = __import__("json").loads(raw)

        # minimal schema guard
        for k in ("suspicious", "reason", "message", "confidence"):
            if k not in data:
                raise ValueError(f"missing key: {k}")

        # clamp confidence
        c = float(data.get("confidence") or 0.0)
        data["confidence"] = max(0.0, min(1.0, c))
        return data
    except Exception:
        # conservative fallback if API flakes
        return {
            "suspicious": False,
            "reason": "no_chrome_tiny",
            "message": "No tiny foreground Chrome window detected (model unavailable; used fallback).",
            "confidence": 0.4,
        }


async def analyze(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Simple analyzer:
    - Finds Chrome windows.
    - Decides if any is 'tiny' (<10% area) and 'foreground'.
    - Asks Gemini to produce report 'reason' and 'message' in strict JSON.
    - Also returns a single 'categories' item so existing reporters can pick a top category.
    """
    esd = (data or {}).get("enhanced_screen_data", {}) or {}
    screen_layout = esd.get("screen_layout", {}) or {}
    primary = screen_layout.get("primary_monitor", {}) or {}
    screen_size = {
        "width": (primary.get("resolution") or [None, None])[0] if isinstance(primary.get("resolution"), list) else primary.get("width"),
        "height": (primary.get("resolution") or [None, None])[1] if isinstance(primary.get("resolution"), list) else primary.get("height"),
    }
    windows: List[Dict[str, Any]] = esd.get("active_windows") or []

    hits: List[Dict[str, Any]] = []
    tiny_foreground = False

    for w in windows:
        app_name = _lower(w.get("application_name"))
        proc_name = _lower(w.get("process_name"))
        title = _lower(w.get("window_title"))
        is_chrome = ("chrome" in app_name) or ("chrome" in proc_name) or ("google chrome" in title)
        if not is_chrome:
            continue

        bounds = w.get("bounds")
        if not bounds:
            pos = w.get("position") or [0, 0]
            dim = w.get("dimensions") or [0, 0]
            bounds = {"x": pos[0], "y": pos[1], "width": (dim[0] or 0), "height": (dim[1] or 0)}

        ar = _area_ratio(bounds, screen_size)
        visible = bool(w.get("is_visible", True)) and not bool(w.get("is_minimized", False))
        focused = bool(w.get("is_focused", False))
        try:
            topmost = int(w.get("z_index")) == 0
        except Exception:
            topmost = False
        fg = visible and (focused or topmost)

        info = {
            "window_title": w.get("window_title"),
            "application_name": w.get("application_name"),
            "process_name": w.get("process_name"),
            "bounds": bounds,
            "is_visible": visible,
            "is_minimized": w.get("is_minimized", False),
            "is_focused": focused,
            "z_index": w.get("z_index"),
            "area_ratio": ar,
            "is_tiny": (ar is not None and ar < TINY_AREA_RATIO),
            "is_foreground": fg,
        }
        hits.append(info)
        if info["is_tiny"] and fg:
            tiny_foreground = True

    facts = _make_model_facts(hits, tiny_foreground, screen_size)
    model_out = _gemini_reason(facts)

    suspicious = bool(model_out.get("suspicious"))
    reason = str(model_out.get("reason") or ("chrome_tiny_foreground" if tiny_foreground else "no_chrome_tiny"))
    message = str(model_out.get("message") or ("Chrome is tiny in foreground." if tiny_foreground else "No tiny foreground Chrome."))

    # Include single category for compatibility with existing reporters
    cat_score = 0.8 if suspicious else 0.2
    categories = {"chrome_tiny_foreground": {"score": cat_score}}

    return {
        "suspicious": suspicious,
        "reason": reason,
        "message": message,
        "confidence": model_out.get("confidence", 0.5),
        "categories": categories,
        "facts": {
            "tiny_area_ratio": TINY_AREA_RATIO,
            "screen_size": screen_size,
            "matches": hits,
        },
        "model_used": GEMINI_MODEL if _GENAI else None,
    }
