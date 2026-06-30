import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from config import MARKETS


def fetch_current_prices():
    results = {}
    for key, info in MARKETS.items():
        try:
            ticker = yf.Ticker(info["ticker"])
            hist = ticker.history(period="5d")
            if hist.empty:
                continue
            last = hist["Close"].iloc[-1]
            prev = hist["Close"].iloc[-2] if len(hist) > 1 else last
            week_ago = hist["Close"].iloc[-5] if len(hist) >= 5 else prev
            change_1d = ((last - prev) / prev) * 100
            change_5d = ((last - week_ago) / week_ago) * 100
            high = hist["High"].iloc[-1]
            low = hist["Low"].iloc[-1]
            results[key] = {
                "name": info["name"],
                "price": round(last, 2),
                "change_1d": round(change_1d, 2),
                "change_5d": round(change_5d, 2),
                "high_24h": round(high, 2),
                "low_24h": round(low, 2),
                "timestamp": datetime.now().isoformat(),
            }
        except:
            pass
    return results


def fetch_historical_data(period="1mo"):
    data = {}
    for key, info in MARKETS.items():
        try:
            ticker = yf.Ticker(info["ticker"])
            hist = ticker.history(period=period)
            if not hist.empty:
                data[key] = hist[["Close"]].reset_index()
                data[key].columns = ["Date", "Close"]
        except:
            pass
    return data


def fetch_fred_data(series_id, name):
    from config import FRED_API_KEY
    if not FRED_API_KEY:
        return None
    try:
        url = f"https://api.stlouisfed.org/fred/series/observations?series_id={series_id}&api_key={FRED_API_KEY}&file_type=json&sort_order=desc&limit=10"
        resp = __import__("requests").get(url, timeout=10)
        if resp.status_code == 200:
            obs = resp.json().get("observations", [])
            return {"name": name, "data": obs}
    except:
        pass
    return None
