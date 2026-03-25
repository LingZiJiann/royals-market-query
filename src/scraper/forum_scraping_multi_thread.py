import concurrent.futures
from typing import Dict, List

import pandas as pd
import requests
from bs4 import BeautifulSoup


class ForumScrapper:
    def __init__(self, base_url: str):
        """
        Initialize the ForumScrapper with the base URL of the forum section.

        Args:
            base_url (str): The URL of the forum page to scrape.
        """
        self.base_url = base_url
        self.session = requests.Session()

    def _get_soup(self, url: str) -> BeautifulSoup:
        """
        Send a GET request to a URL and parse the HTML content.

        Args:
            url (str): The URL to fetch.

        Returns:
            BeautifulSoup: A BeautifulSoup object representing the page's HTML.
        """
        response = self.session.get(url)
        response.raise_for_status()
        return BeautifulSoup(response.text, "html.parser")

    def get_thread_metadata(self, page_url: str) -> List[Dict[str, str]]:
        """
        Scrape metadata of threads from the forum selling section.

        This method fetches the HTML content of the base forum URL and parses it to
        extract information about each thread, including the title, full URL, and
        author's username.

        Returns:
            List[Dict[str, str]]: A list of dictionaries, where each dictionary
            represents a discussion thread with the following keys:
                - "title": The thread title text.
                - "preview_url": The preview URL associated with the thread
                  (removes the '/preview' suffix if present).
                - "username": The username of the thread author.
        """
        soup = self._get_soup(page_url)
        base_forum_url = "https://royals.ms/forum/"
        threads = []

        for li in soup.select("li.discussionListItem"):
            link = li.select_one("h3.title a.PreviewTooltip")
            if not link:
                continue

            threads.append(
                {
                    "title": link.get_text(strip=True),
                    "preview_url": (
                        f"{base_forum_url}"
                        f"{link.get('data-previewurl').removesuffix('/preview')}"
                    ),
                    "username": li.select_one("a.username").get_text(strip=True),
                }
            )
        return threads

    def get_all_threads(self, max_pages: int = 2) -> List[Dict[str, str]]:
        """
        Scrape all threads across paginated pages concurrently.

        Args:
            max_pages (int, optional): Number of pages to scrape. Defaults to 2.

        Returns:
            List[Dict[str, str]]: A list of thread metadata dictionaries
            across all pages.
        """
        page_urls = [self.base_url] + [
            f"{self.base_url}page-{i}" for i in range(2, max_pages + 1)
        ]

        def fetch_page_threads(url):
            print(f"Scraping page: {url}")
            return self.get_thread_metadata(url)

        all_threads = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            page_results = executor.map(fetch_page_threads, page_urls)
            for threads_on_page in page_results:
                all_threads.extend(threads_on_page)

        return all_threads

    def fetch_thread_description(
        self, threads: List[Dict[str, str]]
    ) -> List[Dict[str, str]]:
        """
        Fetch first post content for each thread concurrently (skip pinned thread).

        Args:
            threads (List[Dict[str, str]]): List of thread metadata dictionaries.

        Returns:
            List[Dict[str, str]]: List of thread dictionaries with an added
            "description" key containing the first post text.
        """
        # Skip pinned thread
        threads_to_fetch = threads[1:]

        def fetch_thread_post(thread):
            thread["description"] = self._get_first_post(thread["preview_url"])
            return thread

        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            return list(executor.map(fetch_thread_post, threads_to_fetch))

    def _get_first_post(self, preview_url: str) -> str:
        """
        Retrieve the text content of the first post in a thread.

        Args:
            preview_url (str): The full URL to the thread.

        Returns:
            str: The text content of the first post found in the page,
                    with leading and trailing whitespace removed.
        """
        soup = self._get_soup(preview_url)
        first_article = soup.find("article")
        return first_article.get_text(strip=True)

    def scrape_forum(self, max_pages: int = 2) -> pd.DataFrame:
        """
        Scrape threads and their first posts from the forum, returning a DataFrame.

        This is a high-level method that combines:
        1. Scraping thread metadata across multiple pages.
        2. Fetching the first post content for each thread.
        3. Converting the results into a pandas DataFrame.

        Args:
            max_pages (int, optional): Maximum number of pages to scrape. Defaults to 2.

        Returns:
            pd.DataFrame: DataFrame containing thread metadata and first post
            descriptions.
        """
        # Step 1: Get all threads
        all_threads = self.get_all_threads(max_pages=max_pages)

        # Step 2: Get first post content
        threads_with_desc = self.fetch_thread_description(all_threads)

        # Step 3: Convert to DataFrame
        df = pd.DataFrame(threads_with_desc)
        return df
