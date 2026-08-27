from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup


@dataclass
class WebDocument:
    url: str
    title: str
    text: str
    error: str = ""


class WebResearcher:
    """Downloads user-supplied public pages and converts them to bounded text."""

    def __init__(self, timeout: int = 12, max_chars: int = 18_000):
        self.timeout = timeout
        self.max_chars = max_chars

    def fetch(self, url: str) -> WebDocument:
        safe_url = self._validate_url(url)
        try:
            response = requests.get(
                safe_url,
                timeout=self.timeout,
                headers={"User-Agent": "CAP931-SalesResearchPrototype/1.0"},
            )
            response.raise_for_status()
            content_type = response.headers.get("content-type", "")
            if "text/html" not in content_type:
                return WebDocument(safe_url, safe_url, "", "Unsupported content type")
            soup = BeautifulSoup(response.text, "html.parser")
            for element in soup(["script", "style", "nav", "footer", "form", "svg"]):
                element.decompose()
            title = soup.title.get_text(" ", strip=True) if soup.title else safe_url
            text = " ".join(soup.get_text(" ", strip=True).split())[: self.max_chars]
            return WebDocument(safe_url, title, text)
        except requests.RequestException as exc:
            return WebDocument(safe_url, safe_url, "", str(exc))

    @staticmethod
    def _validate_url(url: str) -> str:
        parsed = urlparse(str(url))
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise ValueError("Only complete public HTTP(S) URLs are supported.")
        host = (parsed.hostname or "").lower()
        if host in {"localhost", "127.0.0.1", "0.0.0.0"} or host.endswith(".local"):
            raise ValueError("Local or private URLs are not supported.")
        return str(url)

