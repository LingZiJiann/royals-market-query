# PriceSummarizer

**Module:** `src/summarizer/price_summarizer.py`

Uses a local LLM (via Ollama) to read forum selling listings and produce a human-readable price summary for a specific item.

---

## Configuration

Settings are centralized in `config/config.py` at the project root.

| Setting | Default | Description |
|---|---|---|
| `OLLAMA_MODEL` | — | Ollama model name used for inference |
| `OLLAMA_TIMEOUT` | — | Request timeout in seconds |

---

## Price Notation

The LLM is instructed to interpret the following Maple Royals marketplace conventions:

| Notation | Meaning |
|---|---|
| `m` / `M` | Million mesos (e.g. `500m` = 500,000,000) |
| `b` / `B` | Billion mesos (e.g. `1b` = 1,000,000,000) |
| `S/B` | Starting Bid — minimum asking price |
| `A/W` | Auto Win — maximum asking price |
| `C/O` | Current Offer — **ignored** (not an asking price) |

All prices are normalized to millions before averaging.

---

## Dependencies

| Package | Purpose |
|---|---|
| `ollama` | Local LLM inference client |
| `pandas` | DataFrame input for listings |
| `config.config` | `OLLAMA_MODEL` and `OLLAMA_TIMEOUT` constants |

---

## Class: `PriceSummarizer`

### Constructor

```python
PriceSummarizer(
    model: str = OLLAMA_MODEL,
    timeout: int = OLLAMA_TIMEOUT,
)
```

| Parameter | Type | Description |
|---|---|---|
| `model` | `str` | Ollama model name. Defaults to `OLLAMA_MODEL` from config. |
| `timeout` | `int` | Request timeout in seconds. Defaults to `OLLAMA_TIMEOUT` from config. |

---

## Public Methods

### `summarize(item_name: str, listings: pd.DataFrame) -> str`

Generates a price summary for an item from a set of forum listings.

| Parameter | Type | Description |
|---|---|---|
| `item_name` | `str` | The name of the item to summarize prices for |
| `listings` | `pd.DataFrame` | Listings DataFrame with columns: `title`, `date`, `preview_url`, `description` |

**Returns:** A human-readable price summary string. Returns a notice if `listings` is empty, or an error message if the Ollama call fails.

**Error handling:**

- `ollama.ResponseError` — caught and returned as `[Summarizer error] Ollama returned an error: ...`
- Any other exception — caught and returned as `[Summarizer error] Unexpected error calling Ollama: ...`

---

## Private Methods

### `_build_prompt(item_name: str, listings: pd.DataFrame) -> str`

Formats the listings into a structured prompt for the LLM. Each listing block includes its title, date, URL, and up to 400 characters of description. The prompt also includes the date range of listings and instructs the LLM to return item name, S/B / A/W price, URL, and date per listing.

---

### `_call_ollama(prompt: str) -> str`

Sends the system prompt and user prompt to Ollama via `ollama.chat()` and returns the response content.

**Raises:** `ollama.ResponseError` if Ollama returns an error response.

---

## Usage Example

```python
from config.config import OLLAMA_MODEL, OLLAMA_TIMEOUT
from src.summarizer.price_summarizer import PriceSummarizer

summarizer = PriceSummarizer()
summary = summarizer.summarize("Stonetooth Sword", filtered_listings)
print(summary)
```

---

## LLM Output Format

For each relevant listing, the LLM returns:

1. **Item** — full item name as it appears in the listing title (e.g. `17 BWG` if you searched `bwg`)
2. **Price** — S/B and/or A/W if present; notes if no clear price exists
3. **URL** — link to the forum thread
4. **Date** — date of the listing

These are **asking prices posted by sellers**, not confirmed sale prices.
