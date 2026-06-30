import requests
from config import LLM_PROVIDER, OLLAMA_URL, OLLAMA_MODEL, GROQ_API_KEY, GROQ_MODEL


def _call_ollama(prompt, system):
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "system": system or "",
        "stream": False,
        "options": {"temperature": 0.2, "num_predict": 1024},
    }
    try:
        resp = requests.post(f"{OLLAMA_URL}/api/generate", json=payload, timeout=120)
        if resp.status_code == 200:
            return resp.json().get("response", "")
    except:
        pass
    return ""


def _call_groq(prompt, system, json_mode=False):
    if not GROQ_API_KEY:
        return ""
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }
    msgs = []
    if system:
        msgs.append({"role": "system", "content": system})
    msgs.append({"role": "user", "content": prompt})
    payload = {
        "model": GROQ_MODEL,
        "messages": msgs,
        "temperature": 0.15,
        "max_tokens": 2048,
    }
    if json_mode:
        payload["response_format"] = {"type": "json_object"}
    try:
        resp = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=120,
        )
        if resp.status_code == 200:
            return resp.json()["choices"][0]["message"]["content"]
    except:
        pass
    return ""


def call_llm(prompt, system="", json_mode=False):
    if LLM_PROVIDER == "groq":
        return _call_groq(prompt, system, json_mode)
    return _call_ollama(prompt, system)
