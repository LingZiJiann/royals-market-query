# Forum base URL
BASE_FORUM_URL = "https://royals.ms/forum/"
SELLING_FORUM_URL = "https://royals.ms/forum/forums/selling.17/"

# Scraping defaults
DEFAULT_MAX_PAGES = 5

# Thread pool workers
PAGE_FETCH_WORKERS = 5
THREAD_FETCH_WORKERS = 10

# Cache settings
CACHE_FILE_PATH = "cache/listings.csv"
CACHE_TTL_MINUTES = 30

# Ollama LLM settings
OLLAMA_MODEL = "gpt-oss:20b"
OLLAMA_TIMEOUT = 60  # seconds
