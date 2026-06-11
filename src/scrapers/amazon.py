from __future__ import annotations

import logging
import re

from bs4 import BeautifulSoup

from src.models.product import Category, Product
from src.scrapers.base import BaseScraper

logger = logging.getLogger(__name__)

_URLS = [
    "https://www.amazon.it/s?k=macbook+air+M1+M2+M3+M4&rh=n%3A425916031",
    "https://www.amazon.it/s?k=macbook+pro+M1+M2+M3+M4&rh=n%3A425916031",
]


class AmazonScraper(BaseScraper):
    @property
    def site_name(self) -> str:
        return "amazon"

    @property
    def base_url(self) -> str:
        return _URLS[0]

    def scrape(self) -> list[Product]:
        logger.info("Scraping %s...", self.site_name)
        products: list[Product] = []
        for url in _URLS:
            try:
                html = self._fetch_page(url)
                products.extend(self._parse_products(html))
            except Exception:
                logger.warning(
                    "Could not scrape Amazon (anti-bot protection expected)"
                )
                break
        logger.info("Found %d products on %s", len(products), self.site_name)
        return products

    def _parse_products(self, html: str) -> list[Product]:
        soup = BeautifulSoup(html, "lxml")
        products: list[Product] = []

        for item in soup.select('[data-component-type="s-search-result"]'):
            title_tag = item.select_one("h2 a span, h2 span")
            price_tag = item.select_one(
                ".a-price .a-offscreen, .a-price-whole"
            )
            link_tag = item.select_one("h2 a")

            if not title_tag or not price_tag:
                continue

            title = title_tag.get_text(strip=True)
            if not self._is_macbook(title):
                continue

            category = self._detect_category(title)
            chip = self._extract_chip(title)
            if not chip:
                continue

            price = self._parse_price(price_tag.get_text(strip=True))
            if price <= 0:
                continue

            url = ""
            if link_tag:
                href = link_tag.get("href", "")
                url = f"https://www.amazon.it{href}" if href.startswith("/") else href

            products.append(Product(
                site=self.site_name,
                category=category,
                title=title,
                chip=chip,
                ram_gb=0,
                storage_gb=0,
                price=price,
                url=url,
                condition="new",
            ))

        return products

    @staticmethod
    def _is_macbook(title: str) -> bool:
        lower = title.lower()
        return "macbook" in lower

    @staticmethod
    def _detect_category(title: str) -> Category:
        lower = title.lower()
        if "air" in lower:
            return Category.AIR
        return Category.PRO

    @staticmethod
    def _extract_chip(title: str) -> str:
        pattern = r"(M[1-4](?:\s+(?:Pro|Max|Ultra))?)"
        match = re.search(pattern, title, re.IGNORECASE)
        return match.group(1).strip() if match else ""

    @staticmethod
    def _parse_price(text: str) -> float:
        cleaned = re.sub(r"[^\d,]", "", text).replace(",", ".")
        try:
            return float(cleaned)
        except ValueError:
            return 0.0
