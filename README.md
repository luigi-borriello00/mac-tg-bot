# Mac Price Monitor Bot

Bot Telegram che monitora giornalmente i prezzi di MacBook Air e Pro (M1+) dai principali siti di ricondizionati e nuovi.

## Siti Monitorati

| Sito | Tipo | Stato |
|------|------|-------|
| Apple Refurbished Store | Ricondizionato | ✅ Stabile |
| refurbed.it | Ricondizionato | ✅ Stabile |
| Back Market | Ricondizionato | ⚠️ Dipende da anti-bot |
| Amazon.it | Nuovo | ⚠️ Dipende da anti-bot |
| iMac-Store | Ricondizionato | ⚠️ Dipende da disponibilità |

## Setup

### 1. Crea il bot Telegram

1. Apri [@BotFather](https://t.me/BotFather) su Telegram
2. `/newbot` → scegli un nome
3. Salva il **bot token** (es. `123456:ABC-DEF...`)
4. Avvia il bot e ottieni il **chat_id**:
   ```bash
   curl "https://api.telegram.org/bot<TOKEN>/getUpdates"
   ```

### 2. Configura GitHub Secrets

Vai su **Settings → Secrets and variables → Actions** nel tuo repo:

- `TELEGRAM_BOT_TOKEN`: il token del bot
- `TELEGRAM_CHAT_ID`: il tuo chat ID

### 3. Push su main

La pipeline GitHub Actions girerà automaticamente ogni 6 ore e ad ogni push su `main`.

## Sviluppo Locale

```bash
pip install -r requirements.txt
DRY_RUN=true python -m src.main
```

## Filtri

Configura i filtri tramite la variabile d'ambiente `FILTERS` (JSON):

```json
{
  "min_ram_gb": 16,
  "min_storage_gb": 512,
  "max_price": 2000,
  "categories": ["air", "pro"],
  "conditions": ["refurbished"]
}
```

Filtri disponibili:
- `min_ram_gb`: RAM minima (GB)
- `min_storage_gb`: Storage minimo (GB)
- `max_price`: Prezzo massimo (€)
- `categories`: Lista di `air` e/o `pro`
- `conditions`: Lista di `refurbished` e/o `new`

## Struttura

```
src/
├── models/product.py          # Modelli dati (Product, Category, PriceChange)
├── scrapers/                  # Scraper per ogni sito
│   ├── base.py                # Classe base astratta
│   ├── apple_refurbished.py   # Apple Refurbished Store
│   ├── backmarket.py          # Back Market
│   ├── amazon.py              # Amazon.it
│   ├── imac_store.py          # iMac-Store.it
│   └── refurbed.py            # refurbed.it
├── filters/filters.py         # Engine filtri componibili
├── notifications/telegram.py  # Notifiche Telegram
├── storage/json_storage.py    # Persistenza stato
├── config.py                  # Configurazione
└── main.py                    # Entry point
```

## Aggiungere un nuovo sito

1. Crea `src/scrapers/nuovo_sito.py` estendendo `BaseScraper`
2. Implementa `site_name`, `base_url` e `_parse_products`
3. Aggiungi la classe a `ALL_SCRAPERS` in `src/scrapers/__init__.py`
