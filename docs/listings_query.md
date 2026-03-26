# ListingsQuery

**Module:** `src/query/listings_query.py`
**Entry point:** `query.py`

A query layer on top of `ForumScrapper` that adds CSV caching and keyword filtering. Run `query.py` for an interactive REPL — listings are scraped once and reused across queries until the cache expires.

---

## Configuration

Settings are centralized in `config/config.py` at the project root.

| Setting | Default | Description |
|---|---|---|
| `SELLING_FORUM_URL` | `"https://royals.ms/forum/forums/selling.17/"` | Forum section URL passed to `ForumScrapper` |
| `CACHE_FILE_PATH` | `"cache/listings.csv"` | Path where scraped listings are cached |
| `CACHE_TTL_MINUTES` | `30` | Minutes before the cache is considered stale |
| `DEFAULT_MAX_PAGES` | `2` | Number of pages to scrape when refreshing the cache |

---

## Dependencies

| Package | Purpose |
|---|---|
| `pandas` | DataFrame handling and CSV I/O |
| `pathlib` | Cache file path management |
| `src.scraper.forum_scraping_multi_thread` | Underlying scraper (`ForumScrapper`) |

---

## Class: `ListingsQuery`

### Constructor

```python
ListingsQuery(
    cache_path: str,
    ttl_minutes: int,
    scraper_url: str,
    max_pages: int,
)
```

| Parameter | Type | Description |
|---|---|---|
| `cache_path` | `str` | File path for the CSV cache |
| `ttl_minutes` | `int` | Cache time-to-live in minutes |
| `scraper_url` | `str` | Forum section URL to scrape |
| `max_pages` | `int` | Pages to scrape when cache is stale or missing |

---

## Public Methods

### `load_or_scrape() -> pd.DataFrame`

Returns a DataFrame of all marketplace listings. Checks the cache first:

- **Cache fresh** (file exists, age < TTL): loads and returns the CSV.
- **Cache stale or missing**: scrapes via `ForumScrapper.scrape_forum()`, writes results to the cache file (creating the directory if needed), and returns the DataFrame.

Prints a status line in both cases so the caller can see whether a scrape occurred.

**Returns:** A DataFrame with columns `title`, `preview_url`, `username`, `description`.

---

### `filter_by_item(df: pd.DataFrame, item_name: str) -> pd.DataFrame`

Filters a listings DataFrame to rows that mention `item_name`.

| Parameter | Type | Description |
|---|---|---|
| `df` | `pd.DataFrame` | Full listings DataFrame from `load_or_scrape()` |
| `item_name` | `str` | Item to search for (case-insensitive) |

**Matching logic:** case-insensitive substring match against `title` **OR** `description`. For example, `"Stonetooth Sword"` matches any row where that string appears in either column.

**Returns:** A filtered DataFrame (empty if no matches), with the index reset.

---

## Private Methods

### `_is_cache_fresh() -> bool`

Returns `True` if the cache file exists and its modification time is within the configured TTL.

---

## Usage Example

```python
from config.config import CACHE_FILE_PATH, CACHE_TTL_MINUTES, DEFAULT_MAX_PAGES, SELLING_FORUM_URL
from src.query.listings_query import ListingsQuery

lq = ListingsQuery(
    cache_path=CACHE_FILE_PATH,
    ttl_minutes=CACHE_TTL_MINUTES,
    scraper_url=SELLING_FORUM_URL,
    max_pages=DEFAULT_MAX_PAGES,
)

listings = lq.load_or_scrape()
results = lq.filter_by_item(listings, "Stonetooth Sword")
print(results)
```

---

## Interactive REPL (`query.py`)

```bash
python query.py
```

1. Calls `load_or_scrape()` once on startup and holds the DataFrame in memory.
2. Prompts for an item name in a loop.
3. Filters and prints matching listings:

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

4. Exits on empty input or `quit`.

The cache persists between REPL sessions. Re-running within the TTL window skips the scrape entirely.
