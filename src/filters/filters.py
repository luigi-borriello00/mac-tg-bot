from __future__ import annotations

import logging
from collections.abc import Callable

from src.config import FilterConfig
from src.models.product import Category, Product

logger = logging.getLogger(__name__)

FilterFn = Callable[[Product], bool]


def _filter_by_min_ram(min_gb: int) -> FilterFn:
    def _check(p: Product) -> bool:
        return p.ram_gb == 0 or p.ram_gb >= min_gb
    return _check


def _filter_by_min_storage(min_gb: int) -> FilterFn:
    def _check(p: Product) -> bool:
        return p.storage_gb == 0 or p.storage_gb >= min_gb
    return _check


def _filter_by_max_price(max_price: float) -> FilterFn:
    def _check(p: Product) -> bool:
        return p.price <= max_price
    return _check


def _filter_by_categories(categories: set[str]) -> FilterFn:
    allowed = {Category(c) for c in categories}

    def _check(p: Product) -> bool:
        return p.category in allowed
    return _check


def _filter_by_conditions(conditions: set[str]) -> FilterFn:
    def _check(p: Product) -> bool:
        return p.condition in conditions
    return _check


class FilterEngine:
    def __init__(self, config: FilterConfig) -> None:
        self._filters: list[FilterFn] = self._build_filters(config)

    def apply(self, products: list[Product]) -> list[Product]:
        if not self._filters:
            return products
        filtered = [p for p in products if all(f(p) for f in self._filters)]
        logger.info(
            "Filters applied: %d -> %d products",
            len(products),
            len(filtered),
        )
        return filtered

    @staticmethod
    def _build_filters(config: FilterConfig) -> list[FilterFn]:
        filters: list[FilterFn] = []

        if config.min_ram_gb > 0:
            filters.append(_filter_by_min_ram(config.min_ram_gb))
        if config.min_storage_gb > 0:
            filters.append(_filter_by_min_storage(config.min_storage_gb))
        if config.max_price > 0:
            filters.append(_filter_by_max_price(config.max_price))
        if config.categories:
            filters.append(_filter_by_categories(config.categories))
        if config.conditions:
            filters.append(_filter_by_conditions(config.conditions))

        return filters
