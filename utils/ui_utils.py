"""
UI Utilities — Text highlighting and shared render components
Used by both single-article and compare views.
"""

import re
import html


# Colour map per report criterion (light mode default - adapts via CSS media queries)
HIGHLIGHT_COLOURS = {
    "emotion": {"bg": "#ffe0e0", "border": "#d32f2f", "text": "#c62828", "label": "Emotion"},
    "credibility": {"bg": "#e8f5e9", "border": "#2e7d32", "text": "#1b5e20", "label": "Credibility"},
    "content": {"bg": "#e3f2fd", "border": "#1976d2", "text": "#0d47a1", "label": "Content"},
    "bias": {"bg": "#fff3e0", "border": "#f57c00", "text": "#e65100", "label": "Bias"},
}



def highlight_text(text: str, flagged_words: dict, max_chars: int = 1800) -> str:
    """
    Render article text with flagged criterion words highlighted inline.
    Returns an HTML string safe for st.markdown(..., unsafe_allow_html=True).

    Handles multiple formats:
    - {criterion: [words]} - new format
    - {category: [words]} - emotion categories (fear, outrage, etc.)
    - Mix of both formats

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

    # Build word -> criterion map, longest phrases first
    word_map = {}
    
    for key, values in flagged_words.items():
        # Determine the criterion type
        criterion = key
        if key in ["fear", "outrage", "exaggeration", "conspiracy", "loaded_language"]:
            criterion = "emotion"
        elif key in ["bias"]:
            criterion = "bias"
        elif key in ["content"]:
            criterion = "content"
        
        # Extract words from either dict (nested categories) or list
        words_list = []
        if isinstance(values, dict):
            # Handle nested dict (emotion categories)
            for category_words in values.values():
                if isinstance(category_words, list):
                    words_list.extend(category_words)
        elif isinstance(values, list):
            words_list = values
        
        # Add to word map
        for word in words_list:
            if word and isinstance(word, str):
                word_map[word.lower()] = criterion

    sorted_words = sorted(word_map.keys(), key=len, reverse=True)
    if not sorted_words:
        return f"<div class='article-text'>{html.escape(display_text)}</div>"

    # Match whole terms while still handling punctuation-adjacent words
    pattern = re.compile(
        r'(?<![a-zA-Z])(' + '|'.join(re.escape(w) for w in sorted_words) + r')(?![a-zA-Z])',
        re.IGNORECASE
    )

    result_parts = []
    last_end = 0

    for m in pattern.finditer(display_text):
        if m.start() > last_end:
            result_parts.append(html.escape(display_text[last_end:m.start()]))

        word = m.group(0)
        criterion = word_map.get(word.lower(), "content")
        colours = HIGHLIGHT_COLOURS.get(criterion, HIGHLIGHT_COLOURS["content"])

        result_parts.append(
            f'<mark style="background:{colours["bg"]};'
            f'border:1px solid {colours["border"]};'
            f'color:{colours["text"]};'
            f'border-radius:3px;'
            f'padding:1px 5px;'
            f'font-weight:600;'
            f'cursor:help;" '
            f'title="{colours["label"]}">{html.escape(word)}</mark>'
        )
        last_end = m.end()

    if last_end < len(display_text):
        result_parts.append(html.escape(display_text[last_end:]))

    return f"<div class='article-text'>{''.join(result_parts)}</div>"


def render_highlight_legend(flagged_words: dict) -> str:
    """Render a colour legend for the highlighted criteria present in the text."""
    if not flagged_words:
        return ""

    # Count words by criterion
    criterion_counts = {}
    
    for key, values in flagged_words.items():
        # Determine the criterion type
        criterion = key
        if key in ["fear", "outrage", "exaggeration", "conspiracy", "loaded_language"]:
            criterion = "emotion"
        elif key in ["bias"]:
            criterion = "bias"
        elif key in ["content"]:
            criterion = "content"
        
        # Count words from either dict or list
        count = 0
        if isinstance(values, dict):
            # Handle nested dict (emotion categories)
            for category_values in values.values():
                if isinstance(category_values, list):
                    count += len(category_values)
        elif isinstance(values, list):
            count = len(values)
        
        if count > 0:
            criterion_counts[criterion] = criterion_counts.get(criterion, 0) + count

    # Build legend HTML
    items = ""
    for criterion in ["emotion", "bias", "content", "credibility"]:
        if criterion in criterion_counts and criterion_counts[criterion] > 0:
            if criterion in HIGHLIGHT_COLOURS:
                c = HIGHLIGHT_COLOURS[criterion]
                count = criterion_counts[criterion]
                items += (
                    f'<span style="background:{c["bg"]};'
                    f'border:1px solid {c["border"]};'
                    f'color:{c["text"]};'
                    f'border-radius:4px;'
                    f'padding:2px 8px;'
                    f'font-size:0.75rem;'
                    f'margin:2px;'
                    f'display:inline-block;">'
                    f'{c["label"]} ({count})</span> '
                )

    return f'<div style="margin-bottom:0.75rem;">{items}</div>' if items else ""


def score_colour(score: int, invert: bool = False) -> str:
    """Return a hex colour for a given score. Set invert=True for bias/emotion (high=bad)."""
    effective = (100 - score) if invert else score
    if effective >= 70:
        return "#2e7d32"
    elif effective >= 50:
        return "#f57f17"
    elif effective >= 30:
        return "#e65100"
    else:
        return "#d32f2f"


def make_gauge(value: int, colour: str, height: int = 200):
    """Create a Plotly gauge figure for a credibility score."""
    import plotly.graph_objects as go
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        gauge={
            "axis": {"range": [0, 100], "tickcolor": "#bbb", "tickfont": {"color": "#666"}, "tickwidth": 1},
            "bar": {"color": colour},
            "bgcolor": "#f5f5f5",
            "bordercolor": "#e0e0e0",
            "steps": [
                {"range": [0, 40], "color": "#ffebee"},
                {"range": [40, 60], "color": "#fff9c4"},
                {"range": [60, 80], "color": "#ffe0b2"},
                {"range": [80, 100], "color": "#e8f5e9"},
            ],
        },
        number={"font": {"color": colour, "size": 40}},
    ))
    fig.update_layout(
        paper_bgcolor="#ffffff",
        plot_bgcolor="#ffffff",
        height=height,
        margin=dict(l=20, r=20, t=20, b=0),
        font={"color": "#333"},
    )
    return fig


def make_radar(pillar_values: list, height: int = 280):
    """Create a Plotly radar chart for the four credibility pillars."""
    import plotly.graph_objects as go
    labels = ["Content\nAuthenticity", "Source\nCredibility", "Bias\nNeutrality", "Emotional\nNeutrality"]
    vals = pillar_values + [pillar_values[0]]
    lbls = labels + [labels[0]]

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=vals, theta=lbls,
        fill="toself",
        fillcolor="rgba(25,118,210,0.2)",
        line=dict(color="#1976d2", width=2),
    ))
    fig.update_layout(
        polar=dict(
            bgcolor="#ffffff",
            radialaxis=dict(visible=True, range=[0, 100], tickfont=dict(color="#999"), gridcolor="#e0e0e0"),
            angularaxis=dict(tickfont=dict(color="#666"), gridcolor="#e0e0e0"),
        ),
        paper_bgcolor="#ffffff",
        showlegend=False,
        height=height,
        margin=dict(l=30, r=30, t=20, b=20),
        font=dict(color="#333"),
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