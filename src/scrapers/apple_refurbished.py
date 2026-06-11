from __future__ import annotations

import json
import logging
import re

from bs4 import BeautifulSoup

from src.models.product import Category, Product
from src.scrapers.base import BaseScraper

logger = logging.getLogger(__name__)

_AIR_URLS = [
    "https://www.apple.com/it/shop/refurbished/mac/macbook-air",
    "https://www.apple.com/it/shop/refurbished/mac/macbook-air?page=2",
]
_PRO_URLS = [
    "https://www.apple.com/it/shop/refurbished/mac/macbook-pro",
    "https://www.apple.com/it/shop/refurbished/mac/macbook-pro?page=2",
]


class AppleRefurbishedScraper(BaseScraper):
    def __init__(self) -> None:
        self._detail_cache: dict[str, tuple[int, int]] = {}

    @property
    def site_name(self) -> str:
        return "apple_refurbished"

    @property
    def base_url(self) -> str:
        return "https://www.apple.com/it/shop/refurbished/mac/macbook-air"

    def scrape(self) -> list[Product]:
        logger.info("Scraping %s...", self.site_name)
        seen_keys: set[str] = set()
        products: list[Product] = []
        for url in _AIR_URLS + _PRO_URLS:
            try:
                html = self._fetch_page(url)
                for product in self._parse_products(html):
                    if product.key not in seen_keys:
                        seen_keys.add(product.key)
                        products.append(product)
            except Exception:
                logger.exception("Error scraping %s page %s", self.site_name, url)
        logger.info("Found %d products on %s", len(products), self.site_name)
        return products

    def _parse_products(self, html: str) -> list[Product]:
        bootstrap = self._extract_bootstrap_json(html)
        if bootstrap is None:
            return self._parse_no_js_fallback(html)

        products: list[Product] = []
        tiles = bootstrap.get("tiles", [])

        for tile in tiles:
            title = tile.get("title", "")
            if not self._is_macbook(title):
                continue

            category = self._detect_category(title)
            chip = self._extract_chip(title)
            if not chip:
                continue

            price_raw = tile.get("price", {}).get("currentPrice", {}).get("raw_amount", "")
            try:
                price = float(str(price_raw).replace(",", "."))
            except (ValueError, TypeError):
                price = 0.0
            if price <= 0:
                continue

            url_path = tile.get("productDetailsUrl", "")
            url = f"https://www.apple.com{url_path}" if url_path else ""

            ram_gb, storage_gb = self._fetch_specs_from_detail_page(url)

            products.append(Product(
                site=self.site_name,
                category=category,
                title=title,
                chip=chip,
                ram_gb=ram_gb,
                storage_gb=storage_gb,
                price=price,
                url=url,
                condition="refurbished",
            ))

        return products

    def _fetch_specs_from_detail_page(self, url: str) -> tuple[int, int]:
        if not url:
            return 0, 0
        normalized = url.split("?")[0]
        if normalized in self._detail_cache:
            return self._detail_cache[normalized]
        try:
            html = self._fetch_page(url)
            result = self._parse_specs_from_html(html)
            self._detail_cache[normalized] = result
            return result
        except Exception:
            logger.debug("Could not fetch detail page: %s", url)
            return 0, 0

    @staticmethod
    def _parse_specs_from_html(html: str) -> tuple[int, int]:
        ram_patterns = [
            r"(\d+)\s*GB\s*di\s*memoria",
            r"Memoria\s*unificata\s*da\s*(\d+)\s*GB",
            r"(\d+)\s*GB\s*di\s*Memoria\s*unificata",
        ]
        storage_patterns = [
            r"SSD\s*da\s*(\d+)\s*(TB|GB)",
            r"(\d+)\s*(TB|GB)\s*SSD",
            r"Unità\s*SSD\s*da\s*(\d+)\s*(TB|GB)",
        ]

        ram_gb = 0
        for pattern in ram_patterns:
            match = re.search(pattern, html, re.IGNORECASE)
            if match:
                ram_gb = int(match.group(1))
                break

        storage_gb = 0
        for pattern in storage_patterns:
            match = re.search(pattern, html, re.IGNORECASE)
            if match:
                value = int(match.group(1))
                unit = match.group(2).upper()
                storage_gb = value * 1024 if unit == "TB" else value
                break

        return ram_gb, storage_gb

    def _parse_no_js_fallback(self, html: str) -> list[Product]:
        soup = BeautifulSoup(html, "lxml")
        products: list[Product] = []

        for item in soup.select("li"):
            link_tag = item.select_one("h3 a")
            price_tag = item.select_one(".as-price-currentprice, .as-producttile-currentprice")
            if not link_tag or not price_tag:
                continue

            title = link_tag.get_text(strip=True)
            if not self._is_macbook(title):
                continue

            category = self._detect_category(title)
            chip = self._extract_chip(title)
            if not chip:
                continue

            price_text = price_tag.get_text(strip=True)
            price = self._parse_price(price_text)
            if price <= 0:
                continue

            url_path = link_tag.get("href", "")
            url = f"https://www.apple.com{url_path}" if url_path else ""

            ram_gb, storage_gb = self._fetch_specs_from_detail_page(url)

            products.append(Product(
                site=self.site_name,
                category=category,
                title=title,
                chip=chip,
                ram_gb=ram_gb,
                storage_gb=storage_gb,
                price=price,
                url=url,
                condition="refurbished",
            ))

        return products

    @staticmethod
    def _extract_bootstrap_json(html: str) -> dict | None:
        match = re.search(r"window\.REFURB_GRID_BOOTSTRAP\s*=\s*({.*?});", html, re.DOTALL)
        if not match:
            return None
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            logger.warning("Failed to parse REFURB_GRID_BOOTSTRAP JSON")
            return None

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
