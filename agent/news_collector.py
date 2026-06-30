import feedparser
import requests
import hashlib
from datetime import datetime
from bs4 import BeautifulSoup
from config import NEWSAPI_KEY, RSS_FEEDS


def fetch_rss():
    articles = []
    for feed_url in RSS_FEEDS:
        try:
            feed = feedparser.parse(feed_url, timeout=10)
            for entry in feed.entries[:10]:
                articles.append({
                    "title": entry.get("title", ""),
                    "summary": entry.get("summary", entry.get("description", "")),
                    "link": entry.get("link", ""),
                    "source": feed.feed.get("title", feed_url.split("/")[2]),
                    "published": entry.get("published", str(datetime.now())),
                    "id": hashlib.md5(entry.get("link", entry.get("title", "")).encode()).hexdigest(),
                })
        except:
            pass
    return articles


def fetch_newsapi():
    if not NEWSAPI_KEY:
        return []
    articles = []
    try:
        queries = [
            ("economy", "business"),
            ("Federal Reserve", "markets"),
            ("gold trading", "markets"),
            ("forex dollar", "markets"),
            ("bitcoin crypto", "cryptocurrency"),
            ("stock market nasdaq", "business"),
        ]
        seen = set()
        for q, category in queries:
            url = f"https://newsapi.org/v2/everything?q={q}&language=en&pageSize=5&apiKey={NEWSAPI_KEY}"
            resp = requests.get(url, timeout=10)
            if resp.status_code != 200:
                continue
            data = resp.json()
            for a in data.get("articles", []):
                aid = hashlib.md5(a["url"].encode()).hexdigest()
                if aid not in seen:
                    seen.add(aid)
                    articles.append({
                        "title": a["title"],
                        "summary": a.get("description", ""),
                        "link": a["url"],
                        "source": a["source"]["name"] if a.get("source") else "NewsAPI",
                        "published": a.get("publishedAt", str(datetime.now())),
                        "id": aid,
                    })
    except:
        pass
    return articles


def fetch_macro_news():
    articles = []
    sources = [
        "https://www.forexfactory.com/feed/news",
    ]
    for url in sources:
        try:
            feed = feedparser.parse(url, timeout=10)
            for entry in feed.entries[:5]:
                articles.append({
                    "title": entry.get("title", ""),
                    "summary": entry.get("summary", entry.get("description", "")),
                    "link": entry.get("link", ""),
                    "source": "ForexFactory",
                    "published": entry.get("published", str(datetime.now())),
                    "id": hashlib.md5(entry.get("link", entry.get("title", "")).encode()).hexdigest(),
                })
        except:
            pass
    return articles


def get_all_news():
    all_articles = fetch_rss() + fetch_newsapi() + fetch_macro_news()
    seen = set()
    unique = []
    for a in all_articles:
        if a["id"] not in seen:
            seen.add(a["id"])
            unique.append(a)
    unique.sort(key=lambda x: x.get("published", ""), reverse=True)
    return unique[:50]
