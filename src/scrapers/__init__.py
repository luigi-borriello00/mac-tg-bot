from src.scrapers.amazon import AmazonScraper
from src.scrapers.apple_refurbished import AppleRefurbishedScraper
from src.scrapers.backmarket import BackMarketScraper
from src.scrapers.base import BaseScraper
from src.scrapers.imac_store import IMacStoreScraper
from src.scrapers.swappie import SwappieScraper

ALL_SCRAPERS: list[type[BaseScraper]] = [
    AppleRefurbishedScraper,
    BackMarketScraper,
    AmazonScraper,
    IMacStoreScraper,
    SwappieScraper,
]

__all__ = [
    "ALL_SCRAPERS",
    "AmazonScraper",
    "AppleRefurbishedScraper",
    "BackMarketScraper",
    "BaseScraper",
    "IMacStoreScraper",
    "SwappieScraper",
]
