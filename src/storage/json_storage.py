from __future__ import annotations

import json
import logging
import os
from datetime import datetime, timezone

from src.config import STATE_FILE
from src.models.product import PriceChange, Product

logger = logging.getLogger(__name__)


class JsonStorage:
    def __init__(self, path: str = STATE_FILE) -> None:
        self._path = path

    def load(self) -> dict[str, dict]:
        if not os.path.exists(self._path):
            return {}
        try:
            with open(self._path, encoding="utf-8") as f:
                data = json.load(f)
            if not isinstance(data, dict):
                return {}
            return data
        except (json.JSONDecodeError, OSError):
            logger.warning("Failed to load state from %s", self._path)
            return {}

    def save(self, products: list[Product]) -> None:
        state: dict[str, dict] = {}
        now = datetime.now(timezone.utc).isoformat()

        for p in products:
            state[p.key] = {
                "product": p.to_dict(),
                "last_seen": now,
            }

        os.makedirs(os.path.dirname(self._path), exist_ok=True)
        with open(self._path, "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
        logger.info("Saved %d products to %s", len(state), self._path)

    def detect_changes(
        self, current: list[Product], previous: dict[str, dict]
    ) -> tuple[list[Product], list[PriceChange]]:
        new_products: list[Product] = []
        price_changes: list[PriceChange] = []

        prev_map: dict[str, dict] = {}
        for key, entry in previous.items():
            prev_map[key] = entry

        for product in current:
            entry = prev_map.get(product.key)
            if entry is None:
                new_products.append(product)
                continue

            old_price = entry.get("product", {}).get("price", 0)
            if old_price and product.price != old_price:
                price_changes.append(PriceChange(
                    product=product,
                    old_price=float(old_price),
                    new_price=product.price,
                ))

        return new_products, price_changes
