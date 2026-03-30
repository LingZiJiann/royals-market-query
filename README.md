# Royals Market Query

A tool for scraping and querying the [Maple Royals](https://royals.ms) forum marketplace to get real-time price information on in-game items.

## Overview

Maple Royals is a private MapleStory server where players buy and sell items in a dedicated forum marketplace. This project scrapes those selling threads, filters them by item name, and uses a local LLM — running via [Ollama](https://ollama.com) — to summarize the retrieved listings into a readable price breakdown.

## How It Works

1. **Scrape** — collect selling thread titles, usernames, and descriptions from the forum
2. **Filter** — narrow listings down by keyword match (with acronym expansion)
3. **Summarize** — send matching listings as context to a local Ollama model
4. **Display** — open a rendered HTML price summary in the browser

## Requirements

- Python 3.10+
- [Ollama](https://ollama.com) running locally with a model pulled (e.g. `ollama pull llama3`)

## Installation

Using [uv](https://docs.astral.sh/uv/) (recommended):

```bash
uv sync
```

This creates a `.venv` and installs all dependencies. To run scripts within the environment:

```bash
uv run python query.py
uv run python scrape.py
```

Alternatively, with pip:

```bash
pip install -e .
```

## Usage

### Interactive Query REPL

```bash
python query.py
```

Scrapes listings once on startup (or loads from cache), then prompts for item names in a loop. After each search, generates a price summary via Ollama and opens it as a rendered HTML page in the browser.

```
Item name (or "quit" to exit): Stonetooth Sword

Found 2 listing(s) for "Stonetooth Sword":
──────────────────────────────────────────────────
Title:       [SELLING] Stonetooth Sword 118 atk
Seller:      username123
Date:        2026-03-25
Description: Selling stonetooth 118 atk, looking for 500m...
URL:         https://royals.ms/forum/threads/...
──────────────────────────────────────────────────

Generating price summary...
Summarizer took 4.2s
Summary opened in browser.
```

The cache persists between sessions — re-running within the TTL window skips the scrape entirely.

### Scraper Only

```bash
python scrape.py
```

Runs the scraper and prints the raw listings DataFrame.

### Item Acronyms

Common item acronyms are supported out of the box:

| Acronym | Searches for |
|---------|-------------|
| `st` | stonetooth |
| `dsc` | dragon slash claw |
| `kc` | king cent |
| `dsb` | dragon shiner bow |
| `rc` | red craven |
| `dps` | dragon purple sleeve |
| `bfc` | blackfist cape, black fist cape |
| `vl` | von leon boots, von leon boot |
| `bwg` | brown work gloves, brown work glove |
| `fs` | facestomper, face stomper, facestompers, face stompers |

Add new entries to [config/item_aliases.py](config/item_aliases.py) to extend coverage.

## Configuration

Edit [config/config.py](config/config.py) to change scraper and summarizer behaviour:

| Setting | Default | Description |
|---------|---------|-------------|
| `BASE_FORUM_URL` | `https://royals.ms/forum/` | Base URL for the forum |
| `SELLING_FORUM_URL` | `https://royals.ms/forum/forums/selling.17/` | Forum section URL |
| `DEFAULT_MAX_PAGES` | `2` | Pages to scrape by default |
| `PAGE_FETCH_WORKERS` | `5` | Concurrent page fetch threads |
| `THREAD_FETCH_WORKERS` | `10` | Concurrent thread fetch threads |
| `CACHE_FILE_PATH` | `cache/listings.csv` | Path where scraped listings are cached |
| `CACHE_TTL_MINUTES` | `30` | Minutes before the cache is considered stale |
| `OLLAMA_MODEL` | — | Ollama model name used for price summarization |
| `OLLAMA_TIMEOUT` | — | Ollama request timeout in seconds |

## Price Notation

The LLM understands standard Maple Royals marketplace conventions:

| Notation | Meaning |
|----------|---------|
| `m` / `M` | Million mesos (e.g. `500m` = 500,000,000) |
| `b` / `B` | Billion mesos (e.g. `1b` = 1,000,000,000) |
| `S/B` | Starting Bid — minimum asking price |
| `A/W` | Auto Win — maximum asking price |
| `C/O` | Current Offer — ignored (not an asking price) |

All prices are normalized to millions. Prices shown are **asking prices posted by sellers**, not confirmed sale prices.

## Project Structure

```
royals_market_query/
├── config/
│   ├── config.py          # Scraper and query configuration
│   └── item_aliases.py    # Acronym → item name mappings for search expansion
├── src/
│   ├── scraper/
│   │   └── forum_scraping_multi_thread.py  # ForumScrapper class
│   ├── query/
│   │   └── listings_query.py               # ListingsQuery class
│   └── summarizer/
│       └── price_summarizer.py             # PriceSummarizer class
├── cache/
│   └── listings.csv       # Cached listings (auto-created)
├── docs/
│   ├── forum_scraping_multi_thread.md      # Scraper docs
│   ├── listings_query.md                   # Query layer docs
│   └── price_summarizer.md                 # Summarizer docs
├── scrape.py              # Scraper entry point
├── query.py               # Interactive REPL entry point
└── pyproject.toml         # Dependencies
```

## Tech Stack

| Component | Library |
|-----------|---------|
| HTTP requests | `requests` |
| HTML parsing | `beautifulsoup4` |
| Data handling | `pandas` |
| Local LLM | `ollama` |
| Markdown rendering | `markdown` |
| Language | Python 3.10+ |

## Documentation

- [ForumScrapper](docs/forum_scraping_multi_thread.md) — multithreaded forum scraper
- [ListingsQuery](docs/listings_query.md) — caching and keyword filtering layer
- [PriceSummarizer](docs/price_summarizer.md) — Ollama-powered price summarizer
