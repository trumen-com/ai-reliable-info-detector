"""
AI Reliable Info Detector — Test Suite
Run this BEFORE the full app to validate all logic locally.

Tests:
  1. Source credibility lookup (no models needed)
  2. Explainer text output (no models needed)
  3. Score formula / weight logic (no models needed)
  4. Full pipeline with MOCKED models (no downloads needed)
  5. Full pipeline with REAL models (requires: pip install -r requirements.txt)

Usage:
  python test_suite.py            # Runs tests 1-4 (instant, no downloads)
  python test_suite.py --real     # Runs all 5 tests (downloads models on first run)
"""

import sys
import os
import json
import argparse
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.dirname(__file__))

# Colour output helpers
GREEN  = "\033[92m"
RED    = "\033[91m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
BOLD   = "\033[1m"
RESET  = "\033[0m"

passed = 0
failed = 0
warnings = 0


def ok(msg):
    global passed
    passed += 1
    print(f"  {GREEN}✓{RESET} {msg}")


def fail(msg):
    global failed
    failed += 1
    print(f"  {RED}✗ FAIL:{RESET} {msg}")


def warn(msg):
    global warnings
    warnings += 1
    print(f"  {YELLOW}⚠ WARN:{RESET} {msg}")


def section(title):
    print(f"\n{BOLD}{CYAN}{'─'*60}{RESET}")
    print(f"{BOLD}{CYAN}  {title}{RESET}")
    print(f"{BOLD}{CYAN}{'─'*60}{RESET}")


# Sample Articles
# These are synthetic test cases, not real scraped content.

ARTICLES = {
    "credible_reuters": {
        "url": "https://www.reuters.com/world/example",
        "text": (
            "The Federal Reserve raised interest rates by 25 basis points on Wednesday, "
            "citing continued concerns about inflation. Fed Chair Jerome Powell said in a "
            "press conference that the decision was unanimous among the 12-member Federal "
            "Open Market Committee. Economists had largely anticipated the move following "
            "last month's consumer price index data, which showed inflation running at 3.2 "
            "percent annually. The central bank indicated it would assess incoming data "
            "before deciding on further adjustments. Markets responded with modest gains, "
            "with the S&P 500 closing up 0.4 percent. The decision brings the federal funds "
            "rate to a target range of 5.25 to 5.5 percent, the highest level in 22 years."
        ),
        "expected_risk": "Low Risk",
        "notes": "Should score high — neutral language, credible domain, factual reporting",
    },
    "fake_conspiracy": {
        "url": "https://www.infowars.com/posts/example",
        "text": (
            "SHOCKING SECRET EXPOSED: The deep state globalist elite are TERRIFIED that you'll "
            "find out the truth they've been hiding for decades! Scientists confirm that vaccines "
            "contain mind control nanobots — and they're using 5G towers to activate them! "
            "The mainstream media won't tell you this because they're all PUPPETS of the corrupt "
            "globalist cabal. Wake up, sheeple! This nightmare agenda will DESTROY our freedom "
            "and OBLITERATE everything we hold dear. Millions are dying and the government is "
            "covering it up. Share this before they silence us forever! The catastrophic truth "
            "will horrify you. They are coming for your children. Act NOW before it's too late!"
        ),
        "expected_risk": "Very High Risk",
        "notes": "Should score very low — conspiracy language, emotional manipulation, low-cred source",
    },
    "biased_opinion": {
        "url": "https://www.huffpost.com/entry/example",
        "text": (
            "The radical extremist government has once again betrayed ordinary citizens with "
            "its disastrous and utterly corrupt economic policies. Every single decision made "
            "by these incompetent puppets has absolutely destroyed the middle class. Obviously, "
            "anyone with common sense can see that this shameful administration is completely "
            "and totally beholden to corporate overlords. The outrageous tax policy is nothing "
            "but a disgusting handout to billionaires while hard-working families suffer. "
            "Experts universally agree that this catastrophic approach is guaranteed to fail "
            "and will inevitably lead to complete economic collapse. The corrupt regime must "
            "be held accountable for this appalling betrayal of the people who trusted them."
        ),
        "expected_risk": "High Risk",
        "notes": "High bias + emotion, mixed source — should score moderate-to-low",
    },
    "satire": {
        "url": "https://www.theonion.com/example",
        "text": (
            "Nation's Dogs Report Absolutely No Awareness Of Anything Happening In World. "
            "EVERYWHERE — Confirming that the situation remains completely unchanged from "
            "every previous moment in recorded history, the nation's dogs reported Monday "
            "that they remain absolutely unaware of anything happening in the world. "
            "'Ball,' said an estimated 90 million dogs simultaneously. Sources confirmed "
            "that despite ongoing international tensions and a turbulent economic climate, "
            "local dogs continued to stare at walls, bark at nothing, and aggressively "
            "pursue their own tails. At press time, all dogs had collectively determined "
            "that something extremely suspicious was occurring outside the window."
        ),
        "expected_risk": "Very High Risk",  # Satire site = very low source credibility
        "notes": "Satire site — source credibility should be very low, content neutral",
    },
    "no_url": {
        "url": "",
        "text": (
            "Scientists at the University of Cambridge have published a new study suggesting "
            "that regular exercise may reduce the risk of developing type 2 diabetes by up to "
            "30 percent. The research, published in the journal Nature Medicine, followed "
            "12,000 participants over a period of eight years. Lead researcher Dr. Sarah Chen "
            "noted that even moderate activity, such as a 30-minute walk five days per week, "
            "produced measurable metabolic benefits. The findings align with existing WHO "
            "guidelines recommending 150 minutes of moderate aerobic activity per week. "
            "However, researchers cautioned that exercise alone is not a substitute for "
            "medical treatment in patients already diagnosed with the condition."
        ),
        "expected_risk": "Low Risk",
        "notes": "No URL — should trigger weight disclaimer, still score well on content",
    },
}


