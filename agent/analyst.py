import json
import re
from agent.llm import call_llm
from agent.calendar_collector import format_calendar_for_prompt


def _extract_json(text):
    text = re.sub(r"```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```", "", text)
    start, end = text.find("{"), text.rfind("}")
    if start != -1 and end != -1:
        return json.loads(text[start : end + 1])
    raise ValueError("No JSON in response")


def analyze_calendar_event(event):
    has_actual = bool(event.get("actual"))
    currency = event.get("currency", "")
    ev = event.get("event", "")
    actual = event.get("actual", "N/A")
    forecast = event.get("forecast", "N/A")
    previous = event.get("previous", "N/A")

    system = "You are a financial analyst. Respond ONLY with valid JSON."
    if has_actual:
        prompt = f"""Analyze this economic RESULT and its market impact.
Event: {ev} ({currency})
Actual: {actual}
Forecast: {forecast}
Previous: {previous}

Return JSON with keys: impact_xauusd, impact_dxy, impact_eurusd, impact_btc, impact_nasdaq (each "bullish"/"bearish"/"neutral"), and raisonnement (1 sentence in French)."""
    else:
        prompt = f"""Analyze this UPCOMING economic event and predict market impact.
Event: {ev} ({currency})
Forecast: {forecast}
Previous: {previous}

Return JSON with keys: impact_xauusd, impact_dxy, impact_eurusd, impact_btc, impact_nasdaq (each "bullish"/"bearish"/"neutral"), and raisonnement (1 sentence in French)."""

    try:
        resp = call_llm(prompt, system, json_mode=True)
        return _extract_json(resp)
    except Exception:
        return {
            "impact_xauusd": "neutral",
            "impact_dxy": "neutral",
            "impact_eurusd": "neutral",
            "impact_btc": "neutral",
            "impact_nasdaq": "neutral",
            "raisonnement": "Analyse temporairement indisponible",
        }


def analyze_sentiment(news_item):
    title = news_item.get("title", "")
    summary = news_item.get("summary", "")[:300]
    system = "You are a financial analyst. Respond ONLY with valid JSON."
    prompt = f"""Analyze this financial news impact on markets.
Title: {title}
Summary: {summary}

Return JSON with keys: sentiment ("bullish"/"bearish"/"neutral"), impact_xauusd, impact_dxy, impact_eurusd, impact_btc, impact_nasdaq (each "bullish"/"bearish"/"neutral"), and explication (1 sentence in French)."""
    try:
        resp = call_llm(prompt, system, json_mode=True)
        return _extract_json(resp)
    except Exception:
        return {
            "sentiment": "neutral",
            "impact_xauusd": "neutral",
            "impact_dxy": "neutral",
            "impact_eurusd": "neutral",
            "impact_btc": "neutral",
            "impact_nasdaq": "neutral",
            "explication": "Analyse temporairement indisponible",
        }


def generate_daily_brief(news, prices, calendar_events=None):
    news_text = "\n".join([f"- {a['title']} ({a['source']})" for a in news[:15]])
    prices_text = "\n".join([f"{k}: {v['price']} ({v['change_1d']:+.2f}%)" for k, v in prices.items()])
    calendar_text = format_calendar_for_prompt(calendar_events or [], 15)

    prompt = f"""You are a financial analyst. Generate a daily macro-economic brief in French.

TODAY'S NEWS:
{news_text}

CURRENT PRICES:
{prices_text}

UPCOMING EVENTS:
{calendar_text}

Write a complete brief covering:
1. SUMMARY: 3-5 key events
2. MACRO ANALYSIS: rates, inflation, monetary policy
3. MARKET IMPACT: XAUUSD, DXY, EURUSD, BTCUSD, NASDAQ100
4. GLOBAL SENTIMENT: Bullish/Bearish/Neutral
5. CATALYSTS TO WATCH: next important events"""
    return call_llm(prompt, "Financial analyst writing in French. Clear, structured, professional.")


def chat_with_agent(question, news_context, prices_context, calendar_context=""):
    context = f"News:\n{news_context}\n\nPrices:\n{prices_context}\n\nCalendar:\n{calendar_context}"
    prompt = f"""Context:\n{context}\n\nQuestion: {question}\n\nAnswer in French with market analysis."""
    return call_llm(prompt, "Financial analyst. Precise, useful French answers about markets.")
