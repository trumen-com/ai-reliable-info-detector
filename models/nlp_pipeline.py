"""
NLP Analysis Pipeline
Handles three of the four pillars using HuggingFace models:
- Content authenticity (fake news detection)
- Bias detection
- Emotional manipulation detection
All models are free, cached locally after first download.
"""

from transformers import pipeline
import re
import numpy as np

# Model registry
# These are loaded lazily to avoid slow startup.
_content_classifier = None
_emotion_classifier = None
_bias_classifier = None


def _get_content_classifier():
    global _content_classifier
    if _content_classifier is None:
        # Fine-tuned RoBERTa for fake vs real news detection
        _content_classifier = pipeline(
            "text-classification",
            model="hamzab/roberta-fake-news-classification",
            truncation=True,
            max_length=512,
        )
    return _content_classifier


def _get_emotion_classifier():
    global _emotion_classifier
    if _emotion_classifier is None:
        # Multi-label emotion classifier (anger, fear, joy, sadness, surprise, disgust, neutral)
        _emotion_classifier = pipeline(
            "text-classification",
            model="j-hartmann/emotion-english-distilroberta-base",
            truncation=True,
            max_length=512,
            top_k=None,
        )
    return _emotion_classifier


def _get_bias_classifier():
    global _bias_classifier
    if _bias_classifier is None:
        # Bias / subjectivity detection
        _bias_classifier = pipeline(
            "text-classification",
            model="valurank/distilroberta-bias",
            truncation=True,
            max_length=512,
        )
    return _bias_classifier


# Keywords for each criterion to enable color-coded highlighting
# emotion (red) - manipulation keywords
EMOTION_KEYWORDS = {
    "fear": [
        "terrifying", "horrifying", "catastrophic", "devastating", "deadly",
        "dangerous", "alarming", "frightening", "nightmare", "crisis",
        "threatens", "warned", "panic", "collapse", "emergency",
    ],
    "outrage": [
        "outrageous", "disgusting", "shameful", "unacceptable", "betrayal",
        "scandal", "corrupt", "exposed", "demand", "furious",
        "shocking", "appalling", "disturbing", "infuriating",
    ],
    "exaggeration": [
        "everyone knows", "always", "never", "all", "every single",
        "absolutely", "completely", "totally", "undeniably", "obviously",
        "proven", "confirms", "100%", "guaranteed", "certain",
    ],
    "conspiracy": [
        "secret", "hidden", "cover-up", "they don't want you to know",
        "deep state", "mainstream media won't", "silenced", "suppressed",
        "wake up", "sheeple", "agenda", "plandemic", "false flag",
        "controlled", "globalist", "elite", "cabal",
    ],
    "loaded_language": [
        "radical", "extreme", "regime", "thug", "terrorist", "invader",
        "traitor", "puppet", "destroy", "obliterate", "savage",
        "fake", "rigged", "stolen", "illegitimate",
    ],
}

# bias (orange) - words suggesting biased or subjective framing
BIAS_KEYWORDS = [
    "biased", "subjective", "opinionated", "one-sided", "slanted",
    "prejudicial", "partisan", "skewed", "distorted", "twisted",
    "misleading", "distortion", "propaganda", "spin", "narrative",
    "dogma", "ideologue", "extremist", "fanatic", "zealot",
    "presumably", "allegedly", "supposedly", "rumor", "claim", "claims",
    "attack", "assault", "war", "military", "conflict",
    "soft-pitched", "pitched", "reassuring", "opposing",
    "risks", "threat", "threats", "danger",
]

# content (green) - words suggesting credible, well-sourced content
CREDIBLE_CONTENT_KEYWORDS = [
    "study", "research", "findings", "analysis", "data",
    "scientific", "evidence", "proven", "confirmed", "verified",
    "reported", "according to", "sources", "experts", "researchers",
    "investigation", "report", "documented", "records",
    "survey", "poll", "statistics", "peer-reviewed", "academic",
    "official", "credible", "reliable", "established",
]

# content (green) - words suggesting lack of credible sourcing
UNCREDIBLE_CONTENT_KEYWORDS = [
    "unverified", "unproven", "unsourced", "unconfirmed", "alleged",
    "unnamed", "anonymous", "insider", "whistleblower", "sources say",
    "gossip", "rumor", "hearsay", "speculation", "guess",
    "unsubstantiated", "baseless", "unfounded", "claims",
    "supposedly", "reportedly", "possibly", "may",
]


def _find_emotion_keywords(text: str) -> list:
    """Find emotional manipulation keywords in text."""
    text_lower = text.lower()
    found = []
    for category, words in EMOTION_KEYWORDS.items():
        matches = [w for w in words if re.search(r'\b' + re.escape(w) + r'\b', text_lower)]
        found.extend(matches)
    return found


def _find_bias_keywords(text: str) -> list:
    """Find bias-related keywords in text."""
    text_lower = text.lower()
    found = []
    for word in BIAS_KEYWORDS:
        if re.search(r'\b' + re.escape(word) + r'\b', text_lower):
            found.append(word)
    return found


def _find_content_keywords(text: str) -> list:
    """Find credibility-related keywords (both positive and negative) in text."""
    text_lower = text.lower()
    found = []
    # Look for credible content keywords
    for word in CREDIBLE_CONTENT_KEYWORDS:
        if re.search(r'\b' + re.escape(word) + r'\b', text_lower):
            found.append(word)
    # Look for uncredible content keywords
    for word in UNCREDIBLE_CONTENT_KEYWORDS:
        if re.search(r'\b' + re.escape(word) + r'\b', text_lower):
            found.append(word)
    return found


