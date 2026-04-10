from __future__ import annotations

import anthropic
from tenacity import retry, stop_after_attempt, wait_exponential
from config import get_settings

_client: anthropic.AsyncAnthropic | None = None


def _get_client() -> anthropic.AsyncAnthropic:
    global _client
    if _client is None:
        settings = get_settings()
        _client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)
    return _client


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
async def generate_response(
    system_prompt: str,
    messages: list[dict],  # [{"role": "user"|"assistant", "content": str}]
) -> str:
    """Send a conversation to Claude and return the response text."""
    settings = get_settings()
    client = _get_client()

    response = await client.messages.create(
        model=settings.claude_model,
        max_tokens=1024,
        temperature=0.3,
        system=system_prompt,
        messages=messages,
    )

    return response.content[0].text
