from __future__ import annotations
import json
import requests
from config import Config


class LLMClient:
    """Unified LLM client supporting Ollama (local) and OpenAI-compatible API."""

    def __init__(self, backend: str | None = None):
        self.backend = backend or Config.LLM_BACKEND

    def chat(self, system_prompt: str, user_prompt: str, temperature: float = 0.1) -> str:
        if self.backend == "ollama":
            return self._chat_ollama(system_prompt, user_prompt, temperature)
        elif self.backend == "openai":
            return self._chat_openai(system_prompt, user_prompt, temperature)
        else:
            raise ValueError(f"Unknown LLM backend: {self.backend}")

    def _chat_ollama(self, system_prompt: str, user_prompt: str, temperature: float) -> str:
        url = f"{Config.OLLAMA_HOST}/api/chat"
        payload = {
            "model": Config.OLLAMA_MODEL,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "stream": False,
            "options": {"temperature": temperature},
        }
        resp = requests.post(url, json=payload, timeout=300)
        resp.raise_for_status()
        data = resp.json()
        return data["message"]["content"]

    def _chat_openai(self, system_prompt: str, user_prompt: str, temperature: float) -> str:
        url = f"{Config.OPENAI_BASE_URL}/chat/completions"
        headers = {
            "Authorization": f"Bearer {Config.OPENAI_API_KEY}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": Config.OPENAI_MODEL,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": temperature,
        }
        resp = requests.post(url, json=payload, headers=headers, timeout=300)
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"]
