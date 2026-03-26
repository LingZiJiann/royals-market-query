# Royals Market Query

A tool for scraping and querying the [Maple Royals](https://royals.ms) forum marketplace to get real-time price information on in-game items.

## Overview

Maple Royals is a private MapleStory server. Players buy and sell items in a dedicated forum marketplace. This project scrapes those selling threads and lets you ask a local LLM — running via Ollama — questions like:

> "How much is a Stonetooth Sword selling for?"

The LLM answers based on actual current listings, not hallucinated prices.

## How It Works

1. **Scrape** selling threads from the forum (titles, usernames, listing descriptions)
2. **Filter** listings by keyword match on the item name
3. **Prompt** a local Ollama model with the matching listings as context
4. **Get** a grounded price answer

No embeddings, no vector database — just keyword search and a local LLM.

## Current State

The scraper and query layer are fully functional:

**Phase 1 — Scraper**
- Scrapes paginated selling threads from `royals.ms/forum/forums/selling.17/`
- Multithreaded: 5 workers for pages, 10 workers for thread content
- Returns a pandas DataFrame with columns: `title`, `username`, `preview_url`, `description`
- Configurable via `config/config.py`

**Phase 2 — Listings Query**
- `ListingsQuery` class wraps the scraper with TTL-based CSV caching (default 30 min)
- Case-insensitive keyword filtering across `title` and `description` columns with acronym expansion (`config/item_aliases.py`)
- Interactive REPL via `query.py` — scrapes once on startup, holds listings in memory across queries

The Ollama price summary (Phase 3) is not yet built.

## Tech Stack

| Component | Library |
|-----------|---------|
| HTTP requests | `requests` |
| HTML parsing | `beautifulsoup4` |
| Data handling | `pandas` |
| Local LLM | `ollama` (planned) |
| Language | Python 3.10+ |

## Roadmap

### Phase 1 — Forum Scraper (Done)
Paginated, multithreaded scraper that collects marketplace listings into a DataFrame.

### Phase 2 — Filtered Listings Query (Done)
- `ListingsQuery` class with TTL-based CSV caching and keyword filtering
- Interactive REPL (`query.py`) — scrapes once, queries in a loop
- Cache persists across REPL sessions; re-running within TTL skips the scrape

### Phase 3 — Ollama Price Summary (Planned)
- Take filtered listings from Phase 2 as input
- Pass matching listings as context to a local Ollama LLM
- Return a price summary answer

## Open Decisions

- **Ollama integration:** Which local model to use; how to structure the price-summary prompt

## Usage

```bash
# Install dependencies
pip install -e .

# Run the scraper (scrapes pages, prints the DataFrame)
python scrape.py

# Run the interactive query REPL
python query.py
```

The REPL scrapes listings once on startup (or loads from cache), then lets you search by item name:

```
Item name (or "quit" to exit): Stonetooth Sword

Found 2 listing(s) for "Stonetooth Sword":
──────────────────────────────────────────────────
Title:       [SELLING] Stonetooth Sword 118 atk
Seller:      username123
Description: Selling stonetooth 118 atk, looking for 500m...
URL:         https://royals.ms/forum/threads/...
──────────────────────────────────────────────────
```

### Configuration

Edit `config/config.py` to change scraper behaviour:

| Setting | Default | Description |
|---------|---------|-------------|
| `BASE_FORUM_URL` | `https://royals.ms/forum/` | Base URL for the forum |
| `SELLING_FORUM_URL` | `https://royals.ms/forum/forums/selling.17/` | Forum section URL for `ListingsQuery` |
| `DEFAULT_MAX_PAGES` | `2` | Pages to scrape by default |
| `PAGE_FETCH_WORKERS` | `5` | Concurrent page fetch threads |
| `THREAD_FETCH_WORKERS` | `10` | Concurrent thread fetch threads |
| `CACHE_FILE_PATH` | `cache/listings.csv` | Path where scraped listings are cached |
| `CACHE_TTL_MINUTES` | `30` | Minutes before the cache is considered stale |

## Project Structure

```
royals_market_query/
├── config/
│   ├── config.py          # Scraper and query configuration
│   └── item_aliases.py    # Acronym → item name mappings for search expansion
├── src/
│   ├── scraper/
│   │   └── forum_scraping_multi_thread.py  # ForumScrapper class
│   └── query/
│       └── listings_query.py               # ListingsQuery class
├── cache/
│   └── listings.csv       # Cached listings (auto-created)
├── docs/
│   ├── forum_scraping_multi_thread.md      # Scraper API docs
│   └── listings_query.md                   # Query layer API docs
├── scrape.py              # Scraper entry point
├── query.py               # Interactive REPL entry point
└── pyproject.toml         # Dependencies
```
