import json
from datetime import datetime
from agent.llm import call_llm
from agent.calendar_collector import format_calendar_for_prompt


def analyze_sentiment(news_item):
    prompt = f"""Analyse cet article financier et donne son impact probable sur les marchés (bullish/bearish/neutral) pour chaque actif (XAUUSD, DXY, EURUSD, BTCUSD, NASDAQ100).

Titre: {news_item['title']}
Résumé: {news_item['summary'][:300]}

Réponds UNIQUEMENT au format JSON:
{{"sentiment": "bullish|bearish|neutral", "impact_xauusd": "...", "impact_dxy": "...", "impact_eurusd": "...", "impact_btc": "...", "impact_nasdaq": "...", "explication": "..."}}"""
    resp = call_llm(prompt)
    try:
        start = resp.index("{")
        end = resp.rindex("}") + 1
        return json.loads(resp[start:end])
    except:
        return {"sentiment": "neutral", "impact_xauusd": "neutre", "impact_dxy": "neutre", "impact_eurusd": "neutre", "impact_btc": "neutre", "impact_nasdaq": "neutre", "explication": "Analyse non disponible"}


def generate_daily_brief(news, prices, calendar_events=None):
    news_text = "\n".join([f"- {a['title']} ({a['source']})" for a in news[:15]])
    prices_text = "\n".join([f"{k}: {v['price']} ({v['change_1d']:+.2f}%)" for k, v in prices.items()])
    calendar_text = format_calendar_for_prompt(calendar_events or [], 15)

    prompt = f"""Tu es un analyste financier. Voici les actualités et les prix du marché du jour.

ACTUALITÉS RÉCENTES:
{news_text}

PRIX ACTUELS:
{prices_text}

ÉVÉNEMENTS ÉCONOMIQUES À VENIR:
{calendar_text}

Génère un brief macro-économique complet en français avec:
1. RÉSUMÉ: Les 3-5 événements clés du jour
2. ANALYSE MACRO: Impact sur les taux, inflation, politique monétaire
3. IMPACT MARCHÉS: Pour chaque actif (XAUUSD, DXY, EURUSD, BTCUSD, NASDAQ100) - direction probable et pourquoi
4. SENTIMENT GLOBAL: Bullish / Bearish / Neutre avec justification
5. CATALYSEURS À SURVEILLER: Les prochains événements importants (calendrier économique)"""
    return call_llm(prompt, "Tu es un analyste financier expert. Réponds en français de manière claire et structurée.")


def chat_with_agent(question, news_context, prices_context, calendar_context=""):
    context = f"Actualités récentes:\n{news_context}\n\nPrix actuels:\n{prices_context}\n\nCalendrier économique:\n{calendar_context}"
    prompt = f"""Contexte marché:
{context}

Question: {question}

Réponds en français avec analyse et conseils."""
    return call_llm(prompt, "Tu es un analyste financier expert. Sois précis et utile.")
