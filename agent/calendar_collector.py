import requests
from datetime import datetime, timedelta

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Origin": "https://www.tradingview.com",
    "Referer": "https://www.tradingview.com/",
}

IMPACT_LABEL = {1: "Haute", 0: "Moyenne", -1: "Basse"}

CURRENCY_DATA = {
    "USD": {"name": "Dollar US", "flag": ":flag-us:"},
    "EUR": {"name": "Euro", "flag": ":flag-eu:"},
    "GBP": {"name": "Livre Sterling", "flag": ":flag-gb:"},
    "JPY": {"name": "Yen", "flag": ":flag-jp:"},
    "CHF": {"name": "Franc Suisse", "flag": ":flag-ch:"},
    "CAD": {"name": "Dollar Canadien", "flag": ":flag-ca:"},
    "AUD": {"name": "Dollar Australien", "flag": ":flag-au:"},
    "NZD": {"name": "Dollar Neo-Zelandais", "flag": ":flag-nz:"},
    "CNY": {"name": "Yuan Chinois", "flag": ":flag-cn:"},
}

TOP_CURRENCIES = ["USD", "EUR", "GBP", "JPY", "CHF", "CAD", "AUD", "NZD"]

_cache = {"data": None, "timestamp": None}


def fetch_calendar(days=7):
    global _cache
    now = datetime.now()
    if _cache["data"] and _cache["timestamp"]:
        if now - _cache["timestamp"] < timedelta(minutes=15):
            return _cache["data"]
    try:
        start = now.strftime("%Y-%m-%d")
        end = (now + timedelta(days=days)).strftime("%Y-%m-%d")
        resp = requests.get(
            "https://economic-calendar.tradingview.com/events",
            params={"from": start, "to": end},
            headers=HEADERS,
            timeout=15,
        )
        if resp.status_code != 200:
            return _cache["data"] or []
        raw = resp.json().get("result", [])
        events = {}
        for e in raw:
            imp = e.get("importance", -1)
            if imp < 0:
                continue
            currency = e.get("currency", "")
            if currency not in TOP_CURRENCIES:
                continue
            event_name = e.get("indicator", "") or e.get("title", "")
            iso = e.get("date", "")
            day = iso[:10] if iso else ""
            time_str = iso[11:16] if iso else ""
            actual = e.get("actual") or ""
            forecast = e.get("forecast") or ""
            previous = e.get("previous") or ""
            direction = ""
            if actual and forecast:
                try:
                    a, f = float(actual), float(forecast)
                    direction = "up" if a > f else ("down" if a < f else "flat")
                except:
                    pass
            import hashlib
            uid = hashlib.md5(f"{day}|{currency}|{event_name}".encode()).hexdigest()[:10]
            event = {
                "id": uid,
                "day": day,
                "time": time_str,
                "currency": currency,
                "event": event_name,
                "impact": imp,
                "impact_label": IMPACT_LABEL.get(imp, "Basse"),
                "actual": actual,
                "forecast": forecast,
                "previous": previous,
                "direction": direction,
            }
            dk = f"{day}|{time_str}|{currency}|{event_name}"
            events[dk] = event
        result = sorted(events.values(), key=lambda e: e["day"] + e["time"])
        _cache = {"data": result, "timestamp": now}
        return result
    except:
        return _cache["data"] or []


def get_calendar_for_dashboard(days=7):
    return fetch_calendar(days)


def format_calendar_for_prompt(events, max_events=12):
    if not events:
        return "Aucun evenement economique a venir."
    lines = []
    for e in events[:max_events]:
        line = f"  [{e['impact_label']}] {e['day']} {e['time']} | {e['currency']} - {e['event']}"
        if e["forecast"] or e["previous"]:
            line += f" | Prev: {e['forecast']} | Prec: {e['previous']}"
        lines.append(line)
    return "\n".join(lines)
