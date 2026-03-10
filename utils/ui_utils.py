"""
UI Utilities — Text highlighting and shared render components
Used by both single-article and compare views.
"""

import re
import html


# Colour map per manipulation category
HIGHLIGHT_COLOURS = {
    "fear":            {"bg": "#3d1a1a", "border": "#8b2020", "text": "#ff8080", "label": "Fear"},
    "outrage":         {"bg": "#3d2a1a", "border": "#8b5a20", "text": "#ffaa60", "label": "Outrage"},
    "exaggeration":    {"bg": "#1a2a3d", "border": "#205a8b", "text": "#60aaff", "label": "Exaggeration"},
    "conspiracy":      {"bg": "#2a1a3d", "border": "#5a208b", "text": "#aa80ff", "label": "Conspiracy"},
    "loaded_language": {"bg": "#1a3d2a", "border": "#208b5a", "text": "#60ffaa", "label": "Loaded Language"},
}


def highlight_text(text: str, flagged_words: dict, max_chars: int = 1800) -> str:
    """
    Render article text with flagged manipulation words highlighted inline.
    Returns an HTML string safe for st.markdown(..., unsafe_allow_html=True).

    IMPORTANT: regex runs on RAW text first, then each segment is HTML-escaped
    individually. Escaping before regex breaks word boundaries on special chars.
    """
    if not text:
        return "<em style='color:#666;'>No text available.</em>"

    display_text = text[:max_chars]
    if len(text) > max_chars:
        display_text += "..."

    if not flagged_words:
        return f"<div class='article-text'>{html.escape(display_text)}</div>"

    # Build word -> category map, longest phrases first
    word_map = {}
    for category, words in flagged_words.items():
        for word in words:
            word_map[word.lower()] = category

    sorted_words = sorted(word_map.keys(), key=len, reverse=True)
    if not sorted_words:
        return f"<div class='article-text'>{html.escape(display_text)}</div>"

    # Use lookahead/lookbehind instead of \b — handles punctuation-adjacent words
    pattern = re.compile(
        r'(?<![a-zA-Z])(' + '|'.join(re.escape(w) for w in sorted_words) + r')(?![a-zA-Z])',
        re.IGNORECASE
    )

    # Split raw text on matches, escape segments individually, wrap matches in <mark>
    result_parts = []
    last_end = 0

    for m in pattern.finditer(display_text):
        if m.start() > last_end:
            result_parts.append(html.escape(display_text[last_end:m.start()]))

        word     = m.group(0)
        category = word_map.get(word.lower(), "loaded_language")
        colours  = HIGHLIGHT_COLOURS.get(category, HIGHLIGHT_COLOURS["loaded_language"])
        result_parts.append(
            f'<mark style="background:{colours["bg"]};border:1px solid {colours["border"]};'
            f'color:{colours["text"]};border-radius:3px;padding:1px 5px;font-weight:600;'
            f'cursor:help;" title="{colours["label"]}">{html.escape(word)}</mark>'
        )
        last_end = m.end()

    if last_end < len(display_text):
        result_parts.append(html.escape(display_text[last_end:]))

    return f"<div class='article-text'>{''.join(result_parts)}</div>"


def render_highlight_legend(flagged_words: dict) -> str:
    """Render a colour legend for the highlighted categories present in the text."""
    if not flagged_words:
        return ""

    items = ""
    for category in flagged_words:
        if category in HIGHLIGHT_COLOURS:
            c     = HIGHLIGHT_COLOURS[category]
            count = len(flagged_words[category])
            items += (
                f'<span style="background:{c["bg"]};border:1px solid {c["border"]};'
                f'color:{c["text"]};border-radius:4px;padding:2px 8px;'
                f'font-size:0.75rem;margin:2px;display:inline-block;">'
                f'{c["label"]} ({count})</span> '
            )

    return f'<div style="margin-bottom:0.75rem;">{items}</div>' if items else ""


def score_colour(score: int, invert: bool = False) -> str:
    """Return a hex colour for a given score. Set invert=True for bias/emotion (high=bad)."""
    effective = (100 - score) if invert else score
    if effective >= 70:
        return "#2ea043"
    elif effective >= 50:
        return "#d29922"
    elif effective >= 30:
        return "#e3711a"
    else:
        return "#f85149"


def make_gauge(value: int, colour: str, height: int = 200):
    """Create a Plotly gauge figure for a credibility score."""
    import plotly.graph_objects as go
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        gauge={
            "axis": {"range": [0, 100], "tickcolor": "#444", "tickfont": {"color": "#555"}, "tickwidth": 1},
            "bar": {"color": colour},
            "bgcolor": "#161b22",
            "bordercolor": "#30363d",
            "steps": [
                {"range": [0,  40], "color": "#2a0d0d"},
                {"range": [40, 60], "color": "#1f1208"},
                {"range": [60, 80], "color": "#1f1a08"},
                {"range": [80, 100], "color": "#0d2016"},
            ],
        },
        number={"font": {"color": colour, "size": 40}},
    ))
    fig.update_layout(
        paper_bgcolor="#0e1117",
        plot_bgcolor="#0e1117",
        height=height,
        margin=dict(l=20, r=20, t=20, b=0),
        font={"color": "#e0e0e0"},
    )
    return fig


def make_radar(pillar_values: list, height: int = 280):
    """Create a Plotly radar chart for the four credibility pillars."""
    import plotly.graph_objects as go
    labels = ["Content\nAuthenticity", "Source\nCredibility", "Bias\nNeutrality", "Emotional\nNeutrality"]
    vals   = pillar_values + [pillar_values[0]]
    lbls   = labels + [labels[0]]

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=vals, theta=lbls,
        fill="toself",
        fillcolor="rgba(0,212,255,0.1)",
        line=dict(color="#00d4ff", width=2),
    ))
    fig.update_layout(
        polar=dict(
            bgcolor="#161b22",
            radialaxis=dict(visible=True, range=[0, 100], tickfont=dict(color="#555"), gridcolor="#30363d"),
            angularaxis=dict(tickfont=dict(color="#aaa"), gridcolor="#30363d"),
        ),
        paper_bgcolor="#0e1117",
        showlegend=False,
        height=height,
        margin=dict(l=30, r=30, t=20, b=20),
        font=dict(color="#e0e0e0"),
    )
    return fig


def pillar_values_from_report(report: dict) -> list:
    """Extract [content, source, bias_neutral, emotion_neutral] from a report."""
    p = report["pillars"]
    return [
        p["content"]["score"],
        p["source"]["score"] if p["source"]["score"] is not None else 40,
        100 - p["bias"]["score"],
        100 - p["emotion"]["score"],
    ]