"""
AI Reliable Info Detector — Main Streamlit Application v2
Features: Single analysis, Compare mode, Session history, Text highlighting
"""

import streamlit as st
import plotly.graph_objects as go
import sys, os
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))

from analysis import run_analysis
from utils.scraper import scrape_article
from utils.ui_utils import (
    highlight_text, render_highlight_legend,
    score_colour, make_gauge, make_radar, pillar_values_from_report,
)

# Page config
st.set_page_config(
    page_title="AI Reliable Info Detector",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Session state init
if "history" not in st.session_state:
    st.session_state.history = []
if "fetched" not in st.session_state:
    st.session_state.fetched = {}
if "mode" not in st.session_state:
    st.session_state.mode = "single"

# CSS - Custom component styling (Streamlit handles theme via config.toml)
css = """
<style>
    header, [data-testid="collapsedControl"] { visibility: visible; }
    .css-18e3th9 { padding-top: 1rem; }
    
    .tl-logo {
        font-size: 2.6rem; font-weight: 900;
        background: linear-gradient(135deg, #00d4ff, #7b2fff);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        letter-spacing: -1px;
    }
    .tl-tagline { font-size: 0.9rem; margin-top: 0.1rem; }
    .tl-sdg-badge {
        display:inline-block; border: 1px solid #4caf50;
        font-size:0.72rem; padding:2px 9px; border-radius:20px; margin:2px;
    }
    .card {
        border-radius:12px; padding:1.25rem;
        border:1px solid; margin-bottom:0.75rem;
    }
    .pillar-title {
        font-size:0.88rem; font-weight:700; letter-spacing:.06em; text-transform:uppercase;
        position: relative; display: inline-block;
    }
    .pillar-title .pillar-num {
        font-size:1.25rem; font-weight:900; margin-right:0.3rem; vertical-align: middle;
    }
    .pillar-title:after {
        content: '';
        display: block;
        width: 2.5rem;
        height: 3px;
        background: currentColor;
        margin-top: 4px;
        border-radius: 2px;
    }
    .pillar-title.content { color:#00d4ff; }
    .pillar-title.credibility { color:#2e7d32; }
    .pillar-title.bias { color:#e65100; }
    .pillar-title.emotion { color:#c62828; }
    .pillar-score { font-size:1.9rem; font-weight:800; line-height:1.1; }
    .pillar-exp { font-size:0.85rem; line-height:1.65; margin-top:0.6rem; }
    .verdict { border-radius:10px; padding:1rem 1.25rem; border-left:5px solid; margin:0.75rem 0; }
    .verdict-green { background:rgba(46, 125, 50, 0.15); border-color:#2e7d32; }
    .verdict-yellow { background:rgba(245, 127, 23, 0.15); border-color:#f57f17; }
    .verdict-orange { background:rgba(230, 81, 0, 0.15); border-color:#e65100; }
    .verdict-red { background:rgba(211, 47, 47, 0.15); border-color:#d32f2f; }
    .article-text {
        font-size:0.88rem; line-height:1.75;
        border-radius:8px; padding:1rem 1.1rem;
        max-height:280px; overflow-y:auto;
        white-space:pre-wrap; word-break:break-word;
        border:1px solid;
    }
    .hist-item {
        border:1px solid; border-radius:8px;
        padding:0.6rem 0.85rem; margin-bottom:0.4rem;
        font-size:0.82rem;
    }
    .cmp-score { font-size:3rem; font-weight:900; text-align:center; line-height:1; }
    .cmp-label { font-size:0.8rem; text-align:center; }
    .stTextArea textarea, .stTextInput input {
        border-color: currentColor !important;
    }
    .stButton button {
        background:linear-gradient(135deg,#00d4ff15,#7b2fff15) !important;
        border:1px solid #7b2fff88 !important;
        font-weight:600 !important;
    }
    .stButton button:hover {
        background:linear-gradient(135deg,#00d4ff30,#7b2fff30) !important;
    }
    .disclaimer {
        border:1px solid; border-radius:8px;
        padding:0.65rem 1rem; font-size:0.75rem;
        text-align:center; margin-top:1.5rem;
    }
</style>
"""

st.markdown(css, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# SHARED HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def save_to_history(label: str, report: dict):
    entry = {
        "label": label[:60] if label else "Untitled",
        "report": report,
        "timestamp": datetime.now().strftime("%H:%M:%S"),
        "score": report["final_score"],
        "risk": report["verdict"]["risk_level"],
    }
    st.session_state.history.insert(0, entry)
    if len(st.session_state.history) > 10:
        st.session_state.history = st.session_state.history[:10]


def risk_icon(risk: str) -> str:
    return {"Low Risk": "✅", "Moderate Risk": "⚠️", "High Risk": "🔶", "Very High Risk": "🚨"}.get(risk, "ℹ️")


def render_verdict_banner(report: dict):
    verdict = report["verdict"]
    colour  = verdict["colour"]
    icon    = risk_icon(verdict["risk_level"])
    st.markdown(f"""
    <div class="verdict verdict-{colour}">
        <strong>{icon} {verdict['risk_level']}</strong> &nbsp;·&nbsp;
        <strong style="font-size:1.1rem;">{report['final_score']}/100</strong>
        <p style="margin:.4rem 0 0;color:#666;font-size:0.85rem;">{verdict['summary']}</p>
    </div>""", unsafe_allow_html=True)


def render_pillar_cards(report: dict, text: str = ""):
    p = report["pillars"]
    col1, col2 = st.columns(2)

    with col1:
        cs = p["content"]["score"]
        cc = score_colour(cs)
        st.markdown(f"""
        <div class="card">
            <div class="pillar-title content"><span class="pillar-num">①</span>Content Analysis</div>
            <div class="pillar-score" style="color:{cc};">{cs}<span style="font-size:.9rem;color:#555;">/100</span></div>
            <div class="pillar-exp">{p['content']['explanation']}</div>
        </div>""", unsafe_allow_html=True)

        bs = p["bias"]["score"]
        bc = score_colour(bs, invert=True)
        st.markdown(f"""
        <div class="card">
            <div class="pillar-title bias"><span class="pillar-num">③</span>Bias Detection &nbsp;<span style="color:#555;font-size:.75rem;">({p['bias']['level']})</span></div>
            <div class="pillar-score" style="color:{bc};">{bs}<span style="font-size:.9rem;color:#555;">/100</span></div>
            <div class="pillar-exp">{p['bias']['explanation']}</div>
        </div>""", unsafe_allow_html=True)

    with col2:
        src = p["source"]
        ss  = src["score"] if src["score"] is not None else "N/A"
        sc  = score_colour(ss) if isinstance(ss, int) else "#666"
        dom = f"<div style='font-size:.77rem;color:#666;margin-top:.2rem;'>{src['domain']} · {src['label']}</div>" if src["domain"] else ""
        st.markdown(f"""
        <div class="card">
            <div class="pillar-title credibility"><span class="pillar-num">②</span>Source Credibility</div>
            <div class="pillar-score" style="color:{sc};">{ss}<span style="font-size:.9rem;color:#555;">/100</span></div>
            {dom}
            <div class="pillar-exp">{src['explanation']}</div>
        </div>""", unsafe_allow_html=True)

        es = p["emotion"]["score"]
        ec = score_colour(es, invert=True)
        emotions_str = " &nbsp;".join(
            f"<span style='font-size:.77rem;color:#777;'>{e['emotion'].capitalize()}: {e['intensity']}%</span>"
            for e in p["emotion"]["dominant_emotions"][:3]
        )
        st.markdown(f"""
        <div class="card">
            <div class="pillar-title emotion"><span class="pillar-num">④</span>Emotional Manipulation</div>
            <div class="pillar-score" style="color:{ec};">{es}<span style="font-size:.9rem;color:#555;">/100</span></div>
            <div style="margin:.3rem 0;">{emotions_str}</div>
            <div class="pillar-exp">{p['emotion']['explanation']}</div>
        </div>""", unsafe_allow_html=True)

    # Highlighted text
    if text:
        # Get combined flagged words from all pillars
        flagged = p.get("flagged_words_by_criterion", {})
        
        # If empty, fall back to emotion flagged_words for backward compatibility
        if not flagged:
            flagged = p.get("emotion", {}).get("flagged_words", {})
        
        st.markdown("#### 🖍️ Manipulation Word Highlights")
        
        # Check if there are any flagged words (handle both dict and list formats)
        has_flagged = False
        if isinstance(flagged, dict):
            has_flagged = any(v for v in flagged.values() if v)
        
        if has_flagged and flagged:
            st.markdown(render_highlight_legend(flagged), unsafe_allow_html=True)
            st.markdown(highlight_text(text, flagged), unsafe_allow_html=True)
        else:
            st.markdown(
                "<div style='color:#555;font-size:.85rem;'>No criterion-specific keywords detected in this text.</div>",
                unsafe_allow_html=True
            )
            st.markdown(highlight_text(text, {}), unsafe_allow_html=True)


def render_full_report(report: dict, text: str = ""):
    render_verdict_banner(report)
    if report.get("weight_note"):
        st.info(report["weight_note"])

    g_col, r_col = st.columns([1, 1])
    final  = report["final_score"]
    colour = report["verdict"]["colour"]
    sc     = {"green":"#2ea043","yellow":"#d29922","orange":"#e3711a","red":"#f85149"}.get(colour, "#888")
    with g_col:
        st.plotly_chart(make_gauge(final, sc, height=190), use_container_width=True)
    with r_col:
        st.plotly_chart(make_radar(pillar_values_from_report(report), height=190), use_container_width=True)

    st.divider()
    render_pillar_cards(report, text)


def input_block(slot: str, label: str):
    url  = st.text_input(f"URL ({label})", placeholder="https://...", key=f"url_{slot}")
    text = st.text_area(f"Article text ({label})", height=180, key=f"text_{slot}",
                        placeholder="Paste article text here, or fetch from URL above...")

    f_col, _ = st.columns([1, 2])
    with f_col:
        if st.button("🌐 Fetch from URL", key=f"fetch_{slot}"):
            if not url.strip():
                st.warning("Enter a URL first.")
            else:
                with st.spinner("Fetching..."):
                    result = scrape_article(url.strip())
                if result["success"]:
                    st.session_state.fetched[slot] = {"text": result["text"], "title": result.get("title", "")}
                    st.success(f"✅ Fetched {len(result['text'])} chars from {result['domain']}")
                    st.rerun()
                else:
                    st.error(result["error"])

    final_text = text.strip()
    if not final_text and slot in st.session_state.fetched:
        final_text = st.session_state.fetched[slot]["text"]
        title = st.session_state.fetched[slot].get("title", "")
        if title:
            st.caption(f"📰 {title}")

    return final_text, url.strip()


# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR — History
# ══════════════════════════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown("""
    <div style="text-align:center;padding:.5rem 0 1rem;">
        <div class="tl-logo" style="font-size:1.6rem;">🔍 AI Reliable Info Detector</div>
    </div>""", unsafe_allow_html=True)

    st.markdown("### 🕘 Session History")

    if not st.session_state.history:
        st.markdown("<div style='color:#555;font-size:0.82rem;'>No analyses yet this session.</div>",
                    unsafe_allow_html=True)
    else:
        colour_map = {"Low Risk":"#2ea043","Moderate Risk":"#d29922",
                      "High Risk":"#e3711a","Very High Risk":"#f85149"}
        for i, entry in enumerate(st.session_state.history):
            icon = risk_icon(entry["risk"])
            c    = colour_map.get(entry["risk"], "#888")
            st.markdown(f"""
            <div class="hist-item">
                <span style="color:{c};">{icon} {entry['score']}/100</span>
                &nbsp;·&nbsp;<span style="color:#666;">{entry['timestamp']}</span><br>
                <span style="color:#ccc;">{entry['label']}</span>
            </div>""", unsafe_allow_html=True)
            if st.button("View", key=f"hist_{i}"):
                st.session_state["viewing_history"] = i
                st.rerun()

        if st.button("🗑️ Clear history"):
            st.session_state.history = []
            st.session_state.pop("viewing_history", None)
            st.rerun()

    st.divider()
    st.markdown("""
    <div style="font-size:0.72rem;color:#444;text-align:center;">
        <span class="tl-sdg-badge">SDG 4</span>
        <span class="tl-sdg-badge">SDG 16</span><br><br>
        AI Reliable Info Detector · HuggingFace + Streamlit
    </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# HEADER + MODE SWITCHER
# ══════════════════════════════════════════════════════════════════════════════

st.markdown("""
<div style="text-align:center;padding:1.5rem 0 0.5rem;">
    <div class="tl-logo">🔍 AI Reliable Info Detector</div>
    <div class="tl-tagline">AI-Powered Misinformation & Bias Detection</div>
</div>""", unsafe_allow_html=True)

m1, m2, m3 = st.columns([2, 2, 5])
with m1:
    if st.button("📄 Single Article", use_container_width=True):
        st.session_state.mode = "single"
        st.session_state.pop("viewing_history", None)
        st.rerun()
with m2:
    if st.button("⚖️ Compare Articles", use_container_width=True):
        st.session_state.mode = "compare"
        st.session_state.pop("viewing_history", None)
        st.rerun()

st.divider()


# ══════════════════════════════════════════════════════════════════════════════
# HISTORY VIEWER
# ══════════════════════════════════════════════════════════════════════════════

if "viewing_history" in st.session_state:
    idx = st.session_state["viewing_history"]
    if 0 <= idx < len(st.session_state.history):
        entry = st.session_state.history[idx]
        st.markdown(f"### 🕘 {entry['label']}")
        st.caption(f"Analysed at {entry['timestamp']}")
        render_full_report(entry["report"])
    if st.button("← Back to analyser"):
        st.session_state.pop("viewing_history", None)
        st.rerun()
    st.stop()


# ══════════════════════════════════════════════════════════════════════════════
# SINGLE ARTICLE MODE
# ══════════════════════════════════════════════════════════════════════════════

if st.session_state.mode == "single":

    left, right = st.columns([1, 1], gap="large")

    with left:
        st.markdown("#### 📰 Article Input")
        article_text, url_input = input_block("single", "article")
        st.markdown("")
        analyse_clicked = st.button("🔍 Analyse Article", use_container_width=True)

    with right:
        st.markdown("#### ℹ️ How AI Reliable Info Detector Works")
        st.markdown("""
        <div style="color:#888;font-size:0.87rem;line-height:1.85;">
        Four independent AI pillars analyse every article:<br><br>
        <strong style="color:#00d4ff;">①</strong> <strong style="color:#00d4ff;">Content Analysis</strong> — fake news language patterns<br>
        <strong style="color:#2e7d32;">②</strong> <strong style="color:#2e7d32;">Source Credibility</strong> — domain reputation database<br>
        <strong style="color:#e65100;">③</strong> <strong style="color:#e65100;">Bias Detection</strong> — subjective framing & loaded language<br>
        <strong style="color:#c62828;">④</strong> <strong style="color:#c62828;">Emotional Manipulation</strong> — fear, outrage & shock signals<br><br>
        Each pillar explains <em>why</em> it scored that way — not just a number.<br>
        Flagged words are <mark style="background:#3d1a1a;color:#ff8080;border-radius:3px;
        padding:1px 4px;">highlighted inline</mark> in the article text.
        </div>""", unsafe_allow_html=True)

    if analyse_clicked:
        if not article_text:
            st.error("Please paste article text or fetch from a URL.")
            st.stop()
        if len(article_text.split()) < 20:
            st.warning("⚠️ Very short text — results may be inaccurate. 100+ words recommended.")

        with st.spinner("🧠 Analysing... (first run downloads AI models ~500MB)"):
            report = run_analysis(article_text, url=url_input)

        label = (
            st.session_state.fetched.get("single", {}).get("title")
            or url_input
            or article_text[:60]
        )
        save_to_history(label, report)

        st.divider()
        st.markdown("## 📊 Analysis Report")
        render_full_report(report, text=article_text)

        st.markdown("""
        <div class="disclaimer">
            ⚠️ AI Reliable Info Detector identifies <em>indicators commonly associated with misinformation</em> —
            not definitive facts. Always verify with independent sources.
        </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# COMPARE MODE
# ══════════════════════════════════════════════════════════════════════════════

elif st.session_state.mode == "compare":

    st.markdown("#### ⚖️ Compare Two Articles Side-by-Side")
    st.caption("Run both articles through AI Reliable Info Detector and see how their credibility profiles differ.")

    col_a, col_b = st.columns(2, gap="large")
    with col_a:
        st.markdown("**Article A**")
        text_a, url_a = input_block("cmp_a", "Article A")
    with col_b:
        st.markdown("**Article B**")
        text_b, url_b = input_block("cmp_b", "Article B")

    compare_clicked = st.button("⚖️ Compare Both Articles", use_container_width=True)

    if compare_clicked:
        if not text_a or not text_b:
            st.error("Both articles must have text. Please fill in Article A and Article B.")
            st.stop()

        with st.spinner("🧠 Analysing both articles..."):
            report_a = run_analysis(text_a, url=url_a)
            report_b = run_analysis(text_b, url=url_b)

        label_a = st.session_state.fetched.get("cmp_a", {}).get("title") or url_a or text_a[:50]
        label_b = st.session_state.fetched.get("cmp_b", {}).get("title") or url_b or text_b[:50]
        save_to_history(f"[A] {label_a}", report_a)
        save_to_history(f"[B] {label_b}", report_b)

        st.divider()
        st.markdown("## ⚖️ Comparison Results")

        # Score banner
        score_a  = report_a["final_score"]
        score_b  = report_b["final_score"]
        colour_a = {"green":"#2ea043","yellow":"#d29922","orange":"#e3711a","red":"#f85149"}.get(report_a["verdict"]["colour"],"#888")
        colour_b = {"green":"#2ea043","yellow":"#d29922","orange":"#e3711a","red":"#f85149"}.get(report_b["verdict"]["colour"],"#888")

        diff = abs(score_a - score_b)
        if score_a > score_b:
            winner_html = f'<span style="color:#2ea043;">Article A scores {diff} points higher</span>'
        elif score_b > score_a:
            winner_html = f'<span style="color:#2ea043;">Article B scores {diff} points higher</span>'
        else:
            winner_html = '<span style="color:#666;">Both articles scored equally</span>'

        h1, hm, h2 = st.columns([2, 1, 2])
        with h1:
            st.markdown(f"""
            <div class="card" style="text-align:center;">
                <div style="color:#555;font-size:.78rem;margin-bottom:.25rem;font-weight:700;letter-spacing:.05em;">ARTICLE A</div>
                <div class="cmp-score" style="color:{colour_a};">{score_a}</div>
                <div class="cmp-label">/100 · {report_a['verdict']['risk_level']}</div>
            </div>""", unsafe_allow_html=True)
        with hm:
            st.markdown("<div style='text-align:center;font-size:1.8rem;padding-top:1.3rem;color:#333;'>vs</div>",
                        unsafe_allow_html=True)
        with h2:
            st.markdown(f"""
            <div class="card" style="text-align:center;">
                <div style="color:#555;font-size:.78rem;margin-bottom:.25rem;font-weight:700;letter-spacing:.05em;">ARTICLE B</div>
                <div class="cmp-score" style="color:{colour_b};">{score_b}</div>
                <div class="cmp-label">/100 · {report_b['verdict']['risk_level']}</div>
            </div>""", unsafe_allow_html=True)

        st.markdown(f"<div style='text-align:center;font-size:.85rem;margin:.3rem 0 1rem;'>{winner_html}</div>",
                    unsafe_allow_html=True)

        # Radar overlay
        st.markdown("#### 📡 Credibility Profile Overlay")
        vals_a = pillar_values_from_report(report_a)
        vals_b = pillar_values_from_report(report_b)
        labels = ["Content\nAuthenticity", "Source\nCredibility", "Bias\nNeutrality", "Emotional\nNeutrality"]

        radar_fig = go.Figure()
        for vals, name, clr, rgba_fill in [
            (vals_a, "Article A", "#00d4ff", "rgba(0,212,255,0.08)"),
            (vals_b, "Article B", "#ff6b6b", "rgba(255,107,107,0.08)"),
        ]:
            radar_fig.add_trace(go.Scatterpolar(
                r=vals+[vals[0]], theta=labels+[labels[0]],
                fill="toself", fillcolor=rgba_fill,
                line=dict(color=clr, width=2), name=name,
            ))
        radar_fig.update_layout(
            polar=dict(
                bgcolor="#161b22",
                radialaxis=dict(visible=True, range=[0,100], tickfont=dict(color="#555"), gridcolor="#30363d"),
                angularaxis=dict(tickfont=dict(color="#aaa"), gridcolor="#30363d"),
            ),
            paper_bgcolor="#0e1117", showlegend=True,
            legend=dict(font=dict(color="#aaa"), bgcolor="#161b22", bordercolor="#30363d"),
            height=320, margin=dict(l=40,r=40,t=20,b=20),
            font=dict(color="#e0e0e0"),
        )
        st.plotly_chart(radar_fig, use_container_width=True)

        # Pillar comparison
        st.markdown("#### 📊 Pillar-by-Pillar Breakdown")
        pillar_defs = [
            ("① Content Analysis",      report_a["pillars"]["content"]["score"],            report_b["pillars"]["content"]["score"],            False),
            ("② Source Credibility",    report_a["pillars"]["source"]["score"] or 40,       report_b["pillars"]["source"]["score"] or 40,       False),
            ("③ Bias Detection",        report_a["pillars"]["bias"]["score"],               report_b["pillars"]["bias"]["score"],               True),
            ("④ Emotional Manipulation",report_a["pillars"]["emotion"]["score"],            report_b["pillars"]["emotion"]["score"],            True),
        ]
        for name, sa, sb, invert in pillar_defs:
            ca = score_colour(sa, invert=invert)
            cb = score_colour(sb, invert=invert)
            if invert:
                better = "A" if sa < sb else ("B" if sb < sa else "=")
            else:
                better = "A" if sa > sb else ("B" if sb > sa else "=")
            badge = {"A": "🔵 A higher", "B": "🔴 B higher", "=": "— equal"}.get(better, "")
            st.markdown(f"""
            <div class="card" style="padding:.8rem 1rem;">
                <div style="display:flex;justify-content:space-between;align-items:center;">
                    <span style="color:#888;font-size:.82rem;font-weight:700;">{name}</span>
                    <span style="color:#555;font-size:.78rem;">{badge}</span>
                </div>
                <div style="display:flex;justify-content:space-between;margin-top:.35rem;">
                    <span style="color:{ca};font-size:1.5rem;font-weight:800;">A: {sa}/100</span>
                    <span style="color:{cb};font-size:1.5rem;font-weight:800;">B: {sb}/100</span>
                </div>
            </div>""", unsafe_allow_html=True)

        # Full individual reports
        st.markdown("#### 🔬 Full Individual Reports")
        with st.expander(f"📄 Article A — Full Report ({score_a}/100)"):
            render_pillar_cards(report_a, text=text_a)
        with st.expander(f"📄 Article B — Full Report ({score_b}/100)"):
            render_pillar_cards(report_b, text=text_b)

        st.markdown("""
        <div class="disclaimer">
            ⚠️ AI Reliable Info Detector identifies <em>indicators commonly associated with misinformation</em> —
            not definitive facts. Always verify with independent sources.
        </div>""", unsafe_allow_html=True)