#  AI Reliable Info Detector

**AI-Powered Misinformation & Bias Detection System**

Aligned with SDG 4 (Quality Education) and SDG 16 (Peace, Justice & Strong Institutions).

---

## Quick Setup (4 steps)

### 1. Clone / download the project
```bash
cd ai-reliable-info-detector
```

### 2. Create a virtual environment (recommended)
```bash
python -m venv venv
source venv/bin/activate        # Mac/Linux
venv\Scripts\activate           # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the app
```bash
streamlit run app.py
```

The app opens at `http://localhost:8501`

> **Note:** First run will download ~500MB of AI models from HuggingFace. Subsequent runs are fast (models are cached).

---

## Project Structure

```
ai-reliable-info-detector/
├── app.py                    # Main Streamlit dashboard
├── analysis.py               # Orchestrator — combines all four pillars
├── requirements.txt
├── .streamlit/
│   └── config.toml           # Dark theme config
├── models/
│   ├── nlp_pipeline.py       # Content, bias & emotion HuggingFace models
│   └── source_credibility.py # Domain credibility lookup
├── utils/
│   ├── scraper.py            # URL -> article text extractor
│   └── explainer.py          # Explanation generator (the differentiator)
└── data/
    └── credibility_db.py     # Source credibility database (~50 domains)
```

---

## Four-Pillar Analysis

| Pillar | Model | What it detects |
|--------|-------|----------------|
| Content Analysis | `hamzab/roberta-fake-news-classification` | Fake news language patterns |
| Source Credibility | Curated DB (MBFC-based) | Domain trustworthiness |
| Bias Detection | `valurank/distilroberta-bias` | Subjective framing |
| Emotional Manipulation | `j-hartmann/emotion-english-distilroberta-base` | Fear, anger, outrage signals |

---

## Final Score Formula

**When URL is provided:**
```
Score = 0.40 × Content + 0.30 × Source + 0.20 × BiasNeutrality + 0.10 × EmotionNeutrality
```

**When no URL:**
```
Score = 0.55 × Content + 0.28 × BiasNeutrality + 0.17 × EmotionNeutrality
```
(Source pillar excluded; weights redistributed — disclaimer shown to user)

---

## Important Disclaimer

TruthLens identifies **indicators commonly associated with misinformation**.
It does not make definitive factual determinations.
Always verify with independent fact-checking sources.

---

## SDG Alignment

- **SDG 4 — Quality Education:** Improves media literacy through explainable AI analysis
- **SDG 16 — Peace & Strong Institutions:** Combats misinformation that undermines democratic stability
