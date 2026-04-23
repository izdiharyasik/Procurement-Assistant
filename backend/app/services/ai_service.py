from __future__ import annotations

import json
from typing import Iterable

import httpx
from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_exponential

from app.config import Settings
from app.services.document_service import Segment

TRANSLATION_SYSTEM_PROMPT = (
    "You are a professional legal translator. Translate the following text into formal, precise "
    "English suitable for contracts. Preserve structure, numbering, and defined terms consistently. "
    "Do not summarize or omit anything. Maintain legal tone and clarity."
)

REVIEW_SYSTEM_PROMPT = """You are a senior procurement auditor and legal-commercial reviewer.
Produce output with sections:
1) EXECUTIVE SUMMARY (5-7 findings, overall risk level, key recommendation)
2) DETAILED FINDINGS (Issue Title, Category, Problem, Risk Impact, Recommendation)
3) REDLINE SUGGESTIONS
4) PROCUREMENT STRATEGY INSIGHTS
Be direct, specific, and practical."""


class AIService:
    def __init__(self) -> None:
        self.settings = Settings()
        self.provider = self.settings.ai_provider.lower()
        self.client = (
            OpenAI(api_key=self.settings.openai_api_key)
            if self.provider == "openai" and self.settings.openai_api_key
            else None
        )

    @retry(wait=wait_exponential(min=1, max=20), stop=stop_after_attempt(5))
    def _chat(self, system: str, user: str) -> str:
        if self.provider == "openai":
            if not self.client:
                raise RuntimeError("OPENAI_API_KEY is not set. Set AI_PROVIDER=ollama for local free inference.")

            response = self.client.chat.completions.create(
                model=self.settings.openai_model,
                temperature=0.1,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
            )
            return response.choices[0].message.content or ""

        if self.provider == "ollama":
            payload = {
                "model": self.settings.ollama_model,
                "stream": False,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
            }
            with httpx.Client(timeout=120) as client:
                response = client.post(f"{self.settings.ollama_base_url}/api/chat", json=payload)
                response.raise_for_status()
                data = response.json()
                return data.get("message", {}).get("content", "")

        raise RuntimeError("Unsupported AI_PROVIDER. Use 'openai' or 'ollama'.")

    def translate_chunk(self, segments: Iterable[Segment], term_memory: dict[str, str]) -> dict[int, str]:
        payload = {
            "term_memory": term_memory,
            "segments": [{"id": s.index, "text": s.original} for s in segments],
            "instructions": "Return strict JSON object: {translations:[{id:number, translated:string}], term_memory_updates:{}}",
        }
        raw = self._chat(TRANSLATION_SYSTEM_PROMPT, json.dumps(payload, ensure_ascii=False))
        parsed = _extract_json(raw)
        translations = {
            int(item["id"]): item["translated"].strip()
            for item in parsed.get("translations", [])
            if str(item.get("id", "")).isdigit()
        }

        if not translations and self.provider == "ollama":
            # fallback when model fails to produce strict JSON
            translations = {s.index: s.original for s in segments}

        term_memory.update(parsed.get("term_memory_updates", {}))
        return translations

    def review_document(self, original_text: str, translated_text: str | None = None) -> str:
        content = f"Original text:\n{original_text}\n\n"
        if translated_text:
            content += f"English translation:\n{translated_text}\n\n"
        content += "Generate the full structured review report now."
        return self._chat(REVIEW_SYSTEM_PROMPT, content)


def _extract_json(raw: str) -> dict:
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[-1]
        raw = raw.rsplit("```", 1)[0]
    start = raw.find("{")
    end = raw.rfind("}")
    if start == -1 or end == -1:
        return {"translations": []}
    try:
        return json.loads(raw[start : end + 1])
    except json.JSONDecodeError:
        return {"translations": []}

ai_service = AIService()