# Test 1: Source Credibility

def test_source_credibility():
    section("TEST 1 — Source Credibility Lookup")
    from models.source_credibility import analyse_source

    cases = [
        ("https://www.reuters.com/article", 90, 100, "Reuters"),
        ("https://www.bbc.co.uk/news", 90, 100, "BBC"),
        ("https://www.infowars.com/post", 0, 20, "InfoWars"),
        ("https://www.theonion.com/article", 0, 15, "The Onion (satire)"),
        ("https://news.bbc.com/article", 90, 100, "BBC subdomain"),
        ("https://www.unknownblog123.net/post", 30, 55, "Unknown domain"),
        ("", None, None, "No URL"),
    ]

    for url, min_score, max_score, label in cases:
        result = analyse_source(url)
        score = result["score"]

        if min_score is None:
            if not result["available"]:
                ok(f"{label}: correctly marked as unavailable")
            else:
                fail(f"{label}: should be unavailable when no URL provided")
        elif score is None:
            fail(f"{label}: returned None score unexpectedly")
        elif min_score <= score <= max_score:
            ok(f"{label}: score {score} within expected range [{min_score}–{max_score}]")
        else:
            fail(f"{label}: score {score} OUTSIDE expected range [{min_score}–{max_score}]")


# Test 2: Explainer Output Quality

def test_explainer_quality():
    section("TEST 2 — Explainer Text Quality")
    from utils.explainer import (
        explain_content, explain_bias, explain_emotion,
        explain_source, generate_verdict
    )

    MIN_EXPLANATION_LENGTH = 80  # Characters

    # Content explanations across score range
    for score, fake_prob, label in [
        (90, 0.10, "high credibility content"),
        (65, 0.35, "moderate content"),
        (35, 0.65, "low credibility content"),
        (15, 0.85, "very low credibility content"),
    ]:
        exp = explain_content(score, fake_prob)
        if len(exp) >= MIN_EXPLANATION_LENGTH:
            ok(f"Content explanation ({label}): {len(exp)} chars")
        else:
            fail(f"Content explanation ({label}): too short ({len(exp)} chars)")

        # Must NOT say "This is fake news"
        if "this is fake" in exp.lower():
            fail(f"Content explanation contains forbidden phrase 'this is fake'")
        else:
            ok(f"Content explanation ({label}): no forbidden 'this is fake' phrase")

    # Bias explanations
    for score, label in [(10, "low bias"), (50, "moderate bias"), (85, "high bias")]:
        exp = explain_bias(score, "")
        if len(exp) >= MIN_EXPLANATION_LENGTH:
            ok(f"Bias explanation ({label}): {len(exp)} chars")
        else:
            fail(f"Bias explanation ({label}): too short")

    # Emotion explanations
    flagged = {"fear": ["terrifying", "deadly"], "outrage": ["disgusting"]}
    emotions = [{"emotion": "anger", "intensity": 72}, {"emotion": "fear", "intensity": 55}]
    for score, label in [(10, "low emotion"), (50, "moderate emotion"), (85, "high emotion")]:
        exp = explain_emotion(score, emotions, flagged)
        if len(exp) >= MIN_EXPLANATION_LENGTH:
            ok(f"Emotion explanation ({label}): {len(exp)} chars")
        else:
            fail(f"Emotion explanation ({label}): too short")

    # Verdict generation
    for score, expected_risk in [
        (85, "Low Risk"),
        (65, "Moderate Risk"),
        (45, "High Risk"),
        (20, "Very High Risk"),
    ]:
        verdict = generate_verdict(score, {"content": score, "source": score, "bias": 100 - score, "emotion": 100 - score})
        if verdict["risk_level"] == expected_risk:
            ok(f"Verdict score {score} → '{expected_risk}'")
        else:
            fail(f"Verdict score {score} → got '{verdict['risk_level']}', expected '{expected_risk}'")


