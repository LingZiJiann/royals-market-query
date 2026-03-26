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
4. **Get** a grounded price summary, rendered in the browser

No embeddings, no vector database — just keyword search and a local LLM.

## Current State

All three phases are complete and integrated:

**Phase 1 — Scraper**
- Scrapes paginated selling threads from `royals.ms/forum/forums/selling.17/`
- Multithreaded: 5 workers for pages, 10 workers for thread content
- Returns a pandas DataFrame with columns: `title`, `username`, `preview_url`, `date`, `description`
- Configurable via `config/config.py`

**Phase 2 — Listings Query**
- `ListingsQuery` class wraps the scraper with TTL-based CSV caching (default 30 min)
- Case-insensitive keyword filtering on `title` column with acronym expansion (`config/item_aliases.py`)

**Phase 3 — Ollama Price Summary**
- `PriceSummarizer` class sends filtered listings as context to a local Ollama LLM
- Extracts S/B and A/W asking prices per listing; normalizes to millions
- `query.py` integrates all three phases: scrapes once, queries in a loop, generates a price summary after each search, and opens it as a rendered HTML page in the browser

## Tech Stack

| Component | Library |
|-----------|---------|
| HTTP requests | `requests` |
| HTML parsing | `beautifulsoup4` |
| Data handling | `pandas` |
| Local LLM | `ollama` |
| Markdown rendering | `markdown` |
| Language | Python 3.10+ |

## Roadmap

### Phase 1 — Forum Scraper (Done)
Paginated, multithreaded scraper that collects marketplace listings into a DataFrame.

### Phase 2 — Filtered Listings Query (Done)
- `ListingsQuery` class with TTL-based CSV caching and keyword filtering
- Interactive REPL (`query.py`) — scrapes once, queries in a loop
- Cache persists across REPL sessions; re-running within TTL skips the scrape

### Phase 3 — Ollama Price Summary (Done)
- `PriceSummarizer` takes filtered listings from Phase 2 as context
- Sends them to a local Ollama LLM with a structured price-analysis system prompt
- Extracts S/B (Starting Bid) and A/W (Auto Win) asking prices; normalizes all values to millions
- `query.py` calls the summarizer after each search and opens the result as a rendered HTML page in the browser

## Usage

```bash
# Install dependencies
pip install -e .

# Run the scraper (scrapes pages, prints the DataFrame)
python scrape.py

# Run the interactive query REPL
python query.py
```

The REPL scrapes listings once on startup (or loads from cache), then lets you search by item name. After printing matching listings, it generates a price summary via Ollama and opens it as a rendered HTML page in the browser:

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
| `OLLAMA_MODEL` | — | Ollama model name used for price summarization |
| `OLLAMA_TIMEOUT` | — | Ollama request timeout in seconds |

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
│   ├── forum_scraping_multi_thread.md      # Scraper API docs
│   ├── listings_query.md                   # Query layer API docs
│   └── price_summarizer.md                 # Summarizer API docs
├── scrape.py              # Scraper entry point
├── query.py               # Interactive REPL entry point
└── pyproject.toml         # Dependencies
```
