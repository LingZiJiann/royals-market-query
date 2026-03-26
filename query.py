from config.config import (
    CACHE_FILE_PATH,
    CACHE_TTL_MINUTES,
    DEFAULT_MAX_PAGES,
    SELLING_FORUM_URL,
)
from src.query.listings_query import ListingsQuery

DIVIDER = "─" * 50


def print_listing(row) -> None:
    print(DIVIDER)
    print(f"Title:       {row['title']}")
    print(f"Seller:      {row['username']}")
    desc = str(row["description"])[:200]
    print(f"Description: {desc}")
    print(f"URL:         {row['preview_url']}")


def main() -> None:
    lq = ListingsQuery(
        cache_path=CACHE_FILE_PATH,
        ttl_minutes=CACHE_TTL_MINUTES,
        scraper_url=SELLING_FORUM_URL,
        max_pages=DEFAULT_MAX_PAGES,
    )

    listings = lq.load_or_scrape()
    print(f"Loaded {len(listings)} listings.\n")

    while True:
        try:
            item_name = input('Item name (or "quit" to exit): ').strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not item_name or item_name.lower() == "quit":
            break

        results = lq.filter_by_item(listings, item_name)

        if results.empty:
            print(f'No listings found for "{item_name}"\n')
            continue

        print(f'\nFound {len(results)} listing(s) for "{item_name}":')
        for _, row in results.iterrows():
            print_listing(row)
        print(DIVIDER + "\n")


if __name__ == "__main__":
    main()
