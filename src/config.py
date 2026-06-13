from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass, field

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
DRY_RUN = os.getenv("DRY_RUN", "false").lower() == "true"

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

SUPPORTED_CHIPS = {
    # "M1",
    "M1 Pro",
    "M1 Max",
    "M1 Ultra",
    # "M2",
    "M2 Pro",
    "M2 Max",
    "M2 Ultra",
    # "M3",
    "M3 Pro",
    "M3 Max",
    "M4",
    "M4 Pro",
    "M4 Max",
}

REQUEST_TIMEOUT_SECONDS = 30
SCRAPER_DELAY_SECONDS = 2
TELEGRAM_SEND_DELAY_SECONDS = 30
MAX_MESSAGE_LENGTH = 4096

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
STATE_FILE = os.path.join(DATA_DIR, "seen_products.json")

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
)

USER_AGENT_POOL = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.2 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:133.0) Gecko/20100101 Firefox/133.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:133.0) Gecko/20100101 Firefox/133.0",
    "Mozilla/5.0 (X11; Linux x86_64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
)


@dataclass
class FilterConfig:
    min_ram_gb: int = 0
    min_storage_gb: int = 0
    max_price: float = 0.0
    categories: set[str] = field(default_factory=set)
    conditions: set[str] = field(default_factory=set)

    @classmethod
    def from_env(cls) -> FilterConfig:
        raw = os.getenv("FILTERS", "{}")
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            logging.warning("Invalid FILTERS env var, using defaults")
            data = {}

        return cls(
            min_ram_gb=data.get("min_ram_gb", 0),
            min_storage_gb=data.get("min_storage_gb", 0),
            max_price=data.get("max_price", 0.0),
            categories=set(data.get("categories", [])),
            conditions=set(data.get("conditions", [])),
        )


def setup_logging() -> None:
    logging.basicConfig(
        level=getattr(logging, LOG_LEVEL.upper(), logging.INFO),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
