from __future__ import annotations

import hashlib
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum


class Category(Enum):
    AIR = "air"
    PRO = "pro"


@dataclass(frozen=True)
class Product:
    site: str
    category: Category
    title: str
    chip: str
    ram_gb: int
    storage_gb: int
    price: float
    currency: str = "EUR"
    url: str = ""
    condition: str = "refurbished"
    scraped_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    @property
    def key(self) -> str:
        if self.url:
            raw = f"{self.site}_{self.url}"
        else:
            raw = f"{self.site}_{self.title}_{self.chip}_{self.ram_gb}_{self.storage_gb}"
        return hashlib.sha256(raw.encode()).hexdigest()[:16]

    def to_dict(self) -> dict:
        data = asdict(self)
        data["category"] = self.category.value
        return data

    @classmethod
    def from_dict(cls, data: dict) -> Product:
        data = data.copy()
        data["category"] = Category(data["category"])
        return cls(**data)

    @property
    def display_name(self) -> str:
        name = f"MacBook {self.category.value.title()}"
        specs = f"{self.chip} — {self.ram_gb}GB/{self.storage_gb}GB"
        return f"{name} {specs}"

    @property
    def price_display(self) -> str:
        return f"€{self.price:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


@dataclass
class PriceChange:
    product: Product
    old_price: float
    new_price: float

    @property
    def change_pct(self) -> float:
        if self.old_price == 0:
            return 0.0
        return ((self.new_price - self.old_price) / self.old_price) * 100

    @property
    def is_decrease(self) -> bool:
        return self.new_price < self.old_price

    @property
    def direction_emoji(self) -> str:
        return "📉" if self.is_decrease else "📈"

    @property
    def old_price_display(self) -> str:
        return f"€{self.old_price:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    @property
    def new_price_display(self) -> str:
        return f"€{self.new_price:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