def _find_flagged_words(text: str) -> dict:
    """Find manipulation keywords present in text, grouped by category (for emotion)."""
    text_lower = text.lower()
    found = {}
    for category, words in EMOTION_KEYWORDS.items():
        matches = [w for w in words if re.search(r'\b' + re.escape(w) + r'\b', text_lower)]
        if matches:
            found[category] = matches
    return found


def _chunk_text(text: str, max_chars: int = 1500) -> list[str]:
    """Split long text into chunks for model inference."""
    sentences = re.split(r'(?<=[.!?])\s+', text)
    chunks = []
    current = ""
    for s in sentences:
        if len(current) + len(s) < max_chars:
            current += " " + s
        else:
            if current:
                chunks.append(current.strip())
            current = s
    if current:
        chunks.append(current.strip())
    return chunks if chunks else [text[:max_chars]]


# Content Analysis

def analyse_content(text: str) -> dict:
    """
    Run fake news classification on the article text.
    Returns score 0-100 (higher = more authentic) plus raw model output.
    """
    classifier = _get_content_classifier()
    chunks = _chunk_text(text)

    fake_probs = []
    for chunk in chunks[:4]:  # Cap at 4 chunks for speed
        try:
            result = classifier(chunk)[0]
            label = result["label"].upper()
            score = result["score"]
            # Model labels: FAKE / REAL
            if "FAKE" in label:
                fake_probs.append(score)
            else:
                fake_probs.append(1 - score)
        except Exception:
            continue

    if not fake_probs:
        return {"score": 50, "fake_probability": 0.5, "error": "Model inference failed", "flagged_words": []}

    avg_fake_prob = float(np.mean(fake_probs))
    authenticity_score = round((1 - avg_fake_prob) * 100)
    
    # Find content-related keywords
    flagged_words = _find_content_keywords(text)

    return {
        "score": authenticity_score,
        "fake_probability": round(avg_fake_prob, 3),
        "chunks_analysed": len(fake_probs),
        "flagged_words": flagged_words,
    }


# Bias Detection

def analyse_bias(text: str) -> dict:
    """
    Detect bias/subjectivity in the article.
    Returns score 0-100 (higher = more biased) and direction hints.
    """
    classifier = _get_bias_classifier()
    chunks = _chunk_text(text)

    bias_probs = []
    for chunk in chunks[:4]:
        try:
            result = classifier(chunk)[0]
            label = result["label"].upper()
            score = result["score"]
            if "BIASED" in label or label == "LABEL_1":
                bias_probs.append(score)
            else:
                bias_probs.append(1 - score)
        except Exception:
            continue

    if not bias_probs:
        return {"score": 50, "error": "Model inference failed", "flagged_words": []}

    avg_bias = float(np.mean(bias_probs))
    bias_score = round(avg_bias * 100)
    
    # Find bias-related keywords
    flagged_words = _find_bias_keywords(text)

    # Classify level
    if bias_score >= 70:
        level = "High"
    elif bias_score >= 40:
        level = "Moderate"
    else:
        level = "Low"

    return {
        "score": bias_score,
        "level": level,
        "bias_probability": round(avg_bias, 3),
        "flagged_words": flagged_words,
    }


# Emotional Manipulation Detection

def analyse_emotion(text: str) -> dict:
    """
    Detect emotional manipulation signals in the text.
    Returns manipulation score 0-100, dominant emotions, and flagged words.
    """
    classifier = _get_emotion_classifier()
    chunks = _chunk_text(text)

    # Aggregate emotion scores across chunks
    emotion_totals = {}
    count = 0

    for chunk in chunks[:4]:
        try:
            results = classifier(chunk)[0]
            for item in results:
                emotion = item["label"].lower()
                emotion_totals[emotion] = emotion_totals.get(emotion, 0) + item["score"]
            count += 1
        except Exception:
            continue

    # Find flagged manipulation keywords
    flagged_words = _find_flagged_words(text)
    total_flagged = sum(len(v) for v in flagged_words.values())

    if not emotion_totals or count == 0:
        return {
            "score": min(total_flagged * 8, 100),
            "flagged_words": flagged_words,
            "dominant_emotions": [],
            "error": "Emotion model inference failed, using keyword analysis only",
        }

    # Average across chunks
    avg_emotions = {k: v / count for k, v in emotion_totals.items()}

    # High-manipulation emotions: anger, fear, disgust
    manipulative_emotions = ["anger", "fear", "disgust"]
    neutral_emotions = ["neutral", "joy"]

    manipulation_signal = sum(avg_emotions.get(e, 0) for e in manipulative_emotions)
    neutral_signal = sum(avg_emotions.get(e, 0) for e in neutral_emotions)

    # Combine model signal with keyword signal
    model_score = manipulation_signal / max(manipulation_signal + neutral_signal, 1e-6)
    keyword_boost = min(total_flagged * 0.05, 0.3)
    raw_score = min(model_score + keyword_boost, 1.0)
    manipulation_score = round(raw_score * 100)

    # Top 3 emotions
    sorted_emotions = sorted(avg_emotions.items(), key=lambda x: x[1], reverse=True)
    dominant = [{"emotion": e, "intensity": round(s * 100)} for e, s in sorted_emotions[:3]]

    return {
        "score": manipulation_score,
        "dominant_emotions": dominant,
        "flagged_words": flagged_words,
        "raw_emotion_scores": {k: round(v, 3) for k, v in avg_emotions.items()},
    }
