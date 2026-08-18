"""Anthropic Messages API."""
from anthropic import Anthropic

DEFAULT_BASE = "https://api.anthropic.com"
KEY_ENV = "ANTHROPIC_API_KEY"

def call(api_key, model_id, messages, base_url=None, temperature=None, timeout=60, max_tokens=2048):
    client = Anthropic(api_key=api_key, base_url=base_url or DEFAULT_BASE, timeout=timeout)
    kw = {"model": model_id, "messages": messages, "max_tokens": max_tokens}
    if temperature is not None:
        kw["temperature"] = temperature
    resp = client.messages.create(**kw)
    return "\n".join(b.text for b in resp.content if getattr(b, "text", None)).strip()
