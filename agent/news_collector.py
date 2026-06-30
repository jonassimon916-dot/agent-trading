import feedparser
import requests
import hashlib
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from config import NEWSAPI_KEY

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

RSS_SOURCES = [
    {"url": "https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRGx1YlY4U0FtVnVHZ0pWVXlnQVAB", "source": "Google News (Business)"},
    {"url": "https://feeds.bloomberg.com/markets/news.rss", "source": "Bloomberg"},
    {"url": "https://www.cnbc.com/id/100003114/device/rss/rss.html", "source": "CNBC"},
    {"url": "https://finance.yahoo.com/news/rssindex", "source": "Yahoo Finance"},
    {"url": "https://www.investing.com/rss/news.rss", "source": "Investing.com"},
    {"url": "https://www.investing.com/rss/market_overview.rss", "source": "Investing.com"},
    {"url": "https://rss.nytimes.com/services/xml/rss/nyt/Economy.xml", "source": "NYT"},
    {"url": "https://cointelegraph.com/rss", "source": "CoinTelegraph"},
]


def fetch_rss_feed(url):
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        if resp.status_code != 200:
            return []
        feed = feedparser.parse(resp.content)
        return feed.entries
    except:
        return []


def extract_articles(entries, source_name):
    articles = []
    for entry in entries[:8]:
        title = entry.get("title", "")
        summary = entry.get("summary", entry.get("description", ""))
        link = entry.get("link", "")
        published = entry.get("published", str(datetime.now()))
        pub_date = datetime.now()
        try:
            parsed = feedparser._parse_date(published)
            if parsed:
                pub_date = datetime(*parsed[:6])
        except:
            pass
        articles.append({
            "title": title,
            "summary": BeautifulSoup(summary, "html.parser").get_text()[:300] if summary else "",
            "link": link,
            "source": source_name,
            "published": published,
            "date": pub_date,
            "id": hashlib.md5(link.encode()).hexdigest() if link else hashlib.md5(title.encode()).hexdigest(),
        })
    return articles


def fetch_newsapi():
    if not NEWSAPI_KEY:
        return []
    articles = []
    try:
        queries = [
            "economy", "Federal Reserve", "gold trading", "forex dollar",
            "bitcoin crypto", "stock market nasdaq", "inflation",
        ]
        seen = set()
        for q in queries:
            url = f"https://newsapi.org/v2/everything?q={q}&language=en&pageSize=4&apiKey={NEWSAPI_KEY}"
            resp = requests.get(url, headers=HEADERS, timeout=10)
            if resp.status_code != 200:
                continue
            data = resp.json()
            for a in data.get("articles", []):
                aid = hashlib.md5(a["url"].encode()).hexdigest()
                if aid not in seen:
                    seen.add(aid)
                    articles.append({
                        "title": a["title"],
                        "summary": a.get("description", "") or "",
                        "link": a["url"],
                        "source": a["source"]["name"] if a.get("source") else "NewsAPI",
                        "published": a.get("publishedAt", str(datetime.now())),
                        "date": datetime.now(),
                        "id": aid,
                    })
    except:
        pass
    return articles


def get_all_news():
    all_articles = []
    seen_ids = set()

    for rss in RSS_SOURCES:
        entries = fetch_rss_feed(rss["url"])
        for article in extract_articles(entries, rss["source"]):
            if article["id"] not in seen_ids and article["title"]:
                seen_ids.add(article["id"])
                all_articles.append(article)

    for article in fetch_newsapi():
        if article["id"] not in seen_ids and article["title"]:
            seen_ids.add(article["id"])
            all_articles.append(article)

    all_articles.sort(key=lambda x: x.get("date", datetime.now()), reverse=True)
    return all_articles[:40]
