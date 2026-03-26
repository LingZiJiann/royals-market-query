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

The scraper is fully functional:
- Scrapes paginated selling threads from `royals.ms/forum/forums/selling.17/`
- Multithreaded: 5 workers for pages, 10 workers for thread content
- Returns a pandas DataFrame with columns: `title`, `username`, `preview_url`, `description`
- Configurable via `config/config.py`

The query pipeline (Phases 2 and 3) is not yet built.

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

### Phase 2 — Filtered Listings Query (Planned)
- Accept an item name as input
- Scrape or load cached listings
- Keyword-filter listings relevant to the query
- Return the matching listings

### Phase 3 — Ollama Price Summary (Planned)
- Take filtered listings from Phase 2 as input
- Pass matching listings as context to a local Ollama LLM
- Return a price summary answer

## Open Decisions

- **Query interface:** CLI script (`python query.py "Stonetooth Sword"`) vs interactive REPL
- **Data freshness:** Re-scrape on every query (always fresh, slower) vs cache listings as CSV (fast, stale after time)

## Usage

```bash
# Install dependencies
pip install -e .

# Run the scraper (scrapes 5 pages, prints the DataFrame)
python scrape.py
```

### Configuration

Edit `config/config.py` to change scraper behaviour:

| Setting | Default | Description |
|---------|---------|-------------|
| `BASE_FORUM_URL` | `https://royals.ms/forum/` | Base URL for the forum |
| `DEFAULT_MAX_PAGES` | `2` | Pages to scrape by default |
| `PAGE_FETCH_WORKERS` | `5` | Concurrent page fetch threads |
| `THREAD_FETCH_WORKERS` | `10` | Concurrent thread fetch threads |

## Project Structure

```
royals_market_query/
├── config/
│   └── config.py          # Scraper configuration
├── src/
│   └── scraper/
│       └── forum_scraping_multi_thread.py  # ForumScrapper class
├── docs/
│   └── forum_scraping_multi_thread.md      # Scraper API docs
├── scrape.py              # Entry point
└── pyproject.toml         # Dependencies
```
