from src.scrapers.apple_refurbished import AppleRefurbishedScraper
from src.scrapers.base import BaseScraper
from src.scrapers.refurbed import RefurbedScraper

ALL_SCRAPERS: list[type[BaseScraper]] = [
    AppleRefurbishedScraper,
    RefurbedScraper,
]

__all__ = [
    "ALL_SCRAPERS",
    "AppleRefurbishedScraper",
    "BaseScraper",
    "RefurbedScraper",
]
