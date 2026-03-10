from data.credibility_db import (
    CREDIBILITY_DB,
    UNKNOWN_DOMAIN_SCORE,
    UNKNOWN_DOMAIN_LABEL,
    UNKNOWN_DOMAIN_NOTES,
)
from utils.scraper import extract_domain


def analyse_source(url: str) -> dict:
    """
    Look up domain credibility from the database.
    Returns score, label, notes, domain, and found flag.
    """
    if not url or not url.strip():
        return {
            "score": None,
            "label": "No URL Provided",
            "notes": "No source URL was provided. Source credibility could not be assessed.",
            "domain": None,
            "found": False,
            "available": False,
        }

    domain = extract_domain(url)

    if not domain:
        return {
            "score": None,
            "label": "Invalid URL",
            "notes": "The URL could not be parsed to extract a domain name.",
            "domain": domain,
            "found": False,
            "available": False,
        }

    # Direct lookup
    if domain in CREDIBILITY_DB:
        entry = CREDIBILITY_DB[domain]
        return {
            "score": entry["score"],
            "label": entry["label"],
            "notes": entry["notes"],
            "domain": domain,
            "found": True,
            "available": True,
        }

    # Try parent domain (e.g. news.bbc.com -> bbc.com)
    parts = domain.split(".")
    if len(parts) > 2:
        parent = ".".join(parts[-2:])
        if parent in CREDIBILITY_DB:
            entry = CREDIBILITY_DB[parent]
            return {
                "score": entry["score"],
                "label": entry["label"],
                "notes": entry["notes"] + f" (matched via parent domain: {parent})",
                "domain": domain,
                "found": True,
                "available": True,
            }

    # Unknown domain
    return {
        "score": UNKNOWN_DOMAIN_SCORE,
        "label": UNKNOWN_DOMAIN_LABEL,
        "notes": UNKNOWN_DOMAIN_NOTES,
        "domain": domain,
        "found": False,
        "available": True,
    }
