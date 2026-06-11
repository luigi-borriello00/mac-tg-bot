from __future__ import annotations

import logging
import time

import requests

from src.config import DRY_RUN, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, TELEGRAM_SEND_DELAY_SECONDS
from src.models.product import PriceChange, Product

logger = logging.getLogger(__name__)

_API_BASE = "https://api.telegram.org/bot{token}"


class TelegramNotifier:
    def __init__(self) -> None:
        self._token = TELEGRAM_BOT_TOKEN
        self._chat_id = TELEGRAM_CHAT_ID

    @property
    def is_configured(self) -> bool:
        return bool(self._token and self._chat_id)

    def send_new_products(self, products: list[Product]) -> int:
        if not products:
            return 0

        groups = self._group_by_site(products)
        sent = 0

        for site, items in groups.items():
            message = self._format_new_products(site, items)
            if self._send_message(message):
                sent += 1
            if len(groups) > 1:
                time.sleep(TELEGRAM_SEND_DELAY_SECONDS)

        return sent

    def send_price_changes(self, changes: list[PriceChange]) -> int:
        if not changes:
            return 0

        groups: dict[str, list[PriceChange]] = {}
        for c in changes:
            groups.setdefault(c.product.site, []).append(c)

        sent = 0
        for site, items in groups.items():
            message = self._format_price_changes(site, items)
            if self._send_message(message):
                sent += 1
            if len(groups) > 1:
                time.sleep(TELEGRAM_SEND_DELAY_SECONDS)

        return sent

    def _send_message(self, text: str) -> bool:
        if DRY_RUN:
            logger.info("[DRY RUN] Telegram message:\n%s", text)
            return True

        if not self.is_configured:
            logger.warning("Telegram not configured, skipping notification")
            return False

        url = _API_BASE.format(token=self._token) + "/sendMessage"
        payload = {
            "chat_id": self._chat_id,
            "text": text,
            "parse_mode": "HTML",
            "disable_web_page_preview": True,
        }

        try:
            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()
            logger.info("Telegram message sent successfully")
            return True
        except requests.RequestException:
            logger.exception("Failed to send Telegram message")
            return False

    @staticmethod
    def _group_by_site(products: list[Product]) -> dict[str, list[Product]]:
        groups: dict[str, list[Product]] = {}
        for p in products:
            groups.setdefault(p.site, []).append(p)
        return groups

    @staticmethod
    def _format_new_products(site: str, products: list[Product]) -> str:
        header = f"🆕 <b>Nuovi prodotti su {site.upper()}</b>\n\n"
        lines: list[str] = []
        for p in products:
            lines.append(
                f"💻 <b>{p.display_name}</b>\n"
                f"   💰 {p.price_display} ({p.condition})\n"
                f"   🔗 <a href=\"{p.url}\">Vedi offerta</a>"
            )
        return header + "\n\n".join(lines)

    @staticmethod
    def _format_price_changes(site: str, changes: list[PriceChange]) -> str:
        header = f"💰 <b>Variazioni prezzo su {site.upper()}</b>\n\n"
        lines: list[str] = []
        for c in changes:
            pct = c.change_pct
            url = c.product.url
            lines.append(
                f"{c.direction_emoji} <b>{c.product.display_name}</b>\n"
                f"   {c.old_price_display} → {c.new_price_display} ({pct:+.1f}%)\n"
                f'   🔗 <a href="{url}">Vedi offerta</a>'
            )
        return header + "\n\n".join(lines)
