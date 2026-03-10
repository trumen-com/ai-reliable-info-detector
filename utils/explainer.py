"""
Explanation Generator
Produces human-readable, educational explanations for each pillar score.
This is the key differentiator — users understand WHY, not just WHAT.
No LLM API required. Template-driven with dynamic phrase selection.
"""

import random


# Utility

def _pick(options: list) -> str:
    """Deterministically pick based on list to avoid randomness in demos."""
    return options[0]


# Content Analysis Explanation

def explain_content(score: int, fake_probability: float) -> str:
    if score >= 80:
        return (
            f"The article's language and structure closely resemble verified, factual reporting. "
            f"The model found a low probability ({round(fake_probability*100)}%) of misinformation patterns "
            f"such as sensational claims, absence of evidence markers, or conspiratorial framing. "
            f"This does not guarantee the article is accurate, but it shows no strong linguistic red flags."
        )
    elif score >= 60:
        return (
            f"The article contains some patterns that appear in both credible and unreliable content. "
            f"The AI detected a moderate misinformation signal ({round(fake_probability*100)}%), which may reflect "
            f"opinionated framing, lack of cited sources, or emotionally charged language. "
            f"Independent verification with a primary source is recommended."
        )
    elif score >= 40:
        return (
            f"The article shows several linguistic patterns commonly associated with misleading content. "
            f"The model assigned a {round(fake_probability*100)}% probability of misinformation patterns, "
            f"including possible exaggerated claims, absence of evidence, or framing techniques typical of "
            f"propaganda or clickbait. Treat this content with significant caution."
        )
    else:
        return (
            f"The article's language strongly resembles known misinformation patterns. "
            f"The model detected a high misinformation signal ({round(fake_probability*100)}%), including likely "
            f"use of sensational headlines, unfounded claims, or manipulation tactics. "
            f"We strongly recommend verifying this with established fact-checking sources before sharing."
        )


# Source Credibility Explanation

def explain_source(score, label: str, notes: str, domain: str, found: bool, available: bool) -> str:
    if not available:
        return (
            "No URL was provided, so the source could not be assessed. "
            "The credibility of the publication is an important factor — the same claim can be "
            "highly credible from a verified outlet and highly suspicious from an unknown blog. "
            "Consider providing the original article URL for a complete analysis."
        )

    if not found:
        return (
            f"The domain '{domain}' does not appear in our credibility database of known news sources. "
            f"Unknown or obscure domains account for a significant proportion of misinformation online. "
            f"This does not mean the content is false, but the absence of an editorial track record "
            f"means there is no established accountability for accuracy. A default cautionary score has been applied."
        )

    if score >= 80:
        return (
            f"'{domain}' is a well-established, high-credibility source. {notes} "
            f"High-credibility sources maintain editorial standards, issue corrections, "
            f"and have a verifiable track record of accurate reporting."
        )
    elif score >= 60:
        return (
            f"'{domain}' has a mixed credibility record. {notes} "
            f"While this outlet publishes factual content, it has a noted editorial lean or has "
            f"historically mixed accuracy in certain coverage areas. Distinguish between its "
            f"news reporting and opinion content."
        )
    elif score >= 30:
        return (
            f"'{domain}' has a low credibility rating in our database. {notes} "
            f"This source has been flagged by fact-checkers or media monitors for recurring inaccuracies, "
            f"strong ideological bias, or a pattern of misleading framing. Independent verification is strongly advised."
        )
    else:
        return (
            f"'{domain}' is rated as a very low credibility source. {notes} "
            f"This domain is associated with fabricated content, conspiracy material, or satire "
            f"presented as fact. Content from this source should not be treated as factual without "
            f"independent confirmation from established outlets."
        )


# Bias Explanation

def explain_bias(score: int, level: str) -> str:
    if score <= 25:
        return (
            f"The article's language appears largely neutral and objective. "
            f"It avoids loaded adjectives, ideological framing, and subjective value judgements. "
            f"Neutral language is associated with fact-based reporting, though it does not "
            f"by itself confirm accuracy."
        )
    elif score <= 50:
        return (
            f"The article shows a moderate level of bias (score: {score}/100). "
            f"Some subjective language or framing was detected — this may include loaded word choices, "
            f"selective emphasis, or mild ideological cues. This level of bias is common even in "
            f"mainstream media and does not necessarily indicate the content is false."
        )
    elif score <= 75:
        return (
            f"The article exhibits significant bias (score: {score}/100). "
            f"The AI detected strong directional framing, emotionally loaded adjectives, or language "
            f"that presents one perspective as objectively correct while dismissing alternatives. "
            f"Biased framing can mislead readers even when the underlying facts are technically accurate."
        )
    else:
        return (
            f"The article shows very high bias (score: {score}/100). "
            f"The language is heavily loaded with subjective framing, ideological vocabulary, and "
            f"persuasive techniques designed to influence opinion rather than inform. "
            f"Even if some facts are present, the framing significantly distorts how they are presented."
        )


