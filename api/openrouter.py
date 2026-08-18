"""OpenRouter (OpenAI-compatible)."""
import json
import urllib.request

DEFAULT_BASE = "https://openrouter.ai/api/v1"
KEY_ENV = "OPENROUTER_API_KEY"

def call(api_key, model_id, messages, base_url=None, temperature=None, timeout=60):
    base = (base_url or DEFAULT_BASE).rstrip("/")
    url = f"{base}/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    body = {"model": model_id, "messages": messages}
    if temperature is not None:
        body["temperature"] = temperature
    req = urllib.request.Request(url, data=json.dumps(body).encode(), headers=headers)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        d = json.loads(r.read())
    return (d.get("choices") or [{}])[0].get("message", {}).get("content", "").strip()
