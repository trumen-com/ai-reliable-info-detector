"""
UI Utilities — Text highlighting and shared render components
"""

import re
import html as html_module


<<<<<<< HEAD
# Colour map per report criterion (light mode default - adapts via CSS media queries)
=======
>>>>>>> 22db2b8e7a8d8cfd6e890e613641909505f8dfd6
HIGHLIGHT_COLOURS = {
    "emotion": {"bg": "#ffe0e0", "border": "#d32f2f", "text": "#c62828", "label": "Emotion"},
    "credibility": {"bg": "#e8f5e9", "border": "#2e7d32", "text": "#1b5e20", "label": "Credibility"},
    "content": {"bg": "#e3f2fd", "border": "#1976d2", "text": "#0d47a1", "label": "Content"},
    "bias": {"bg": "#fff3e0", "border": "#f57c00", "text": "#e65100", "label": "Bias"},
}

# How many chars to show in the text preview
DISPLAY_CHARS = 2500


<<<<<<< HEAD
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
=======
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
>>>>>>> 22db2b8e7a8d8cfd6e890e613641909505f8dfd6
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

<<<<<<< HEAD
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
=======
    # Build word map — only include words present in display window
    display_lower = display_text.lower()
    word_map = {}
    for category, words in flagged_words.items():
        for word in words:
            if word.lower() in display_lower:
                word_map[word.lower()] = category
>>>>>>> 22db2b8e7a8d8cfd6e890e613641909505f8dfd6

    if not word_map:
        # Flagged words exist but are beyond the display window
        escaped = html_module.escape(display_text)
        suffix = _truncation_note(has_hidden_flags=True) if truncated else ""
        return f"<div class='article-text'>{escaped}{suffix}</div>"

    # Sort longest first to match multi-word phrases before single words
    sorted_words = sorted(word_map.keys(), key=len, reverse=True)

<<<<<<< HEAD
    # Match whole terms while still handling punctuation-adjacent words
=======
    # Use lookahead/lookbehind — more reliable than \b with unicode text
>>>>>>> 22db2b8e7a8d8cfd6e890e613641909505f8dfd6
    pattern = re.compile(
        r'(?<![a-zA-Z])(' + '|'.join(re.escape(w) for w in sorted_words) + r')(?![a-zA-Z])',
        re.IGNORECASE
    )

<<<<<<< HEAD
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
=======
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
>>>>>>> 22db2b8e7a8d8cfd6e890e613641909505f8dfd6
        )
        last = m.end()

    if last < len(display_text):
        parts.append(html_module.escape(display_text[last:]))

    suffix = _truncation_note() if truncated else ""
    return f"<div class='article-text'>{''.join(parts)}{suffix}</div>"


<<<<<<< HEAD
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
=======
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
>>>>>>> 22db2b8e7a8d8cfd6e890e613641909505f8dfd6

    return f'<div style="margin-bottom:0.6rem;">{items}</div>' if items else ""


def score_colour(score: int, invert: bool = False) -> str:
    effective = (100 - score) if invert else score
<<<<<<< HEAD
    if effective >= 70:
        return "#2e7d32"
    elif effective >= 50:
        return "#f57f17"
    elif effective >= 30:
        return "#e65100"
    else:
        return "#d32f2f"
=======
    if effective >= 70: return "#2ea043"
    if effective >= 50: return "#d29922"
    if effective >= 30: return "#e3711a"
    return "#f85149"
>>>>>>> 22db2b8e7a8d8cfd6e890e613641909505f8dfd6


def make_gauge(value: int, colour: str, height: int = 200):
    import plotly.graph_objects as go
    fig = go.Figure(go.Indicator(
        mode="gauge+number", value=value,
        gauge={
<<<<<<< HEAD
            "axis": {"range": [0, 100], "tickcolor": "#bbb", "tickfont": {"color": "#666"}, "tickwidth": 1},
            "bar": {"color": colour},
            "bgcolor": "#f5f5f5",
            "bordercolor": "#e0e0e0",
            "steps": [
                {"range": [0, 40], "color": "#ffebee"},
                {"range": [40, 60], "color": "#fff9c4"},
                {"range": [60, 80], "color": "#ffe0b2"},
                {"range": [80, 100], "color": "#e8f5e9"},
=======
            "axis": {"range": [0, 100], "tickcolor": "#444", "tickfont": {"color": "#555"}},
            "bar": {"color": colour},
            "bgcolor": "#161b22", "bordercolor": "#30363d",
            "steps": [
                {"range": [0,  40], "color": "#2a0d0d"},
                {"range": [40, 60], "color": "#1f1208"},
                {"range": [60, 80], "color": "#1f1a08"},
                {"range": [80,100], "color": "#0d2016"},
>>>>>>> 22db2b8e7a8d8cfd6e890e613641909505f8dfd6
            ],
        },
        number={"font": {"color": colour, "size": 40}},
    ))
<<<<<<< HEAD
    fig.update_layout(
        paper_bgcolor="#ffffff",
        plot_bgcolor="#ffffff",
        height=height,
        margin=dict(l=20, r=20, t=20, b=0),
        font={"color": "#333"},
    )
=======
    fig.update_layout(paper_bgcolor="#0e1117", plot_bgcolor="#0e1117",
                      height=height, margin=dict(l=20,r=20,t=20,b=0),
                      font={"color": "#e0e0e0"})
>>>>>>> 22db2b8e7a8d8cfd6e890e613641909505f8dfd6
    return fig


def make_radar(pillar_values: list, height: int = 280):
    import plotly.graph_objects as go
    labels = ["Content\nAuthenticity", "Source\nCredibility", "Bias\nNeutrality", "Emotional\nNeutrality"]
    vals = pillar_values + [pillar_values[0]]
    lbls = labels + [labels[0]]
<<<<<<< HEAD

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
=======
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
>>>>>>> 22db2b8e7a8d8cfd6e890e613641909505f8dfd6
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
