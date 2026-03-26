import pathlib
import re
import tempfile
import time
import webbrowser

import markdown as md

from config.config import (
    CACHE_FILE_PATH,
    CACHE_TTL_MINUTES,
    DEFAULT_MAX_PAGES,
    OLLAMA_MODEL,
    OLLAMA_TIMEOUT,
    SELLING_FORUM_URL,
)
from src.query.listings_query import ListingsQuery
from src.summarizer.price_summarizer import PriceSummarizer

DIVIDER = "─" * 50


def _open_summary_in_browser(item_name: str, summary: str) -> None:
    linked = re.sub(r"(?<!\()(?<!\[)(https?://\S+)", r"[\1](\1)", summary)
    body = md.markdown(linked, extensions=["tables"])
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Price Summary: {item_name}</title>
  <style>
    body {{ font-family: sans-serif; max-width: 860px;
            margin: 40px auto; padding: 0 20px; }}
    h1 {{ font-size: 1.4rem; color: #333; }}
    table {{ border-collapse: collapse; width: 100%; margin-top: 12px; }}
    th, td {{ border: 1px solid #ddd; padding: 8px 12px; text-align: left; }}
    th {{ background: #f0f0f0; font-weight: 600; }}
    tr:nth-child(even) {{ background: #fafafa; }}
    a {{ color: #1a73e8; }}
  </style>
</head>
<body>
  <h1>Price Summary: {item_name}</h1>
  {body}
</body>
</html>"""
    tmp = pathlib.Path(tempfile.mktemp(suffix=".html"))
    tmp.write_text(html, encoding="utf-8")
    webbrowser.open(tmp.as_uri())
    print("Summary opened in browser.")


def print_listing(row) -> None:
    print(DIVIDER)
    print(f"Title:       {row['title']}")
    print(f"Seller:      {row['username']}")
    print(f"Date:        {row['date']}")
    desc = str(row["description"])[:200]
    print(f"Description: {desc}")
    url = row["preview_url"]
    print(f"URL:         \033]8;;{url}\033\\{url}\033]8;;\033\\")


def main() -> None:
    lq = ListingsQuery(
        cache_path=CACHE_FILE_PATH,
        ttl_minutes=CACHE_TTL_MINUTES,
        scraper_url=SELLING_FORUM_URL,
        max_pages=DEFAULT_MAX_PAGES,
    )
    summarizer = PriceSummarizer(model=OLLAMA_MODEL, timeout=OLLAMA_TIMEOUT)

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

        print("Generating price summary...")
        start = time.perf_counter()
        summary = summarizer.summarize(item_name, results)
        print(f"Summarizer took {time.perf_counter() - start:.1f}s")
        _open_summary_in_browser(item_name, summary)


if __name__ == "__main__":
    main()
