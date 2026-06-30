import os
from dotenv import load_dotenv

load_dotenv()

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama")

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "mistral")

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama3-70b-8192")

NEWSAPI_KEY = os.getenv("NEWSAPI_KEY", "")
FRED_API_KEY = os.getenv("FRED_API_KEY", "")

DAILY_BRIEF_HOUR = int(os.getenv("DAILY_BRIEF_HOUR", "8"))
DAILY_BRIEF_MINUTE = int(os.getenv("DAILY_BRIEF_MINUTE", "0"))
POLL_INTERVAL_MINUTES = int(os.getenv("POLL_INTERVAL_MINUTES", "15"))

MARKETS = {
    "XAUUSD": {"ticker": "GC=F", "name": "Or / Gold", "suffix": ""},
    "DXY": {"ticker": "DX-Y.NYB", "name": "Dollar Index", "suffix": ""},
    "EURUSD": {"ticker": "EURUSD=X", "name": "EUR/USD", "suffix": "=X"},
    "BTCUSD": {"ticker": "BTC-USD", "name": "Bitcoin", "suffix": ""},
    "NASDAQ100": {"ticker": "^NDX", "name": "Nasdaq 100", "suffix": ""},
}

CACHE_FILE = "data/cache.json"
