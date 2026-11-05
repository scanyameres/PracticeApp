"""Download a job posting from a URL and turn it into plain text for the LLM prompt.

The LLM cannot open URLs by itself, so when the user pastes a link instead of a job
description, the app fetches the page here and sends the page text to the model.

Public functions: is_url(), fetch_job_description().
"""

import ipaddress
import socket

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


def _block_private_hosts(request: httpx.Request) -> None:
    """Security guard: refuse URLs that point to this machine or a private network.

    Otherwise a user could make the app open internal pages (e.g. http://localhost:8080/admin
    or a router at http://192.168.1.1), which only the app's own machine can reach.
    Runs as an httpx hook before every request, so redirects to such hosts are blocked too.
    """
    host = request.url.host
    try:
        addresses = {info[4][0] for info in socket.getaddrinfo(host, None)}
    except socket.gaierror:
        return  # Unknown host: let httpx fail with its normal "could not connect" error.
    for address in addresses:
        if not ipaddress.ip_address(address).is_global:
            raise ValueError(f"URLs pointing to local or private networks are not allowed ({host}).")


def fetch_job_description(url: str) -> str:
    """Download the page at `url` and return its readable text (at most MAX_CHARS).

    Raises:
        ValueError: if the URL points to a local/private network, the page cannot be
            downloaded, or it contains too little text.
    """
    try:
        with httpx.Client(event_hooks={"request": [_block_private_hosts]}) as client:
            response = client.get(url.strip(), headers=_HEADERS, timeout=15, follow_redirects=True)
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
