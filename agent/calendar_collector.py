import requests
from datetime import datetime, timedelta

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Origin": "https://www.tradingview.com",
    "Referer": "https://www.tradingview.com/",
}

COUNTRY_CURRENCY = {
    "US": "USD", "EU": "EUR", "GB": "GBP", "JP": "JPY", "CH": "CHF",
    "CA": "CAD", "AU": "AUD", "NZ": "NZD", "CN": "CNY",
}

IMPACT_LABEL = {1: "Haute", 0: "Moyenne", -1: "Basse"}

CURRENCY_NAMES = {
    "USD": "Dollar US", "EUR": "Euro", "GBP": "Livre Sterling",
    "JPY": "Yen", "CHF": "Franc Suisse", "CAD": "Dollar Canadien",
    "AUD": "Dollar Australien", "NZD": "Dollar Neo-Zelandais", "CNY": "Yuan",
}

_cache = {"data": None, "timestamp": None}
_CACHE_TTL = timedelta(minutes=15)

IMPORTANT_INDICATORS = [
    "Interest Rate", "CPI", "GDP", "Employment", "Non Farm Payrolls",
    "Unemployment", "FOMC", "Fed", "BCE", "NFP", "Inflation",
    "PPI", "Retail Sales", "PMI", "Manufacturing", "Services",
    "Housing", "Consumer Confidence", "Trade Balance", "JOLTS",
    "Industrial Production", "Capacity Utilization",
]


def fetch_calendar(days=7):
    global _cache
    now = datetime.now()
    if _cache["data"] and _cache["timestamp"] and now - _cache["timestamp"] < _CACHE_TTL:
        return _cache["data"]
    try:
        today = now.strftime("%Y-%m-%d")
        end = (now + timedelta(days=days)).strftime("%Y-%m-%d")
        resp = requests.get(
            "https://economic-calendar.tradingview.com/events",
            params={"from": today, "to": end},
            headers=HEADERS,
            timeout=15,
        )
        if resp.status_code != 200:
            return _cache["data"] or []
        raw = resp.json().get("result", [])
        events = []
        for e in raw:
            currency = e.get("currency", "") or COUNTRY_CURRENCY.get(e.get("country", ""), e.get("country", ""))
            importance = e.get("importance", -1)
            event_name = e.get("indicator", "") or e.get("title", "")
            events.append({
                "date": e.get("date", "")[:10],
                "time": e.get("date", "")[11:16] if e.get("date") else "",
                "currency": currency,
                "currency_name": CURRENCY_NAMES.get(currency, currency),
                "event": event_name,
                "title": e.get("title", ""),
                "impact": IMPACT_LABEL.get(importance, "Basse"),
                "importance": importance,
                "actual": e.get("actual") or "",
                "forecast": e.get("forecast") or "",
                "previous": e.get("previous") or "",
            })
        events.sort(key=lambda e: e["date"] + e["time"])
        _cache = {"data": events, "timestamp": now}
        return events
    except:
        return _cache["data"] or []


def get_high_impact_events(days=7):
    return [e for e in fetch_calendar(days) if e["importance"] >= 0]


def format_calendar_for_prompt(events, max_events=15):
    if not events:
        return "Aucun evenement economique a venir."
    lines = []
    for e in events[:max_events]:
        line = f"  [{e['impact']}] {e['date']} {e['time']} | {e['currency']} - {e['event']}"
        if e["forecast"] or e["previous"]:
            line += f" | Prev: {e['forecast']} | Prec: {e['previous']}"
        lines.append(line)
    return "\n".join(lines)
