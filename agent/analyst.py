import json
import re
from datetime import datetime
from agent.llm import call_llm
from agent.calendar_collector import format_calendar_for_prompt


def _extract_json(text):
    text = re.sub(r"```json\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"```\s*", "", text)
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1:
        return json.loads(text[start:end+1])
    raise ValueError("No JSON found")


def _neutral_analysis():
    return {"impact_xauusd": "neutral", "impact_dxy": "neutral", "impact_eurusd": "neutral", "impact_btc": "neutral", "impact_nasdaq": "neutral", "raisonnement": "Analyse non disponible"}


def analyze_sentiment(news_item):
    prompt = f"""Analyse cet article financier.

Titre: {news_item['title']}
Resume: {news_item['summary'][:300]}

Reponds UNIQUEMENT ce JSON (pas d'autre texte):
{{"sentiment":"bullish|bearish|neutral","impact_xauusd":"bullish|bearish|neutral","impact_dxy":"bullish|bearish|neutral","impact_eurusd":"bullish|bearish|neutral","impact_btc":"bullish|bearish|neutral","impact_nasdaq":"bullish|bearish|neutral","explication":"..."}}"""
    try:
        resp = call_llm(prompt)
        return _extract_json(resp)
    except:
        return {"sentiment": "neutral", "impact_xauusd": "neutral", "impact_dxy": "neutral", "impact_eurusd": "neutral", "impact_btc": "neutral", "impact_nasdaq": "neutral", "explication": "Analyse non disponible"}


def analyze_calendar_event(event):
    has_actual = bool(event.get("actual"))
    if not has_actual:
        prompt = f"""Tu es un analyste financier. Donne TON analyse de cet evenement A VENIR.

Evenement: {event.get('event', '')}
Devise: {event.get('currency', '')}
Date: {event.get('day', '')} {event.get('time', '')}
Prevision: {event.get('forecast', 'N/A')}
Precedent: {event.get('previous', 'N/A')}

Quel est l'impact PREVU sur les marches ?

Reponds UNIQUEMENT ce JSON:
{{"impact_xauusd":"bullish|bearish|neutral","impact_dxy":"bullish|bearish|neutral","impact_eurusd":"bullish|bearish|neutral","impact_btc":"bullish|bearish|neutral","impact_nasdaq":"bullish|bearish|neutral","raisonnement":"impact預測 en 1 phrase"}}"""
    else:
        prompt = f"""Tu es un analyste financier. Analyse ce RESULTAT economique.

Evenement: {event.get('event', '')}
Devise: {event.get('currency', '')}
Resultat: {event.get('actual', 'N/A')} (vs prevision: {event.get('forecast', 'N/A')})
Precedent: {event.get('previous', 'N/A')}

Quel est l'impact de ce resultat sur les marches ?

Reponds UNIQUEMENT ce JSON:
{{"impact_xauusd":"bullish|bearish|neutral","impact_dxy":"bullish|bearish|neutral","impact_eurusd":"bullish|bearish|neutral","impact_btc":"bullish|bearish|neutral","impact_nasdaq":"bullish|bearish|neutral","raisonnement":"impact en 1 phrase"}}"""
    try:
        resp = call_llm(prompt, "Tu es un analyste. Reponds UNIQUEMENT en JSON valide, sans texte autour.")
        return _extract_json(resp)
    except Exception:
        return _neutral_analysis()


def generate_daily_brief(news, prices, calendar_events=None):
    news_text = "\n".join([f"- {a['title']} ({a['source']})" for a in news[:15]])
    prices_text = "\n".join([f"{k}: {v['price']} ({v['change_1d']:+.2f}%)" for k, v in prices.items()])
    calendar_text = format_calendar_for_prompt(calendar_events or [], 15)

    prompt = f"""Tu es un analyste financier. Voici les actualites et les prix du marche du jour.

ACTUALITES RECENTES:
{news_text}

PRIX ACTUELS:
{prices_text}

EVENEMENTS ECONOMIQUES A VENIR:
{calendar_text}

Genere un brief macro-economique complet en francais avec:
1. RESUME: Les 3-5 evenements cles du jour
2. ANALYSE MACRO: Impact sur les taux, inflation, politique monetaire
3. IMPACT MARCHES: Pour chaque actif (XAUUSD, DXY, EURUSD, BTCUSD, NASDAQ100) - direction probable et pourquoi
4. SENTIMENT GLOBAL: Bullish / Bearish / Neutre avec justification
5. CATALYSEURS A SURVEILLER: Les prochains evenements importants (calendrier economique)"""
    return call_llm(prompt, "Tu es un analyste financier expert. Reponds en francais de maniere claire et structuree.")


def chat_with_agent(question, news_context, prices_context, calendar_context=""):
    context = f"Actualites recentes:\n{news_context}\n\nPrix actuels:\n{prices_context}\n\nCalendrier economique:\n{calendar_context}"
    prompt = f"""Contexte marche:
{context}

Question: {question}

Reponds en francais avec analyse et conseils."""
    return call_llm(prompt, "Tu es un analyste financier expert. Sois precis et utile.")
