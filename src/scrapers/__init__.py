from src.scrapers.amazon import AmazonScraper
from src.scrapers.apple_refurbished import AppleRefurbishedScraper
from src.scrapers.backmarket import BackMarketScraper
from src.scrapers.base import BaseScraper
from src.scrapers.imac_store import IMacStoreScraper
from src.scrapers.refurbed import RefurbedScraper

ALL_SCRAPERS: list[type[BaseScraper]] = [
    AppleRefurbishedScraper,
    BackMarketScraper,
    AmazonScraper,
    IMacStoreScraper,
    RefurbedScraper,
]

__all__ = [
    "ALL_SCRAPERS",
    "AmazonScraper",
    "AppleRefurbishedScraper",
    "BackMarketScraper",
    "BaseScraper",
    "IMacStoreScraper",
    "RefurbedScraper",
]
