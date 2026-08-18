"""Anthropic Messages API."""
import json
import urllib.request

DEFAULT_BASE = "https://api.anthropic.com/v1"
KEY_ENV = "ANTHROPIC_API_KEY"

def call(api_key, model_id, messages, base_url=None, temperature=None, timeout=60, max_tokens=2048):
    base = (base_url or DEFAULT_BASE).rstrip("/")
    url = f"{base}/messages"
    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "Content-Type": "application/json",
    }
    body = {"model": model_id, "messages": messages, "max_tokens": max_tokens}
    if temperature is not None:
        body["temperature"] = temperature
    req = urllib.request.Request(url, data=json.dumps(body).encode(), headers=headers)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        d = json.loads(r.read())
    return "\n".join(b.get("text", "") for b in d.get("content", []) if b.get("type") == "text").strip()