# Test 3: Score Formula & Weight Logic

def test_score_formula():
    section("TEST 3 — Score Formula & Weight Logic")

    # Simulate the formula manually
    def calc_with_source(content, source, bias, emotion):
        return round(0.40 * content + 0.30 * source + 0.20 * (100 - bias) + 0.10 * (100 - emotion))

    def calc_without_source(content, bias, emotion):
        return round(0.55 * content + 0.28 * (100 - bias) + 0.17 * (100 - emotion))

    # Perfect credible article
    score = calc_with_source(95, 95, 5, 5)
    if score >= 85:
        ok(f"Perfect credible article → {score}/100 (expected ≥85)")
    else:
        fail(f"Perfect credible article → {score}/100 (expected ≥85)")

    # Clear misinformation
    score = calc_with_source(10, 5, 90, 90)
    if score <= 25:
        ok(f"Clear misinformation → {score}/100 (expected ≤25)")
    else:
        fail(f"Clear misinformation → {score}/100 (expected ≤25)")

    # No URL — weight redistribution
    with_url    = calc_with_source(70, 70, 30, 30)
    without_url = calc_without_source(70, 30, 30)
    if abs(with_url - without_url) <= 20:
        ok(f"Weight redistribution reasonable: with URL={with_url}, without={without_url} (diff={abs(with_url-without_url)})")
    else:
        warn(f"Weight redistribution large gap: with URL={with_url}, without={without_url} — consider reviewing weights")

    # Good content + bad source: should land in Moderate Risk zone (45-65)
    # A well-written article from a known bad source is still suspicious.
    score = calc_with_source(75, 5, 20, 20)
    if 45 <= score <= 65:
        ok(f"Good content + bad source → {score}/100 (correctly Moderate Risk zone 45-65)")
    else:
        warn(f"Good content + bad source → {score}/100 — outside expected Moderate Risk zone [45-65]")

    # Range sanity: scores should always be 0–100
    for c, s, b, e in [(0,0,100,100), (100,100,0,0), (50,50,50,50)]:
        score = calc_with_source(c, s, b, e)
        if 0 <= score <= 100:
            ok(f"Score ({c},{s},{b},{e}) → {score} is in valid range [0–100]")
        else:
            fail(f"Score ({c},{s},{b},{e}) → {score} OUT OF RANGE")


# Test 4: Full Pipeline with Mocked Models

