from __future__ import annotations

import logging
import sys

from src.config import FilterConfig, setup_logging
from src.filters.filters import FilterEngine
from src.models.product import Product
from src.notifications.telegram import TelegramNotifier
from src.scrapers import ALL_SCRAPERS
from src.storage.json_storage import JsonStorage

logger = logging.getLogger(__name__)


def run() -> int:
    setup_logging()
    logger.info("=== Mac Price Monitor started ===")

    storage = JsonStorage()
    previous_state = storage.load()
    logger.info("Loaded %d previous products", len(previous_state))

    filter_config = FilterConfig.from_env()
    filter_engine = FilterEngine(filter_config)

    all_products: list[Product] = []
    scrapers = [cls() for cls in ALL_SCRAPERS]

    for scraper in scrapers:
        try:
            products = scraper.scrape()
            all_products.extend(products)
        except Exception:
            logger.exception("Scraper %s failed", scraper.site_name)

    if not all_products:
        logger.warning("No products found from any source")
        storage.save([])
        return 0

    logger.info("Total products scraped: %d", len(all_products))

    filtered = filter_engine.apply(all_products)
    logger.info("Products after filtering: %d", len(filtered))

    new_products, price_changes = storage.detect_changes(filtered, previous_state)
    logger.info(
        "Changes detected: %d new, %d price changes",
        len(new_products),
        len(price_changes),
    )

    notifier = TelegramNotifier()

    if new_products:
        notifier.send_new_products(new_products)
    if price_changes:
        notifier.send_price_changes(price_changes)

    if not new_products and not price_changes:
        logger.info("No changes detected")

    storage.save(filtered)
    logger.info("=== Mac Price Monitor finished ===")
    return 0


def main() -> None:
    sys.exit(run())


if __name__ == "__main__":
    main()
