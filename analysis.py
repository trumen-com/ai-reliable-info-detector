"""
Analysis Orchestrator
Combines all four pillars into a single credibility report.
Handles dynamic weight adjustment when source URL is unavailable.
"""

from models.nlp_pipeline import analyse_content, analyse_bias, analyse_emotion
from models.source_credibility import analyse_source
from utils.explainer import (
    explain_content,
    explain_source,
    explain_bias,
    explain_emotion,
    generate_verdict,
)


# Fixed weights when URL IS provided
WEIGHTS_WITH_SOURCE = {
    "content": 0.40,
    "source": 0.30,
    "bias": 0.20,
    "emotion": 0.10,
}

# Adjusted weights when no URL (source pillar excluded, redistributed)
WEIGHTS_WITHOUT_SOURCE = {
    "content": 0.55,
    "source": 0.00,
    "bias": 0.28,
    "emotion": 0.17,
}


def run_analysis(text: str, url: str = "") -> dict:
    """
    Run full four-pillar analysis on an article.

    Args:
        text: Article text (required)
        url: Optional article URL for source credibility check

    Returns:
        Full analysis report dict
    """

    report = {
        "input": {
            "text_length": len(text),
            "url_provided": bool(url and url.strip()),
        },
        "pillars": {},
        "final_score": None,
        "verdict": None,
        "weight_note": None,
    }

    # ── Pillar 1: Content Analysis ────────────────────────────────────────────
    content_result = analyse_content(text)
    content_score = content_result.get("score", 50)
    content_fake_prob = content_result.get("fake_probability", 0.5)
    report["pillars"]["content"] = {
        "score": content_score,
        "fake_probability": content_fake_prob,
        "explanation": explain_content(content_score, content_fake_prob),
        "raw": content_result,
    }

    # ── Pillar 2: Source Credibility ──────────────────────────────────────────
    source_result = analyse_source(url)
    source_available = source_result.get("available", False)
    source_score = source_result.get("score") if source_available else None
    report["pillars"]["source"] = {
        "score": source_score,
        "label": source_result.get("label"),
        "domain": source_result.get("domain"),
        "found": source_result.get("found", False),
        "available": source_available,
        "explanation": explain_source(
            score=source_score,
            label=source_result.get("label", ""),
            notes=source_result.get("notes", ""),
            domain=source_result.get("domain", ""),
            found=source_result.get("found", False),
            available=source_available,
        ),
    }

    # ── Pillar 3: Bias Detection ──────────────────────────────────────────────
    bias_result = analyse_bias(text)
    bias_score = bias_result.get("score", 50)
    report["pillars"]["bias"] = {
        "score": bias_score,
        "level": bias_result.get("level", "Unknown"),
        "explanation": explain_bias(bias_score, bias_result.get("level", "Unknown")),
        "raw": bias_result,
    }

    # ── Pillar 4: Emotional Manipulation ─────────────────────────────────────
    emotion_result = analyse_emotion(text)
    emotion_score = emotion_result.get("score", 50)
    report["pillars"]["emotion"] = {
        "score": emotion_score,
        "dominant_emotions": emotion_result.get("dominant_emotions", []),
        "flagged_words": emotion_result.get("flagged_words", {}),
        "explanation": explain_emotion(
            emotion_score,
            emotion_result.get("dominant_emotions", []),
            emotion_result.get("flagged_words", {}),
        ),
        "raw": emotion_result,
    }

    # ── Final Score Calculation ───────────────────────────────────────────────
    use_source = source_available and source_score is not None
    weights = WEIGHTS_WITH_SOURCE if use_source else WEIGHTS_WITHOUT_SOURCE

    if not use_source:
        report["weight_note"] = (
            "⚠️ No URL was provided, so source credibility could not be assessed. "
            "Weights have been redistributed across the remaining three pillars. "
            "Provide a URL for a more complete analysis."
        )

    # For content and source: higher score = more credible (good)
    # For bias and emotion: higher score = more problematic (bad → invert)
    bias_credibility = 100 - bias_score
    emotion_credibility = 100 - emotion_score

    if use_source:
        final = (
            weights["content"] * content_score
            + weights["source"] * source_score
            + weights["bias"] * bias_credibility
            + weights["emotion"] * emotion_credibility
        )
    else:
        final = (
            weights["content"] * content_score
            + weights["bias"] * bias_credibility
            + weights["emotion"] * emotion_credibility
        )

    final_score = round(final)
    report["final_score"] = final_score

    # ── Verdict ───────────────────────────────────────────────────────────────
    pillar_scores_for_verdict = {
        "content": content_score,
        "source": source_score if source_score is not None else 100,
        "bias": bias_score,
        "emotion": emotion_score,
    }
    report["verdict"] = generate_verdict(final_score, pillar_scores_for_verdict)

    return report
