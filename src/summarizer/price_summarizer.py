import ollama
import pandas as pd

from config.config import OLLAMA_MODEL, OLLAMA_TIMEOUT

SYSTEM_PROMPT = """You are a price analysis assistant for the Maple Royals
MapleStory private server marketplace.
Your job is to read forum selling listings and summarize the asking prices
for a specific item.

Rules:
- Prices use in-game mesos. "m"/"M" = million (500m = 500 million).
  "b"/"B" = billion (1b = 1000m).
- Convert all prices to millions for consistency before averaging.
- S/B = Starting Bid (min asking price). A/W = Auto Win (max asking price).
- C/O = Current Offer — ignore these entirely.
- A listing may sell multiple items. Only extract prices that clearly
  refer to the requested item.
- These are ASKING PRICES posted by sellers, NOT confirmed sale prices."""


class PriceSummarizer:
    """Summarizes marketplace listing prices for a given item using a local LLM.

    Attributes:
        _model: Ollama model name to use for inference.
        _timeout: Request timeout in seconds.
    """

    def __init__(self, model: str = OLLAMA_MODEL, timeout: int = OLLAMA_TIMEOUT):
        """Initializes PriceSummarizer with the given model and timeout.

        Args:
            model: Ollama model name. Defaults to OLLAMA_MODEL from config.
            timeout: Request timeout in seconds. Defaults to OLLAMA_TIMEOUT from config.
        """
        self._model = model
        self._timeout = timeout

    def summarize(self, item_name: str, listings: pd.DataFrame) -> str:
        """Generates a price summary for an item from a set of forum listings.

        Args:
            item_name: The name of the item to summarize prices for.
            listings: DataFrame of listings, expected to have columns: title,
                date, preview_url, description.

        Returns:
            A human-readable price summary string, or an error/notice message
            if listings are empty or the LLM call fails.
        """
        if listings.empty:
            return f'No listings found for "{item_name}" — cannot summarize.'
        prompt = self._build_prompt(item_name, listings)
        try:
            return self._call_ollama(prompt)
        except ollama.ResponseError as e:
            return f"[Summarizer error] Ollama returned an error: {e}"
        except Exception as e:
            return f"[Summarizer error] Unexpected error calling Ollama: {e}"

    def _build_prompt(self, item_name: str, listings: pd.DataFrame) -> str:
        """Builds the user prompt from item name and listings data.

        Args:
            item_name: The item to ask the LLM to price-summarize.
            listings: DataFrame of listings to include as context.

        Returns:
            A formatted prompt string ready to send to the LLM.
        """
        blocks = []
        for i, row in enumerate(listings.itertuples(), start=1):
            desc = str(row.description)[:400]
            blocks.append(
                f"--- Listing {i} ---\n"
                f"Title: {row.title}\n"
                f"Date: {row.date}\n"
                f"URL: {row.preview_url}\n"
                f"Description: {desc}"
            )
        context = "\n\n".join(blocks)
        dates = listings["date"].dropna()
        date_range = (
            f"{dates.min()} to {dates.max()}"
            if len(dates) > 1
            else str(dates.iloc[0])
            if len(dates) == 1
            else "unknown"
        )
        return (
            f"Item: {item_name}\n\n"
            f"Here are {len(listings)} listing(s) that mention this item"
            f" (date range: {date_range}):\n\n"
            f"{context}\n\n"
            f'For each listing that mentions "{item_name}", return:\n'
            f"1. Item\n"
            f"2. Price (include S/B, C/O, and A/W if listed)\n"
            f"3. URL\n"
            f"4. Date of the listing\n\n"
            f"If no clear price exists for a listing, say so."
        )

    def _call_ollama(self, prompt: str) -> str:
        """Sends the prompt to Ollama and returns the response text.

        Args:
            prompt: The user prompt to send.

        Returns:
            The LLM's response content as a string.

        Raises:
            ollama.ResponseError: If Ollama returns an error response.
        """
        response = ollama.chat(
            model=self._model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
        )
        return response.message.content
