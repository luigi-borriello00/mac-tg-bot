from __future__ import annotations

import codecs
import json
import logging
import re

from bs4 import BeautifulSoup

from src.models.product import Category, Product
from src.scrapers.base import BaseScraper

logger = logging.getLogger(__name__)

_URLS = [
    "https://www.refurbed.it/c/macbook/",
    "https://www.refurbed.it/c/macbook/?page=2&sort=popular",
]


class RefurbedScraper(BaseScraper):
    @property
    def site_name(self) -> str:
        return "refurbed"

    @property
    def base_url(self) -> str:
        return _URLS[0]

    def scrape(self) -> list[Product]:
        logger.info("Scraping %s...", self.site_name)
        products: list[Product] = []
        seen_keys: set[str] = set()
        for url in _URLS:
            try:
                html = self._fetch_page(url)
                for product in self._parse_products(html):
                    if product.key not in seen_keys:
                        seen_keys.add(product.key)
                        products.append(product)
            except Exception:
                logger.warning("Could not scrape %s", url)
        logger.info("Found %d products on %s", len(products), self.site_name)
        return products

    def _parse_products(self, html: str) -> list[Product]:
        gadata_items = self._extract_gadata(html)
        urls = self._extract_product_urls(html)
        products: list[Product] = []

        for idx, item in enumerate(gadata_items):
            name = item.get("item_name", "")
            if not self._is_macbook(name):
                continue

            category = self._detect_category(name)
            chip = self._extract_chip(name)
            if not chip:
                continue

            try:
                price = float(item.get("price", "0"))
            except (ValueError, TypeError):
                price = 0.0
            if price <= 0:
                continue

            variant = item.get("item_variant", "")
            ram_gb, storage_gb = self._parse_specs(variant)
            url = urls[idx] if idx < len(urls) else ""

            products.append(Product(
                site=self.site_name,
                category=category,
                title=name,
                chip=chip,
                ram_gb=ram_gb,
                storage_gb=storage_gb,
                price=price,
                url=url,
                condition="refurbished",
            ))

        return products

    @staticmethod
    def _extract_gadata(html: str) -> list[dict]:
        match = re.search(
            r"GAData\s*=\s*JSON\.parse\(\"(.+?)\"\)\s*;", html, re.DOTALL
        )
        if not match:
            return []
        try:
            decoded = codecs.decode(match.group(1), "unicode_escape")
            data = json.loads(decoded)
            return data.get("ecommerce", {}).get("items", [])
        except (json.JSONDecodeError, UnicodeDecodeError):
            logger.warning("Failed to parse GAData JSON from refurbed")
            return []

    @staticmethod
    def _extract_product_urls(html: str) -> list[str]:
        soup = BeautifulSoup(html, "lxml")
        urls: list[str] = []
        for article in soup.select("article[data-test='product-tile']"):
            link = article.select_one("a[href]")
            if not link:
                urls.append("")
                continue
            href = link.get("href", "")
            url = f"https://www.refurbed.it{href}" if href.startswith("/") else href
            urls.append(url)
        return urls

    @staticmethod
    def _parse_specs(variant: str) -> tuple[int, int]:
        ram_match = re.search(r"(\d+)\s*GB(?!\s*SSD)", variant)
        ram_gb = int(ram_match.group(1)) if ram_match else 0

        storage_match = re.search(r"(\d+)\s*(TB|GB)\s*SSD", variant)
        if storage_match:
            value = int(storage_match.group(1))
            unit = storage_match.group(2).upper()
            storage_gb = value * 1024 if unit == "TB" else value
        else:
            storage_gb = 0

        return ram_gb, storage_gb

    @staticmethod
    def _is_macbook(name: str) -> bool:
        return "macbook" in name.lower()

    @staticmethod
    def _detect_category(name: str) -> Category:
        lower = name.lower()
        if "air" in lower:
            return Category.AIR
        return Category.PRO

    @staticmethod
    def _extract_chip(name: str) -> str:
        pattern = r"(M[1-4](?:\s+(?:Pro|Max|Ultra))?)"
        match = re.search(pattern, name, re.IGNORECASE)
        return match.group(1).strip() if match else ""
