import time

from config.config import DEFAULT_MAX_PAGES
from src.scraper.forum_scraping_multi_thread import ForumScrapper

if __name__ == "__main__":
    start_time = time.time()
    maple_royals_url = "https://royals.ms/forum/forums/selling.17/"

    scraper = ForumScrapper(maple_royals_url)
    df = scraper.scrape_forum(max_pages=DEFAULT_MAX_PAGES)
    print(df)

    end_time = time.time()
    print(f"\nScraping finished in {end_time - start_time:.2f} seconds")
