import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import re


def extract_domain(url: str) -> str:
    """Extract root domain from a URL."""
    try:
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        # Strip www.
        if domain.startswith("www."):
            domain = domain[4:]
        return domain
    except Exception:
        return ""


def scrape_article(url: str) -> dict:
    """
    Scrape article text and metadata from a URL.
    Returns dict with keys: title, text, domain, success, error
    """
    result = {
        "title": "",
        "text": "",
        "domain": "",
        "success": False,
        "error": None,
    }

    try:
        domain = extract_domain(url)
        result["domain"] = domain

        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        }

        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "lxml")

        # Extract title
        title_tag = soup.find("title")
        if title_tag:
            result["title"] = title_tag.get_text(strip=True)

        # Try common article containers first
        article_text = ""
        for selector in ["article", "main", '[role="main"]', ".article-body", ".post-content", ".entry-content"]:
            container = soup.select_one(selector)
            if container:
                paragraphs = container.find_all("p")
                article_text = " ".join(p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 40)
                if len(article_text) > 200:
                    break

        # Fallback: grab all paragraphs
        if len(article_text) < 200:
            paragraphs = soup.find_all("p")
            article_text = " ".join(p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 40)

        # Clean up whitespace
        article_text = re.sub(r"\s+", " ", article_text).strip()

        if len(article_text) < 100:
            result["error"] = "Could not extract sufficient article text from this URL. Try pasting the text directly."
            return result

        result["text"] = article_text
        result["success"] = True

    except requests.exceptions.Timeout:
        result["error"] = "Request timed out. The site may be slow or blocking scrapers. Try pasting the text directly."
    except requests.exceptions.HTTPError as e:
        result["error"] = f"HTTP error {e.response.status_code}. The page may require login or be unavailable."
    except requests.exceptions.ConnectionError:
        result["error"] = "Could not connect to the URL. Check the address and your internet connection."
    except Exception as e:
        result["error"] = f"Unexpected error while scraping: {str(e)}"

    return result