# Emotional Manipulation Explanation

def explain_emotion(score: int, dominant_emotions: list, flagged_words: dict) -> str:
    # Build a description of flagged keywords
    keyword_examples = []
    for category, words in flagged_words.items():
        if words:
            keyword_examples.append(f"{category.replace('_', ' ')} language (e.g. \"{words[0]}\")")

    keyword_str = ""
    if keyword_examples:
        keyword_str = f" Specific signals include: {', '.join(keyword_examples[:3])}."

    emotion_str = ""
    if dominant_emotions:
        top = dominant_emotions[0]
        emotion_str = f" The dominant detected emotion is {top['emotion']} at {top['intensity']}% intensity."

    if score <= 20:
        return (
            f"The article uses predominantly neutral, measured language with minimal emotional appeals. "
            f"Low emotional manipulation is a positive signal — factual reporting typically informs "
            f"without relying on provoking strong feelings to persuade.{emotion_str}"
        )
    elif score <= 45:
        return (
            f"Some emotional language is present (score: {score}/100), which is normal in "
            f"editorial and opinion writing.{emotion_str}{keyword_str} "
            f"Moderate emotional tone does not indicate misinformation, but readers should be aware "
            f"of how emotional framing can shape perception of facts."
        )
    elif score <= 70:
        return (
            f"The article contains a high level of emotionally charged language (score: {score}/100).{emotion_str}"
            f"{keyword_str} "
            f"Heavy use of fear, anger, or outrage language is a common technique in misinformation "
            f"and propaganda, designed to bypass critical thinking. Be cautious about sharing "
            f"content that provokes a strong emotional reaction before fact-checking it."
        )
    else:
        return (
            f"The article is heavily loaded with emotional manipulation signals (score: {score}/100).{emotion_str}"
            f"{keyword_str} "
            f"Extreme emotional language — particularly fear, outrage, and shock — is a hallmark of "
            f"misinformation designed to go viral. Content that makes you feel a strong, immediate "
            f"emotional reaction is statistically more likely to be misleading. Pause before sharing."
        )


# Final Verdict

def generate_verdict(final_score: int, pillar_scores: dict) -> dict:
    """Generate overall verdict, risk level, and summary explanation."""

    if final_score >= 80:
        risk = "Low Risk"
        colour = "green"
        summary = (
            f"This content shows strong indicators of credibility. "
            f"The language is largely neutral, the source (if provided) has a solid reputation, "
            f"and the AI detected minimal misinformation patterns. "
            f"Always verify important claims independently, but this article presents no major red flags."
        )
    elif final_score >= 60:
        risk = "Moderate Risk"
        colour = "yellow"
        summary = (
            f"This content shows mixed signals. Some credibility indicators are positive, "
            f"but others — such as biased framing, emotional language, or an unclear source — "
            f"suggest caution. Read critically, check the source, and verify key claims before sharing."
        )
    elif final_score >= 40:
        risk = "High Risk"
        colour = "orange"
        summary = (
            f"This content displays multiple indicators commonly associated with misleading information. "
            f"Notable concerns include: {_build_concern_list(pillar_scores)}. "
            f"We strongly recommend cross-referencing with established fact-checking organisations "
            f"before treating this content as factual."
        )
    else:
        risk = "Very High Risk"
        colour = "red"
        summary = (
            f"This content shows very strong misinformation signals across multiple dimensions. "
            f"Concerns: {_build_concern_list(pillar_scores)}. "
            f"This article should be treated as highly unreliable. Do not share without thorough "
            f"independent verification from credible sources."
        )

    return {
        "risk_level": risk,
        "colour": colour,
        "summary": summary,
    }


def _build_concern_list(pillar_scores: dict) -> str:
    concerns = []
    if pillar_scores.get("content", 100) < 50:
        concerns.append("high misinformation language patterns")
    if pillar_scores.get("source", 100) < 50:
        concerns.append("low-credibility or unknown source")
    if pillar_scores.get("bias", 0) > 60:
        concerns.append("strong bias detected")
    if pillar_scores.get("emotion", 0) > 60:
        concerns.append("heavy emotional manipulation")
    return ", ".join(concerns) if concerns else "multiple low-scoring indicators"
