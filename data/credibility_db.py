# Source Credibility Database
# Based on Media Bias/Fact Check and NewsGuard public data
# Score: 0-100 (higher = more credible)

CREDIBILITY_DB = {
    # Tier 1 — High credibility (80-100)
    "reuters.com": {"score": 97, "label": "High Credibility", "notes": "International wire service, strict editorial standards"},
    "apnews.com": {"score": 96, "label": "High Credibility", "notes": "Associated Press, non-partisan wire service"},
    "bbc.com": {"score": 94, "label": "High Credibility", "notes": "Public broadcaster with editorial charter"},
    "bbc.co.uk": {"score": 94, "label": "High Credibility", "notes": "Public broadcaster with editorial charter"},
    "npr.org": {"score": 92, "label": "High Credibility", "notes": "Public radio, strong editorial standards"},
    "theguardian.com": {"score": 88, "label": "High Credibility", "notes": "Established broadsheet, transparent corrections policy"},
    "nytimes.com": {"score": 87, "label": "High Credibility", "notes": "Major newspaper of record, though opinion section is distinct"},
    "washingtonpost.com": {"score": 86, "label": "High Credibility", "notes": "Major newspaper, Pulitzer-winning investigative team"},
    "economist.com": {"score": 90, "label": "High Credibility", "notes": "Long-standing analytical publication"},
    "nature.com": {"score": 98, "label": "High Credibility", "notes": "Peer-reviewed scientific journal"},
    "science.org": {"score": 97, "label": "High Credibility", "notes": "Peer-reviewed scientific journal"},
    "who.int": {"score": 95, "label": "High Credibility", "notes": "World Health Organization official source"},
    "cdc.gov": {"score": 94, "label": "High Credibility", "notes": "US Centers for Disease Control official source"},
    "gov.uk": {"score": 90, "label": "High Credibility", "notes": "UK Government official source"},
    "europa.eu": {"score": 89, "label": "High Credibility", "notes": "European Union official source"},
    "aljazeera.com": {"score": 82, "label": "High Credibility", "notes": "International broadcaster with broad coverage"},
    "bloomberg.com": {"score": 88, "label": "High Credibility", "notes": "Financial news, strong fact-checking record"},
    "ft.com": {"score": 89, "label": "High Credibility", "notes": "Financial Times, strong editorial standards"},
    "politifact.com": {"score": 91, "label": "High Credibility", "notes": "Dedicated fact-checking organisation"},
    "factcheck.org": {"score": 92, "label": "High Credibility", "notes": "Dedicated fact-checking organisation"},
    "snopes.com": {"score": 88, "label": "High Credibility", "notes": "Established fact-checking site"},

    # Tier 2 — Moderate credibility (50-79)
    "foxnews.com": {"score": 58, "label": "Mixed Credibility", "notes": "High audience reach but opinion content mixed with news"},
    "cnn.com": {"score": 65, "label": "Mixed Credibility", "notes": "Major outlet but noted for sensational presentation"},
    "msnbc.com": {"score": 60, "label": "Mixed Credibility", "notes": "Strong opinion lean, news accuracy generally maintained"},
    "nypost.com": {"score": 52, "label": "Mixed Credibility", "notes": "Tabloid style, some accuracy concerns in reporting"},
    "dailymail.co.uk": {"score": 45, "label": "Mixed Credibility", "notes": "High traffic tabloid with noted accuracy issues"},
    "huffpost.com": {"score": 62, "label": "Mixed Credibility", "notes": "Strong editorial lean, factual reporting varies"},
    "vice.com": {"score": 63, "label": "Mixed Credibility", "notes": "Varied quality depending on section"},
    "buzzfeed.com": {"score": 55, "label": "Mixed Credibility", "notes": "News division is separate from entertainment; quality varies"},
    "newsweek.com": {"score": 60, "label": "Mixed Credibility", "notes": "Formerly prestigious, quality has varied in recent years"},

    # Tier 3 — Low credibility (0-49)
    "infowars.com": {"score": 5, "label": "Very Low Credibility", "notes": "Known conspiracy and misinformation source"},
    "naturalnews.com": {"score": 8, "label": "Very Low Credibility", "notes": "Repeatedly flagged for health misinformation"},
    "breitbart.com": {"score": 22, "label": "Low Credibility", "notes": "Strong ideological bias, frequent factual inaccuracies"},
    "beforeitsnews.com": {"score": 6, "label": "Very Low Credibility", "notes": "User-submitted conspiracy content"},
    "theonion.com": {"score": 10, "label": "Satire", "notes": "Satire publication — not intended as factual news"},
    "babylonbee.com": {"score": 10, "label": "Satire", "notes": "Christian satire publication — not intended as factual news"},
    "worldnewsdailyreport.com": {"score": 3, "label": "Very Low Credibility", "notes": "Known fabricated news site"},
    "empirenews.net": {"score": 3, "label": "Very Low Credibility", "notes": "Known fabricated news site"},
    "nationalreport.net": {"score": 4, "label": "Very Low Credibility", "notes": "Known fabricated news site"},
    "yournewswire.com": {"score": 7, "label": "Very Low Credibility", "notes": "Repeatedly flagged for misinformation"},
    "newsmax.com": {"score": 38, "label": "Low Credibility", "notes": "Noted for promoting unverified claims"},
    "oann.com": {"score": 25, "label": "Low Credibility", "notes": "One America News, repeated misinformation flags"},
}

UNKNOWN_DOMAIN_SCORE = 40
UNKNOWN_DOMAIN_LABEL = "Unknown Source"
UNKNOWN_DOMAIN_NOTES = "This domain has no established credibility record in our database. Exercise caution."
