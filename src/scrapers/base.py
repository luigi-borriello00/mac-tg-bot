from __future__ import annotations

import logging
import time
from abc import ABC, abstractmethod

import httpx

from src.config import REQUEST_TIMEOUT_SECONDS, SCRAPER_DELAY_SECONDS, USER_AGENT
from src.models.product import Product

logger = logging.getLogger(__name__)

_HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "it-IT,it;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
}


class BaseScraper(ABC):
    @property
    @abstractmethod
    def site_name(self) -> str: ...

    @property
    @abstractmethod
    def base_url(self) -> str: ...

    @abstractmethod
    def _parse_products(self, html: str) -> list[Product]: ...

    def scrape(self) -> list[Product]:
        logger.info("Scraping %s...", self.site_name)
        try:
            html = self._fetch_page(self.base_url)
            products = self._parse_products(html)
            logger.info("Found %d products on %s", len(products), self.site_name)
            return products
        except Exception:
            logger.exception("Error scraping %s", self.site_name)
            return []

    def _fetch_page(self, url: str) -> str:
        time.sleep(SCRAPER_DELAY_SECONDS)
        with httpx.Client(timeout=REQUEST_TIMEOUT_SECONDS, follow_redirects=True) as client:
            response = client.get(url, headers=_HEADERS)
            response.raise_for_status()
            return response.text

    def _fetch_json(self, url: str) -> dict:
        time.sleep(SCRAPER_DELAY_SECONDS)
        headers = {**_HEADERS, "Accept": "application/json"}
        with httpx.Client(timeout=REQUEST_TIMEOUT_SECONDS, follow_redirects=True) as client:
            response = client.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