def test_pipeline_mocked():
    section("TEST 4 — Full Pipeline (Mocked Models)")

    # Mock all three HuggingFace pipelines so no download needed
    def make_mock_content_pipeline(fake_score=0.8):
        mock = MagicMock()
        mock.return_value = [{"label": "FAKE", "score": fake_score}]
        return mock

    def make_mock_bias_pipeline(bias_score=0.7):
        mock = MagicMock()
        mock.return_value = [{"label": "BIASED", "score": bias_score}]
        return mock

    def make_mock_emotion_pipeline(anger=0.6, fear=0.3):
        mock = MagicMock()
        mock.return_value = [[
            {"label": "anger", "score": anger},
            {"label": "fear", "score": fear},
            {"label": "neutral", "score": 0.05},
            {"label": "joy", "score": 0.03},
            {"label": "disgust", "score": 0.02},
        ]]
        return mock

    # Stub out transformers before importing the module
    import types
    fake_transformers = types.ModuleType("transformers")
    fake_transformers.pipeline = MagicMock()
    sys.modules.setdefault("transformers", fake_transformers)
    # Also stub torch if missing
    if "torch" not in sys.modules:
        sys.modules["torch"] = types.ModuleType("torch")

    import models.nlp_pipeline as nlp_mod
    with patch.object(nlp_mod, "_get_content_classifier", return_value=make_mock_content_pipeline(0.85)), \
         patch.object(nlp_mod, "_get_bias_classifier",    return_value=make_mock_bias_pipeline(0.75)), \
         patch.object(nlp_mod, "_get_emotion_classifier", return_value=make_mock_emotion_pipeline(0.65, 0.25)):

        from analysis import run_analysis

        print(f"\n  {CYAN}Running mocked analysis on 5 test articles...{RESET}\n")

        for name, article in ARTICLES.items():
            try:
                report = run_analysis(article["text"], url=article["url"])

                final = report["final_score"]
                risk  = report["verdict"]["risk_level"]
                has_weight_note = report.get("weight_note") is not None
                url_provided    = article["url"] != ""

                # Basic structure checks
                assert "pillars" in report, "Missing pillars key"
                assert "content" in report["pillars"], "Missing content pillar"
                assert "source"  in report["pillars"], "Missing source pillar"
                assert "bias"    in report["pillars"], "Missing bias pillar"
                assert "emotion" in report["pillars"], "Missing emotion pillar"
                assert 0 <= final <= 100, f"Score {final} out of range"

                # Weight note should appear iff no URL
                if not url_provided and not has_weight_note:
                    fail(f"{name}: missing weight disclaimer when no URL provided")
                elif url_provided and has_weight_note:
                    fail(f"{name}: unexpected weight disclaimer when URL WAS provided")
                else:
                    ok(f"{name}: weight disclaimer logic correct")

                # Explanations should be non-empty
                for pillar in ["content", "source", "bias", "emotion"]:
                    exp = report["pillars"][pillar].get("explanation", "")
                    if len(exp) > 50:
                        ok(f"{name} → {pillar} explanation present ({len(exp)} chars)")
                    else:
                        fail(f"{name} → {pillar} explanation missing or too short")

                print(f"  {BOLD}  [{name}]{RESET}")
                print(f"     Score: {final}/100  |  Risk: {risk}")
                print(f"     Notes: {article['notes']}")
                print()

            except Exception as e:
                fail(f"{name}: pipeline raised exception — {e}")
                import traceback
                traceback.print_exc()


# Test 5: Real Models

def test_real_models():
    section("TEST 5 — Real Models (Live HuggingFace Inference)")
    print(f"  {YELLOW}Downloading models on first run (~500MB). Please wait...{RESET}\n")

    try:
        from analysis import run_analysis

        for name, article in ARTICLES.items():
            print(f"  {CYAN}Analysing: {name}{RESET}")
            report = run_analysis(article["text"], url=article["url"])
            final  = report["final_score"]
            risk   = report["verdict"]["risk_level"]
            expected = article["expected_risk"]

            print(f"    Score : {final}/100")
            print(f"    Risk  : {risk}")
            print(f"    Expect: {expected}")
            print(f"    Notes : {article['notes']}")

            # Soft check — risk level should roughly match expectation
            # (models may vary slightly; we warn rather than hard-fail)
            if risk == expected:
                ok(f"{name}: risk level matches expectation '{expected}'")
            else:
                warn(f"{name}: expected '{expected}', got '{risk}' — review model outputs")
            print()

    except ImportError as e:
        fail(f"Could not import models — are dependencies installed? ({e})")
    except Exception as e:
        fail(f"Unexpected error during real model test: {e}")
        import traceback
        traceback.print_exc()


# Runner 

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--real", action="store_true", help="Also run Test 5 with real HuggingFace models")
    args = parser.parse_args()

    print(f"\n{BOLD}{'═'*60}")
    print(f"  AI Reliable Info Detector — Test Suite")
    print(f"{'═'*60}{RESET}")

    test_source_credibility()
    test_explainer_quality()
    test_score_formula()
    test_pipeline_mocked()

    if args.real:
        test_real_models()
    else:
        print(f"\n{YELLOW}  Skipping Test 5 (real models). Run with --real to include it.{RESET}")

    # Summary 
    total = passed + failed
    print(f"\n{BOLD}{'═'*60}")
    print(f"  Results: {GREEN}{passed} passed{RESET}  {RED}{failed} failed{RESET}  {YELLOW}{warnings} warnings{RESET}  ({total} total)")
    print(f"{'═'*60}{RESET}\n")

    if failed > 0:
        print(f"{RED}  ✗ Some tests failed. Review output above before running the app.{RESET}\n")
        sys.exit(1)
    elif warnings > 0:
        print(f"{YELLOW}  ⚠ All tests passed with warnings. Review warnings above.{RESET}\n")
    else:
        print(f"{GREEN}  ✓ All tests passed. Safe to run the app.{RESET}\n")
