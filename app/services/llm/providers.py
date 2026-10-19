import json
from dataclasses import dataclass
from typing import Protocol

import httpx

from app.core.config import Settings
from app.core.errors import AppError
from app.modules.knowledge.schemas import SearchHit


class LLMProvider(Protocol):
    name: str

    def analyze(self, question: str, contexts: list[SearchHit]) -> dict[str, object]: ...


class MockLLMProvider:
    name = "mock"

    def analyze(self, question: str, contexts: list[SearchHit]) -> dict[str, object]:
        if contexts:
            sources = ", ".join(hit.citation for hit in contexts[:3])
            answer = (
                "Demo mode generated a grounded response from the retrieved public knowledge. "
                f"Review the cited material before taking action: {sources}."
            )
            recommendations = [
                "Inspect the cited procedure and verify the observed condition.",
                "Record the finding in the maintenance workflow before replacing components.",
            ]
        else:
            answer = "Demo mode found no supporting knowledge for this question."
            recommendations = ["Add an authorized technical document and search again."]
        return {
            "answer": answer,
            "risk_level": "unknown",
            "recommendations": recommendations,
        }


@dataclass
class OpenAICompatibleProvider:
    name: str
    base_url: str
    model: str
    api_key: str = ""
    timeout_seconds: float = 30.0

    def analyze(self, question: str, contexts: list[SearchHit]) -> dict[str, object]:
        context_text = "\n\n".join(f"{hit.citation} {hit.content}" for hit in contexts)
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        payload = {
            "model": self.model,
            "temperature": 0,
            "response_format": {"type": "json_object"},
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "Return JSON with answer, risk_level, and recommendations. "
                        "Use only supplied context and do not issue physical control commands."
                    ),
                },
                {"role": "user", "content": f"Question: {question}\nContext:\n{context_text}"},
            ],
        }
        try:
            with httpx.Client(timeout=self.timeout_seconds) as client:
                response = client.post(
                    f"{self.base_url.rstrip('/')}/chat/completions", json=payload, headers=headers
                )
                response.raise_for_status()
                content = response.json()["choices"][0]["message"]["content"]
                result = json.loads(content)
        except (httpx.HTTPError, KeyError, TypeError, json.JSONDecodeError) as exc:
            raise AppError(
                503, "llm_provider_unavailable", "The configured LLM provider failed"
            ) from exc
        if not all(key in result for key in ("answer", "risk_level", "recommendations")):
            raise AppError(502, "llm_response_invalid", "The LLM response did not match the schema")
        return result


def build_provider(settings: Settings) -> LLMProvider:
    if settings.llm_provider == "mock":
        return MockLLMProvider()
    if settings.llm_provider == "deepseek":
        return OpenAICompatibleProvider(
            "deepseek",
            f"{settings.deepseek_base_url.rstrip('/')}/v1",
            "deepseek-chat",
            settings.deepseek_api_key,
        )
    if settings.llm_provider == "ollama":
        return OpenAICompatibleProvider(
            "ollama", f"{settings.ollama_base_url.rstrip('/')}/v1", "configured-local-model"
        )
    return OpenAICompatibleProvider("vllm", settings.vllm_base_url, "configured-served-model")
