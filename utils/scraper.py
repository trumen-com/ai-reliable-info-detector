import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import re

# Sites known to block scrapers — show a helpful message instead of a cryptic error
KNOWN_PAYWALLS = {
    "reuters.com":        "Reuters requires a subscription login. Please copy and paste the article text manually.",
    "ft.com":             "The Financial Times is paywalled. Please paste the article text manually.",
    "wsj.com":            "The Wall Street Journal is paywalled. Please paste the article text manually.",
    "nytimes.com":        "The New York Times may require login. If you hit a paywall, paste the article text manually.",
    "washingtonpost.com": "The Washington Post may require login. If you hit a paywall, paste the article text manually.",
    "bloomberg.com":      "Bloomberg requires a subscription. Please paste the article text manually.",
    "economist.com":      "The Economist is paywalled. Please paste the article text manually.",
    "thetimes.co.uk":     "The Times is paywalled. Please paste the article text manually.",
}


def extract_domain(url: str) -> str:
    try:
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        if domain.startswith("www."):
            domain = domain[4:]
        return domain
    except Exception:
        return ""


def scrape_article(url: str) -> dict:
    result = {"title": "", "text": "", "domain": "", "success": False, "error": None}

    try:
        domain = extract_domain(url)
        result["domain"] = domain

        # Check for known paywalled sites before even trying
        for known, msg in KNOWN_PAYWALLS.items():
            if domain == known or domain.endswith("." + known):
                result["error"] = f"⚠️ {msg}"
                return result

        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/122.0.0.0 Safari/537.36"
            ),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
        }

        response = requests.get(url, headers=headers, timeout=12)

        # Handle auth/paywall HTTP errors specifically
        if response.status_code == 401:
            result["error"] = f"⚠️ This site requires login (HTTP 401). Please paste the article text manually."
            return result
        if response.status_code == 403:
            result["error"] = f"⚠️ Access denied by this site (HTTP 403). Please paste the article text manually."
            return result
        if response.status_code == 429:
            result["error"] = f"⚠️ Too many requests to this site (HTTP 429). Try again in a moment, or paste the text manually."
            return result

        response.raise_for_status()

        soup = BeautifulSoup(response.text, "lxml")

        # Title
        title_tag = soup.find("title")
        if title_tag:
            result["title"] = title_tag.get_text(strip=True)

        # Try article containers in priority order
        article_text = ""
        selectors = [
            "article", "main", '[role="main"]',
            ".article-body", ".article__body", ".article-content",
            ".post-content", ".entry-content", ".story-body",
            ".content-body", ".body-content", "#article-body",
        ]
        for selector in selectors:
            container = soup.select_one(selector)
            if container:
                paras = container.find_all("p")
                candidate = " ".join(p.get_text(strip=True) for p in paras if len(p.get_text(strip=True)) > 40)
                if len(candidate) > 200:
                    article_text = candidate
                    break

        # Fallback: all paragraphs
        if len(article_text) < 200:
            paras = soup.find_all("p")
            article_text = " ".join(p.get_text(strip=True) for p in paras if len(p.get_text(strip=True)) > 40)

        # Clean whitespace
        article_text = re.sub(r"\s+", " ", article_text).strip()

        # Soft paywall detection — if text is very short despite a 200 response
        if len(article_text) < 150:
            # Check for paywall-indicator phrases
            page_text = soup.get_text().lower()
            paywall_phrases = ["subscribe to read", "sign in to read", "create a free account", 
                               "subscribe now", "log in to continue", "premium content"]
            if any(p in page_text for p in paywall_phrases):
                result["error"] = "⚠️ This article appears to be behind a paywall. Please paste the article text manually."
                return result
            result["error"] = "Could not extract enough text from this page. Try pasting the article text manually."
            return result

        result["text"] = article_text
        result["success"] = True

    except requests.exceptions.Timeout:
        result["error"] = "⚠️ Request timed out. The site may be slow or blocking automated access. Try pasting the text manually."
    except requests.exceptions.HTTPError as e:
        code = e.response.status_code if e.response else "?"
        result["error"] = f"⚠️ HTTP error {code}. This page may require login or be unavailable. Try pasting the text manually."
    except requests.exceptions.ConnectionError:
        result["error"] = "⚠️ Could not connect. Check the URL and your internet connection."
    except Exception as e:
        result["error"] = f"⚠️ Unexpected error: {str(e)}. Try pasting the text manually."

    return result
