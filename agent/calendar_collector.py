import requests
import json
from datetime import datetime, timedelta
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

IMPACT_MAP = {
    "icon--ff-impact-red": "Haute",
    "icon--ff-impact-ora": "Haute",
    "icon--ff-impact-yel": "Moyenne",
    "icon--ff-impact-gra": "Basse",
}

CURRENCY_NAMES = {
    "USD": "Dollar US", "EUR": "Euro", "GBP": "Livre Sterling",
    "JPY": "Yen", "CHF": "Franc Suisse", "CAD": "Dollar Canadien",
    "AUD": "Dollar Australien", "NZD": "Dollar Neo-Zelandais",
    "CNY": "Yuan Chinois",
}

_cache = {"data": None, "timestamp": None}
_CACHE_TTL = timedelta(minutes=15)


def fetch_calendar(days_ahead=7):
    global _cache
    now = datetime.now()
    if _cache["data"] is not None and _cache["timestamp"] is not None:
        if now - _cache["timestamp"] < _CACHE_TTL:
            return _cache["data"]
    try:
        resp = requests.get("https://www.forexfactory.com/calendar", headers=HEADERS, timeout=15)
        if resp.status_code != 200:
            if _cache["data"] is not None:
                return _cache["data"]
            return []
        events = parse_calendar(resp.text)
        _cache["data"] = events
        _cache["timestamp"] = now
        return events
    except:
        if _cache["data"] is not None:
            return _cache["data"]
        return []


def parse_calendar(html):
    soup = BeautifulSoup(html, "html.parser")
    events = []
    current_date = ""
    rows = soup.select("tr.calendar__row")
    for row in rows:
        date_cell = row.select_one("td.calendar__date")
        if date_cell:
            date_text = date_cell.get_text(strip=True)
            if date_text:
                current_date = date_text
        event_cell = row.select_one("td.calendar__event")
        if not event_cell:
            continue
        event_text = event_cell.get_text(strip=True)
        if not event_text:
            continue
        time_cell = row.select_one("td.calendar__time")
        currency_cell = row.select_one("td.calendar__currency")
        impact_cell = row.select_one("td.calendar__impact")
        actual_cell = row.select_one("td.calendar__actual")
        forecast_cell = row.select_one("td.calendar__forecast")
        previous_cell = row.select_one("td.calendar__previous")
        time_text = time_cell.get_text(strip=True) if time_cell else ""
        currency_text = currency_cell.get_text(strip=True) if currency_cell else ""
        impact_span = impact_cell.select_one("span.icon") if impact_cell else None
        impact = "Basse"
        if impact_span:
            for cls, label in IMPACT_MAP.items():
                if cls in impact_span.get("class", []):
                    impact = label
                    break
        events.append({
            "date": current_date,
            "time": time_text,
            "currency": currency_text,
            "currency_name": CURRENCY_NAMES.get(currency_text, currency_text),
            "event": event_text,
            "impact": impact,
            "actual": actual_cell.get_text(strip=True) if actual_cell else "",
            "forecast": forecast_cell.get_text(strip=True) if forecast_cell else "",
            "previous": previous_cell.get_text(strip=True) if previous_cell else "",
        })
    events.sort(key=lambda e: (e["date"], e["time"]))
    return events


def get_high_impact_events(days_ahead=7):
    return [e for e in fetch_calendar(days_ahead) if e["impact"] == "Haute"]


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
