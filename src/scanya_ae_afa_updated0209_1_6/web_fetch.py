"""Download a job posting from a URL and turn it into plain text for the LLM prompt.

The LLM cannot open URLs by itself, so when the user pastes a link instead of a job
description, the app fetches the page here and sends the page text to the model.

Public functions: is_url(), fetch_job_description().
"""

import httpx
from bs4 import BeautifulSoup

# Keep the prompt a reasonable size: job postings rarely need more than this.
MAX_CHARS = 15_000

# Below this, the page probably needs a login or JavaScript (e.g. LinkedIn) and holds no posting.
MIN_CHARS = 200

# Some sites block requests without a browser-like User-Agent.
_HEADERS = {"User-Agent": "Mozilla/5.0 (interview-practice-app)"}


def is_url(text: str) -> bool:
    """True if the input is a single http(s) link rather than a pasted description."""
    text = text.strip()
    return text.startswith(("http://", "https://")) and " " not in text and "\n" not in text


def fetch_job_description(url: str) -> str:
    """Download the page at `url` and return its readable text (at most MAX_CHARS).

    Raises:
        ValueError: if the page cannot be downloaded or contains too little text.
    """
    try:
        response = httpx.get(url.strip(), headers=_HEADERS, timeout=15, follow_redirects=True)
        response.raise_for_status()
    except httpx.HTTPError as error:
        raise ValueError(f"Could not open the URL ({error}). Please paste the job description instead.") from error

    # Drop elements that never contain the posting text, then collapse whitespace.
    soup = BeautifulSoup(response.text, "html.parser")
    for tag in soup(["script", "style", "noscript", "nav", "header", "footer", "svg"]):
        tag.decompose()
    text = " ".join(soup.get_text(separator=" ").split())

    if len(text) < MIN_CHARS:
        raise ValueError(
            "The page has almost no readable text (it may need a login or JavaScript). "
            "Please paste the job description instead."
        )
    return text[:MAX_CHARS]
