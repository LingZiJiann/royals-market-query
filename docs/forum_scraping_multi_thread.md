# ForumScrapper

**Module:** `src/scraper/forum_scraping_multi_thread.py`

A multithreaded web scraper for the Royals.ms forum marketplace. It collects thread metadata and first-post content from paginated forum listings and returns the results as a pandas DataFrame.

---

## Configuration

Settings are centralized in `config/config.py` at the project root.

| Setting | Default | Description |
|---|---|---|
| `BASE_FORUM_URL` | `"https://royals.ms/forum/"` | Base URL prepended to thread paths |
| `DEFAULT_MAX_PAGES` | `2` | Default number of pages to scrape |
| `PAGE_FETCH_WORKERS` | `5` | Thread pool size for page fetching |
| `THREAD_FETCH_WORKERS` | `10` | Thread pool size for thread description fetching |

---

## Dependencies

| Package | Purpose |
|---|---|
| `requests` | HTTP session management |
| `bs4` (BeautifulSoup) | HTML parsing |
| `pandas` | DataFrame output |
| `concurrent.futures` | Multithreaded page/thread fetching |

---

## Class: `ForumScrapper`

### Constructor

```python
ForumScrapper(base_url: str)
```

| Parameter | Type | Description |
|---|---|---|
| `base_url` | `str` | URL of the forum section to scrape (e.g., the selling/buying board) |

A `requests.Session` is created on initialization and reused across all requests.

---

## Public Methods

### `get_thread_metadata(page_url: str) -> List[Dict[str, str]]`

Scrapes thread listing metadata from a single forum page.

**Returns** a list of dicts, one per thread:

| Key | Description |
|---|---|
| `title` | Thread title text |
| `preview_url` | Full URL to the thread (with `/preview` suffix removed) |
| `username` | Thread author's username |

Threads are selected via CSS selector `li.discussionListItem`. Entries without a `.PreviewTooltip` link are skipped.

---

### `get_all_threads(max_pages: int = DEFAULT_MAX_PAGES) -> List[Dict[str, str]]`

Scrapes thread metadata across multiple paginated pages **concurrently** using a `ThreadPoolExecutor` with `PAGE_FETCH_WORKERS` workers.

| Parameter | Default | Description |
|---|---|---|
| `max_pages` | `DEFAULT_MAX_PAGES` | Number of pages to scrape |

Page URLs are constructed as:
- Page 1: `base_url`
- Page N: `base_url + "page-N"`

---

### `fetch_thread_description(threads: List[Dict[str, str]]) -> List[Dict[str, str]]`

Fetches the first post content for each thread **concurrently** using `THREAD_FETCH_WORKERS` workers. Adds a `"description"` key to each thread dict.

> **Note:** The first thread in the list is skipped, as it is assumed to be a pinned/sticky thread.

---

### `scrape_forum(max_pages: int = DEFAULT_MAX_PAGES) -> pd.DataFrame`

High-level entry point. Orchestrates the full scrape pipeline:

1. `get_all_threads()` — collect thread metadata across pages
2. `fetch_thread_description()` — fetch first-post text for each thread
3. Convert to `pd.DataFrame` and return

**Returns:** A DataFrame with columns `title`, `preview_url`, `username`, and `description`.

---

## Private Methods

### `_get_soup(url: str) -> BeautifulSoup`

Sends a GET request and parses the response into a BeautifulSoup object. Raises an `HTTPError` if the response status is not 2xx.

### `_get_first_post(preview_url: str) -> str`

Fetches a thread page and extracts the text of the first `<article>` element (the opening post body).

---

## Usage Example

```python
from src.scraper.forum_scraping_multi_thread import ForumScrapper

scraper = ForumScrapper(base_url="https://royals.ms/forum/forums/selling.123/")
df = scraper.scrape_forum(max_pages=5)
print(df.head())
```

---

## Concurrency Overview

| Method | Workers (config key) | Unit of work |
|---|---|---|
| `get_all_threads` | `PAGE_FETCH_WORKERS` (default: 5) | One page per worker |
| `fetch_thread_description` | `THREAD_FETCH_WORKERS` (default: 10) | One thread per worker |
