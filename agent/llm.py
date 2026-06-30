import json
import requests
from config import (
    LLM_PROVIDER,
    OLLAMA_URL,
    OLLAMA_MODEL,
    GROQ_API_KEY,
    GROQ_MODEL,
)


def _call_ollama(prompt, system):
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "system": system or "Tu es un analyste financier expert en macro-economie et trading.",
        "stream": False,
        "options": {"temperature": 0.3, "num_predict": 1024},
    }
    resp = requests.post(f"{OLLAMA_URL}/api/generate", json=payload, timeout=120)
    if resp.status_code == 200:
        return resp.json().get("response", "")
    return ""


def _call_groq(prompt, system):
    if not GROQ_API_KEY:
        return ""
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": GROQ_MODEL,
        "messages": [
            {"role": "system", "content": system or "Tu es un analyste financier expert en macro-economie et trading."},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.3,
        "max_tokens": 1024,
    }
    resp = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers=headers,
        json=payload,
        timeout=120,
    )
    if resp.status_code == 200:
        return resp.json()["choices"][0]["message"]["content"]
    return ""


def call_llm(prompt, system=""):
    if LLM_PROVIDER == "groq":
        return _call_groq(prompt, system)
    return _call_ollama(prompt, system)
