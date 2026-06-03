"""LM Studio OpenAI-compatible API helper。

当前只保留原有 helper，方便后续需要模型端摘要或解释时复用。
"""


class LMStudioClient:
    """Minimal helper for interacting with LM Studio's OpenAI-compatible API."""

    def __init__(self, config: dict) -> None:
        lm_cfg = config.get("lmstudio", {})
        self.base_url: str = lm_cfg.get("base_url", "http://localhost:1234/v1")
        self.model: str = lm_cfg.get("model", "local-model")
        self.timeout: int = lm_cfg.get("timeout", 120)

    async def chat_completion(self, messages: list[dict], temperature: float = 0.7) -> str:
        """Send a chat completion request and return the assistant message text."""
        try:
            import aiohttp
        except ImportError:
            return "aiohttp is not installed – cannot reach LM Studio."

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
        }
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/chat/completions",
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=self.timeout),
                ) as resp:
                    data = await resp.json()
                    return data["choices"][0]["message"]["content"]
        except Exception as exc:
            return f"LM Studio request failed: {exc}"
