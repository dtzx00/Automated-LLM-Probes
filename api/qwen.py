"""Qwen / DashScope (OpenAI-compatible)."""
from openai import OpenAI

DEFAULT_BASE = "https://dashscope.aliyuncs.com/compatible-mode/v1"
KEY_ENV = "QWEN_API_KEY"

def call(api_key, model_id, messages, base_url=None, temperature=None, timeout=60):
    client = OpenAI(api_key=api_key, base_url=base_url or DEFAULT_BASE, timeout=timeout)
    kw = {"model": model_id, "messages": messages}
    if temperature is not None:
        kw["temperature"] = temperature
    resp = client.chat.completions.create(**kw)
    return (resp.choices[0].message.content or "").strip()
