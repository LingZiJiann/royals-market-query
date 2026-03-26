import time
from pathlib import Path

import pandas as pd

from config.item_aliases import ITEM_ALIASES
from src.scraper.forum_scraping_multi_thread import ForumScrapper


class ListingsQuery:
    """Manages retrieval of forum listings via cache or live scraping.

    Attributes:
        _cache_path: Path to the CSV cache file.
        _ttl_seconds: Cache time-to-live in seconds.
        _scraper_url: Base URL passed to the forum scraper.
        _max_pages: Maximum number of forum pages to scrape.
    """

    def __init__(
        self,
        cache_path: str,
        ttl_minutes: int,
        scraper_url: str,
        max_pages: int,
    ):
        """Initializes ListingsQuery with cache and scraper settings.

        Args:
            cache_path: File path where scraped listings are cached as CSV.
            ttl_minutes: Number of minutes before the cache is considered stale.
            scraper_url: Base URL of the forum to scrape.
            max_pages: Maximum number of pages to scrape when refreshing.
        """
        self._cache_path = Path(cache_path)
        self._ttl_seconds = ttl_minutes * 60
        self._scraper_url = scraper_url
        self._max_pages = max_pages

    def _is_cache_fresh(self) -> bool:
        """Checks whether the cache file exists and is within the TTL.

        Returns:
            True if the cache file exists and its age is less than the TTL,
            False otherwise.
        """
        if not self._cache_path.exists():
            return False
        age = time.time() - self._cache_path.stat().st_mtime
        return age < self._ttl_seconds

    def load_or_scrape(self) -> pd.DataFrame:
        """Returns listings from cache if fresh, otherwise scrapes and caches.

        If the cache is fresh, reads and returns it directly. Otherwise,
        runs the forum scraper, saves the results to the cache path, and
        returns the scraped DataFrame.

        Returns:
            A DataFrame containing forum listing data with at minimum
            ``title`` and ``description`` columns.
        """
        if self._is_cache_fresh():
            age_minutes = int((time.time() - self._cache_path.stat().st_mtime) / 60)
            print(f"Loading cached listings (age: {age_minutes}m)...")
            return pd.read_csv(self._cache_path)

        print(f"Scraping {self._max_pages} page(s)...")
        scraper = ForumScrapper(self._scraper_url)
        df = scraper.scrape_forum(max_pages=self._max_pages)
        self._cache_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(self._cache_path, index=False)
        print(f"Cached {len(df)} listings to {self._cache_path}")
        return df

    def filter_by_item(self, df: pd.DataFrame, item_name: str) -> pd.DataFrame:
        """Filters listings whose title contains the item name.

        The search is case-insensitive. If ``item_name`` matches a key
        in ``ITEM_ALIASES``, the alias expansion terms are also searched so
        that acronyms like ``"gfa"`` match listings that say "gloves for attack".

        Args:
            df: DataFrame of listings, expected to have a ``title`` string column.
            item_name: The search term to match against the listing title. May be
                an acronym defined in ``ITEM_ALIASES``.

        Returns:
            A filtered DataFrame with the index reset, containing only rows
            that match any search term in the title.
        """
        base_query = item_name.lower()
        expanded = ITEM_ALIASES.get(base_query, [])
        search_terms = [base_query] + [t for t in expanded if t != base_query]

        def _contains_any(series: pd.Series) -> pd.Series:
            lower = series.str.lower()
            result = pd.Series(False, index=series.index)
            for term in search_terms:
                result |= lower.str.contains(term, na=False)
            return result

        mask = _contains_any(df["title"])
        return df[mask].reset_index(drop=True)
