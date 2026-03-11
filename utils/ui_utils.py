"""
UI Utilities — Text highlighting and shared render components
"""

import re
import html as html_module


HIGHLIGHT_COLOURS = {
    "fear":            {"bg": "#3d1a1a", "border": "#8b2020", "text": "#ff8080", "label": "Fear"},
    "outrage":         {"bg": "#3d2a1a", "border": "#8b5a20", "text": "#ffaa60", "label": "Outrage"},
    "exaggeration":    {"bg": "#1a2a3d", "border": "#205a8b", "text": "#60aaff", "label": "Exaggeration"},
    "conspiracy":      {"bg": "#2a1a3d", "border": "#5a208b", "text": "#aa80ff", "label": "Conspiracy"},
    "loaded_language": {"bg": "#1a3d2a", "border": "#208b5a", "text": "#60ffaa", "label": "Loaded Language"},
}

# How many chars to show in the text preview
DISPLAY_CHARS = 2500


def _normalise(text: str) -> str:
    """Normalise unicode whitespace and invisible chars from scraped content."""
    import unicodedata
    # Replace non-breaking spaces, zero-width chars, soft hyphens etc with regular space
    text = text.replace('\xa0', ' ').replace('\u200b', '').replace('\u00ad', '')
    # Normalise unicode to composed form
    text = unicodedata.normalize('NFC', text)
    return text


def highlight_text(text: str, flagged_words: dict) -> str:
    """
    Render article text with flagged manipulation words highlighted inline.
    
    Key fix: only include flagged words that actually appear in the display
    window — avoids showing legend items with no visible highlights.
    Runs regex on raw normalised text BEFORE html-escaping.
    """
    if not text:
        return "<em style='color:#666;'>No text available.</em>"

    # Normalise then truncate
    text = _normalise(text)
    display_text = text[:DISPLAY_CHARS]
    truncated = len(text) > DISPLAY_CHARS

    if not flagged_words:
        escaped = html_module.escape(display_text)
        suffix = _truncation_note() if truncated else ""
        return f"<div class='article-text'>{escaped}{suffix}</div>"

    # Build word map — only include words present in display window
    display_lower = display_text.lower()
    word_map = {}
    for category, words in flagged_words.items():
        for word in words:
            if word.lower() in display_lower:
                word_map[word.lower()] = category

    if not word_map:
        # Flagged words exist but are beyond the display window
        escaped = html_module.escape(display_text)
        suffix = _truncation_note(has_hidden_flags=True) if truncated else ""
        return f"<div class='article-text'>{escaped}{suffix}</div>"

    # Sort longest first to match multi-word phrases before single words
    sorted_words = sorted(word_map.keys(), key=len, reverse=True)

    # Use lookahead/lookbehind — more reliable than \b with unicode text
    pattern = re.compile(
        r'(?<![a-zA-Z])(' + '|'.join(re.escape(w) for w in sorted_words) + r')(?![a-zA-Z])',
        re.IGNORECASE
    )

    # Process raw text segment by segment, escape each part individually
    parts = []
    last = 0
    for m in pattern.finditer(display_text):
        if m.start() > last:
            parts.append(html_module.escape(display_text[last:m.start()]))
        word     = m.group(0)
        category = word_map.get(word.lower(), "loaded_language")
        c        = HIGHLIGHT_COLOURS.get(category, HIGHLIGHT_COLOURS["loaded_language"])
        parts.append(
            f'<mark style="background:{c["bg"]};border:1px solid {c["border"]};'
            f'color:{c["text"]};border-radius:3px;padding:1px 5px;font-weight:600;'
            f'cursor:help;" title="{c["label"]}">{html_module.escape(word)}</mark>'
        )
        last = m.end()

    if last < len(display_text):
        parts.append(html_module.escape(display_text[last:]))

    suffix = _truncation_note() if truncated else ""
    return f"<div class='article-text'>{''.join(parts)}{suffix}</div>"


def _truncation_note(has_hidden_flags: bool = False) -> str:
    msg = "... <em style='color:#555;font-size:.8rem;'>[article truncated for display"
    if has_hidden_flags:
        msg += " — some flagged words appear beyond this preview"
    return msg + "]</em>"


def render_highlight_legend(flagged_words: dict, display_text: str = "") -> str:
    """
    Render legend — only show categories whose words appear in the display window.
    Pass display_text to filter accurately; omit to show all.
    """
    if not flagged_words:
        return ""

    display_lower = display_text.lower() if display_text else None
    items = ""
    for category, words in flagged_words.items():
        if category not in HIGHLIGHT_COLOURS:
            continue
        # Filter to words visible in display window
        visible = [w for w in words if display_lower is None or w.lower() in display_lower] if display_lower else words
        if not visible:
            continue
        c = HIGHLIGHT_COLOURS[category]
        items += (
            f'<span style="background:{c["bg"]};border:1px solid {c["border"]};'
            f'color:{c["text"]};border-radius:4px;padding:2px 9px;'
            f'font-size:0.75rem;margin:2px;display:inline-block;">'
            f'{c["label"]} ({len(visible)})</span> '
        )

    return f'<div style="margin-bottom:0.6rem;">{items}</div>' if items else ""


def score_colour(score: int, invert: bool = False) -> str:
    effective = (100 - score) if invert else score
    if effective >= 70: return "#2ea043"
    if effective >= 50: return "#d29922"
    if effective >= 30: return "#e3711a"
    return "#f85149"


def make_gauge(value: int, colour: str, height: int = 200):
    import plotly.graph_objects as go
    fig = go.Figure(go.Indicator(
        mode="gauge+number", value=value,
        gauge={
            "axis": {"range": [0, 100], "tickcolor": "#444", "tickfont": {"color": "#555"}},
            "bar": {"color": colour},
            "bgcolor": "#161b22", "bordercolor": "#30363d",
            "steps": [
                {"range": [0,  40], "color": "#2a0d0d"},
                {"range": [40, 60], "color": "#1f1208"},
                {"range": [60, 80], "color": "#1f1a08"},
                {"range": [80,100], "color": "#0d2016"},
            ],
        },
        number={"font": {"color": colour, "size": 40}},
    ))
    fig.update_layout(paper_bgcolor="#0e1117", plot_bgcolor="#0e1117",
                      height=height, margin=dict(l=20,r=20,t=20,b=0),
                      font={"color": "#e0e0e0"})
    return fig


def make_radar(pillar_values: list, height: int = 280):
    import plotly.graph_objects as go
    labels = ["Content\nAuthenticity", "Source\nCredibility", "Bias\nNeutrality", "Emotional\nNeutrality"]
    vals = pillar_values + [pillar_values[0]]
    lbls = labels + [labels[0]]
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=vals, theta=lbls, fill="toself",
        fillcolor="rgba(0,212,255,0.1)",
        line=dict(color="#00d4ff", width=2),
    ))
    fig.update_layout(
        polar=dict(bgcolor="#161b22",
            radialaxis=dict(visible=True, range=[0,100], tickfont=dict(color="#555"), gridcolor="#30363d"),
            angularaxis=dict(tickfont=dict(color="#aaa"), gridcolor="#30363d"),
        ),
        paper_bgcolor="#0e1117", showlegend=False,
        height=height, margin=dict(l=30,r=30,t=20,b=20),
        font=dict(color="#e0e0e0"),
    )
    return fig


def pillar_values_from_report(report: dict) -> list:
    p = report["pillars"]
    return [
        p["content"]["score"],
        p["source"]["score"] if p["source"]["score"] is not None else 40,
        100 - p["bias"]["score"],
        100 - p["emotion"]["score"],
    ]
