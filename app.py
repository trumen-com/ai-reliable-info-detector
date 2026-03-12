"""
AI Reliable Info Detector — Main Streamlit Application v3
Clean, minimal UI: URL input → analyse → four-pillar report.
"""

import streamlit as st
import sys, os
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))

from analysis import run_analysis
from utils.scraper import scrape_article
from utils.ui_utils import (
    highlight_text, render_highlight_legend,
    score_colour, make_gauge, make_radar, pillar_values_from_report, DISPLAY_CHARS,
)

st.set_page_config(
    page_title="AI Reliable Info Detector",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

if "history" not in st.session_state:
    st.session_state.history = []

<<<<<<< HEAD
# CSS - Custom component styling (Streamlit handles theme via config.toml)
css = """
=======
st.markdown("""
>>>>>>> 22db2b8e7a8d8cfd6e890e613641909505f8dfd6
<style>
    header, [data-testid="collapsedControl"] { visibility: visible; }
    .css-18e3th9 { padding-top: 1rem; }
    
    .tl-logo {
        font-size: 2.4rem; font-weight: 900;
        background: linear-gradient(135deg, #00d4ff, #7b2fff);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        letter-spacing: -0.5px;
    }
<<<<<<< HEAD
    .tl-tagline { font-size: 0.9rem; margin-top: 0.1rem; }
    .tl-sdg-badge {
        display:inline-block; border: 1px solid #4caf50;
        font-size:0.72rem; padding:2px 9px; border-radius:20px; margin:2px;
    }
=======
    .tl-tagline { color: #555; font-size: 0.88rem; margin-top: 0.15rem; }
    .sdg-badge {
        display:inline-block; background:#1a2a1a; border:1px solid #2d5a2d;
        color:#4caf50; font-size:0.72rem; padding:2px 9px;
        border-radius:20px; margin:2px;
    }

    /* Input card */
    .input-card {
        background:#161b22; border-radius:14px;
        padding:2rem 2rem 1.5rem; border:1px solid #30363d;
        max-width: 680px; margin: 0 auto;
    }

    /* Result cards */
>>>>>>> 22db2b8e7a8d8cfd6e890e613641909505f8dfd6
    .card {
        border-radius:12px; padding:1.25rem;
        border:1px solid; margin-bottom:0.75rem;
    }
    .pillar-title {
<<<<<<< HEAD
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
=======
        font-size:0.76rem; font-weight:700;
        letter-spacing:.07em; text-transform:uppercase; color:#555;
    }
    .pillar-score { font-size:1.9rem; font-weight:800; line-height:1.15; }
    .pillar-exp   { font-size:0.84rem; color:#aaa; line-height:1.7; margin-top:0.55rem; }

    /* Verdict */
    .verdict { border-radius:10px; padding:1rem 1.3rem; border-left:5px solid; margin:0.75rem 0; }
    .verdict-green  { background:#0d2016; border-color:#2ea043; }
    .verdict-yellow { background:#1f1a08; border-color:#d29922; }
    .verdict-orange { background:#1f1208; border-color:#e3711a; }
    .verdict-red    { background:#200d0d; border-color:#f85149; }

    /* Article text display */
    .article-text {
        font-size:0.87rem; line-height:1.8; color:#bbb;
        background:#0d1117; border:1px solid #30363d;
>>>>>>> 22db2b8e7a8d8cfd6e890e613641909505f8dfd6
        border-radius:8px; padding:1rem 1.1rem;
        max-height:300px; overflow-y:auto;
        white-space:pre-wrap; word-break:break-word;
        border:1px solid;
    }
<<<<<<< HEAD
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
=======

    /* History sidebar */
    .hist-item {
        background:#161b22; border:1px solid #30363d;
        border-radius:8px; padding:0.55rem 0.8rem;
        margin-bottom:0.4rem; font-size:0.81rem;
    }

    /* Inputs & buttons */
    .stTextInput input {
        background:#161b22 !important; color:#e0e0e0 !important;
        border-color:#30363d !important; border-radius:8px !important;
        font-size:0.95rem !important;
    }
    .stButton button {
        background:linear-gradient(135deg,#00d4ff22,#7b2fff22) !important;
        border:1px solid #7b2fff99 !important; color:#fff !important;
        font-weight:700 !important; border-radius:8px !important;
        font-size:1rem !important;
>>>>>>> 22db2b8e7a8d8cfd6e890e613641909505f8dfd6
    }
    .stButton button:hover {
        background:linear-gradient(135deg,#00d4ff44,#7b2fff44) !important;
    }
    .disclaimer {
<<<<<<< HEAD
        border:1px solid; border-radius:8px;
        padding:0.65rem 1rem; font-size:0.75rem;
        text-align:center; margin-top:1.5rem;
    }
=======
        background:#161b22; border:1px solid #30363d; border-radius:8px;
        padding:0.6rem 1rem; font-size:0.74rem; color:#555;
        text-align:center; margin-top:1.5rem;
    }

    section[data-testid="stSidebar"] { background:#0d1117; }
    div[data-testid="stSidebarContent"] { padding-top: 1rem; }
>>>>>>> 22db2b8e7a8d8cfd6e890e613641909505f8dfd6
</style>
"""

st.markdown(css, unsafe_allow_html=True)


# Helpers 

def risk_icon(risk: str) -> str:
    return {"Low Risk":"✅","Moderate Risk":"⚠️","High Risk":"🔶","Very High Risk":"🚨"}.get(risk, "ℹ️")

def verdict_colour_hex(colour: str) -> str:
    return {"green":"#2ea043","yellow":"#d29922","orange":"#e3711a","red":"#f85149"}.get(colour,"#888")

def save_history(label: str, report: dict):
    st.session_state.history.insert(0, {
        "label": label[:55],
        "report": report,
        "time": datetime.now().strftime("%H:%M"),
        "score": report["final_score"],
        "risk": report["verdict"]["risk_level"],
    })
    if len(st.session_state.history) > 10:
        st.session_state.history = st.session_state.history[:10]


# Sidebar — History 

with st.sidebar:
    st.markdown("""
    <div style="text-align:center;padding:.25rem 0 1.25rem;">
        <div class="tl-logo" style="font-size:1.4rem;">🔍 AI Reliable Info Detector</div>
    </div>""", unsafe_allow_html=True)

<<<<<<< HEAD
def render_verdict_banner(report: dict):
    verdict = report["verdict"]
    colour  = verdict["colour"]
    icon    = risk_icon(verdict["risk_level"])
    st.markdown(f"""
    <div class="verdict verdict-{colour}">
        <strong>{icon} {verdict['risk_level']}</strong> &nbsp;·&nbsp;
        <strong style="font-size:1.1rem;">{report['final_score']}/100</strong>
        <p style="margin:.4rem 0 0;color:#666;font-size:0.85rem;">{verdict['summary']}</p>
=======
    st.markdown("### 🕘 Session History")
    cmap = {"Low Risk":"#2ea043","Moderate Risk":"#d29922","High Risk":"#e3711a","Very High Risk":"#f85149"}

    if not st.session_state.history:
        st.markdown("<div style='color:#444;font-size:0.82rem;'>No analyses yet.</div>", unsafe_allow_html=True)
    else:
        for i, e in enumerate(st.session_state.history):
            c = cmap.get(e["risk"], "#888")
            st.markdown(f"""
            <div class="hist-item">
                <span style="color:{c};">{risk_icon(e['risk'])} {e['score']}/100</span>
                &nbsp;·&nbsp;<span style="color:#555;">{e['time']}</span><br>
                <span style="color:#bbb;">{e['label']}</span>
            </div>""", unsafe_allow_html=True)
            if st.button("View", key=f"h{i}"):
                st.session_state["view_hist"] = i
                st.rerun()

        if st.button("🗑️ Clear history"):
            st.session_state.history = []
            st.session_state.pop("view_hist", None)
            st.rerun()

    st.divider()
    st.markdown("""
    <div style="font-size:0.7rem;color:#383838;text-align:center;">
        <span class="sdg-badge">SDG 4</span>
        <span class="sdg-badge">SDG 16</span><br><br>
        Powered by HuggingFace · Streamlit
>>>>>>> 22db2b8e7a8d8cfd6e890e613641909505f8dfd6
    </div>""", unsafe_allow_html=True)


# Header 

st.markdown("""
<div style="text-align:center; padding:2rem 0 0.25rem;">
    <div class="tl-logo">🔍 AI Reliable Info Detector</div>
    <div class="tl-tagline">AI-Powered Misinformation & Bias Detection</div>
    <div style="margin-top:0.6rem;">
        <span class="sdg-badge">🟢 SDG 4 — Quality Education</span>
        <span class="sdg-badge">🟢 SDG 16 — Peace & Strong Institutions</span>
    </div>
</div>""", unsafe_allow_html=True)

st.divider()


# History viewer 

def render_report(report: dict, text: str = ""):
    verdict = report["verdict"]
    colour  = verdict["colour"]
    sc      = verdict_colour_hex(colour)
    icon    = risk_icon(verdict["risk_level"])

    st.markdown(f"""
    <div class="verdict verdict-{colour}">
        <strong>{icon} {verdict['risk_level']}</strong>
        &nbsp;·&nbsp;<strong style="font-size:1.05rem;">{report['final_score']}/100</strong>
        <p style="margin:.35rem 0 0;color:#bbb;font-size:0.85rem;">{verdict['summary']}</p>
    </div>""", unsafe_allow_html=True)

    if report.get("weight_note"):
        st.info(report["weight_note"])

    gc, rc = st.columns(2)
    with gc:
        st.plotly_chart(make_gauge(report["final_score"], sc, height=185), use_container_width=True)
    with rc:
        st.plotly_chart(make_radar(pillar_values_from_report(report), height=185), use_container_width=True)

    st.divider()

    p   = report["pillars"]
    c1, c2 = st.columns(2)

    with c1:
        cs = p["content"]["score"]
        st.markdown(f"""
        <div class="card">
<<<<<<< HEAD
            <div class="pillar-title content"><span class="pillar-num">①</span>Content Analysis</div>
            <div class="pillar-score" style="color:{cc};">{cs}<span style="font-size:.9rem;color:#555;">/100</span></div>
=======
            <div class="pillar-title">① Content Analysis</div>
            <div class="pillar-score" style="color:{score_colour(cs)};">{cs}<span style="font-size:.85rem;color:#444;">/100</span></div>
>>>>>>> 22db2b8e7a8d8cfd6e890e613641909505f8dfd6
            <div class="pillar-exp">{p['content']['explanation']}</div>
        </div>""", unsafe_allow_html=True)

        bs = p["bias"]["score"]
        st.markdown(f"""
        <div class="card">
<<<<<<< HEAD
            <div class="pillar-title bias"><span class="pillar-num">③</span>Bias Detection &nbsp;<span style="color:#555;font-size:.75rem;">({p['bias']['level']})</span></div>
            <div class="pillar-score" style="color:{bc};">{bs}<span style="font-size:.9rem;color:#555;">/100</span></div>
=======
            <div class="pillar-title">③ Bias Detection &nbsp;<span style="color:#444;font-size:.73rem;">({p['bias']['level']})</span></div>
            <div class="pillar-score" style="color:{score_colour(bs,invert=True)};">{bs}<span style="font-size:.85rem;color:#444;">/100</span></div>
>>>>>>> 22db2b8e7a8d8cfd6e890e613641909505f8dfd6
            <div class="pillar-exp">{p['bias']['explanation']}</div>
        </div>""", unsafe_allow_html=True)

    with c2:
        src = p["source"]
        ss  = src["score"] if src["score"] is not None else "N/A"
        sc2 = score_colour(ss) if isinstance(ss, int) else "#555"
        dom = f"<div style='font-size:.75rem;color:#555;margin-top:.2rem;'>{src['domain']} · {src['label']}</div>" if src["domain"] else ""
        st.markdown(f"""
        <div class="card">
<<<<<<< HEAD
            <div class="pillar-title credibility"><span class="pillar-num">②</span>Source Credibility</div>
            <div class="pillar-score" style="color:{sc};">{ss}<span style="font-size:.9rem;color:#555;">/100</span></div>
=======
            <div class="pillar-title">② Source Credibility</div>
            <div class="pillar-score" style="color:{sc2};">{ss}<span style="font-size:.85rem;color:#444;">/100</span></div>
>>>>>>> 22db2b8e7a8d8cfd6e890e613641909505f8dfd6
            {dom}
            <div class="pillar-exp">{src['explanation']}</div>
        </div>""", unsafe_allow_html=True)

        es = p["emotion"]["score"]
        emo_str = " &nbsp;".join(
            f"<span style='font-size:.75rem;color:#666;'>{e['emotion'].capitalize()}: {e['intensity']}%</span>"
            for e in p["emotion"]["dominant_emotions"][:3]
        )
        st.markdown(f"""
        <div class="card">
<<<<<<< HEAD
            <div class="pillar-title emotion"><span class="pillar-num">④</span>Emotional Manipulation</div>
            <div class="pillar-score" style="color:{ec};">{es}<span style="font-size:.9rem;color:#555;">/100</span></div>
            <div style="margin:.3rem 0;">{emotions_str}</div>
=======
            <div class="pillar-title">④ Emotional Manipulation</div>
            <div class="pillar-score" style="color:{score_colour(es,invert=True)};">{es}<span style="font-size:.85rem;color:#444;">/100</span></div>
            <div style="margin:.25rem 0 .1rem;">{emo_str}</div>
>>>>>>> 22db2b8e7a8d8cfd6e890e613641909505f8dfd6
            <div class="pillar-exp">{p['emotion']['explanation']}</div>
        </div>""", unsafe_allow_html=True)

    # Highlighted text
    if text:
<<<<<<< HEAD
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
=======
        flagged = p["emotion"]["flagged_words"]
        display_text = text[:DISPLAY_CHARS]
        st.markdown("#### 🖍️ Manipulation Word Highlights")
        legend = render_highlight_legend(flagged, display_text=display_text)
        if legend:
            st.markdown(legend, unsafe_allow_html=True)
        elif flagged:
            st.markdown("<div style='color:#555;font-size:.82rem;'>Flagged words detected but fall outside the preview window.</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div style='color:#555;font-size:.82rem;'>No manipulation keywords detected in this article.</div>", unsafe_allow_html=True)
        st.markdown(highlight_text(text, flagged), unsafe_allow_html=True)
>>>>>>> 22db2b8e7a8d8cfd6e890e613641909505f8dfd6

    st.markdown("""
    <div class="disclaimer">
        ⚠️ This tool identifies <em>indicators commonly associated with misinformation</em> — not definitive facts.
        Always verify important claims with trusted, independent sources.
    </div>""", unsafe_allow_html=True)


if "view_hist" in st.session_state:
    idx = st.session_state["view_hist"]
    if 0 <= idx < len(st.session_state.history):
        e = st.session_state.history[idx]
        st.markdown(f"### 🕘 {e['label']}")
        st.caption(f"Analysed at {e['time']}")
        render_report(e["report"])
    if st.button("← Back"):
        st.session_state.pop("view_hist", None)
        st.rerun()
    st.stop()


# Main Input 

_, mid, _ = st.columns([1, 2, 1])
with mid:
    st.markdown("""
    <div style="text-align:center;margin-bottom:1.25rem;">
        <div style="color:#aaa;font-size:0.9rem;line-height:1.8;">
            Paste a news article link below.<br>
            The AI will assess it across <strong style="color:#e0e0e0;">four independent dimensions</strong>
            — credibility, source reputation, bias, and emotional manipulation —
            and explain exactly why it scored the way it did.
        </div>
    </div>""", unsafe_allow_html=True)

    url = st.text_input(
        "",
        placeholder="https://www.bbc.com/news/article-example",
        label_visibility="collapsed",
    )
    analyse = st.button("🔍 Analyse Article", use_container_width=True)

if analyse:
    if not url.strip():
        with mid:
            st.warning("Please enter a URL.")
        st.stop()

<<<<<<< HEAD
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
=======
    with st.spinner("Fetching article..."):
        scraped = scrape_article(url.strip())
>>>>>>> 22db2b8e7a8d8cfd6e890e613641909505f8dfd6

    if not scraped["success"]:
        with mid:
            st.error(scraped["error"])
            st.markdown("""
            <div style="margin-top:.75rem;color:#666;font-size:.85rem;text-align:center;">
            Some sites block automated access or require login.<br>
            <strong style="color:#aaa;">Tip:</strong> Copy the article text and paste it into the text box below as a fallback.
            </div>""", unsafe_allow_html=True)
            # Fallback text paste
            fallback = st.text_area("Or paste article text here:", height=180,
                                    placeholder="Paste the article text if the URL fetch failed...")
            if fallback.strip():
                if st.button("🔍 Analyse Pasted Text"):
                    with st.spinner("Analysing..."):
                        report = run_analysis(fallback.strip(), url=url.strip())
                    save_history(url.strip() or "Pasted text", report)
                    st.divider()
                    st.markdown("## 📊 Analysis Report")
                    render_report(report, text=fallback.strip())
        st.stop()

    article_text = scraped["text"]
    article_title = scraped.get("title", "")
    domain = scraped.get("domain", "")

    with st.spinner("🧠 Analysing... (first run downloads AI models ~500MB)"):
        report = run_analysis(article_text, url=url.strip())

    label = article_title or domain or url[:55]
    save_history(label, report)

    st.divider()
    if article_title:
        st.markdown(f"### 📰 {article_title}")
    st.caption(f"Source: {domain}  ·  {len(article_text):,} characters extracted")

    st.markdown("## 📊 Analysis Report")
    render_report(report, text=article_text)
