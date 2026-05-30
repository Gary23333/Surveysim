"""OpenAI适配器"""

import json
from typing import Any, AsyncGenerator, Dict, List, Optional

import httpx

from ..provider import LLMProvider


class OpenAIProvider(LLMProvider):
    """OpenAI Provider — 兼容 OpenAI / MiMo / DeepSeek / 豆包 等"""

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.openai.com/v1",
        timeout: float = 60.0,
        auth_header: str = "Authorization",
    ):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.auth_header = auth_header
        self._client: Optional[httpx.AsyncClient] = None

    @property
    def client(self) -> httpx.AsyncClient:
        if self._client is None:
            headers = {
                "Content-Type": "application/json",
            }
            if self.auth_header == "api-key":
                headers["api-key"] = self.api_key
            else:
                headers["Authorization"] = f"Bearer {self.api_key}"

            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=self.timeout,
                headers=headers,
            )
        return self._client

    async def close(self) -> None:
        if self._client:
            await self._client.aclose()
            self._client = None

    async def chat(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        thinking_enabled: bool = False,
        thinking_intensity: str = "medium",
        max_tokens_param: str = "max_tokens",
        thinking_config: Any = None,
        **kwargs: Any,
    ) -> str:
        payload = self._build_payload(
            messages, model, temperature, max_tokens,
            thinking_enabled, thinking_intensity,
            max_tokens_param, thinking_config, **kwargs
        )

        response = await self.client.post("/chat/completions", json=payload)
        response.raise_for_status()

        data = response.json()
        return data["choices"][0]["message"]["content"]

    async def chat_json(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        thinking_enabled: bool = False,
        thinking_intensity: str = "medium",
        max_tokens_param: str = "max_tokens",
        thinking_config: Any = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        json_instruction = "\n\n请以JSON格式输出，确保输出是有效的JSON。"
        if messages and messages[-1]["role"] == "user":
            messages = messages.copy()
            messages[-1] = {
                "role": "user",
                "content": messages[-1]["content"] + json_instruction,
            }

        payload = self._build_payload(
            messages, model, temperature, max_tokens,
            thinking_enabled, thinking_intensity,
            max_tokens_param, thinking_config,
            response_format={"type": "json_object"},
            **kwargs
        )

        response = await self.client.post("/chat/completions", json=payload)
        response.raise_for_status()

        data = response.json()
        content = data["choices"][0]["message"]["content"]

        try:
            return json.loads(content)
        except json.JSONDecodeError:
            return self._extract_json(content)

    async def stream_chat(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        thinking_enabled: bool = False,
        thinking_intensity: str = "medium",
        max_tokens_param: str = "max_tokens",
        thinking_config: Any = None,
        **kwargs: Any,
    ) -> AsyncGenerator[str, None]:
        payload = self._build_payload(
            messages, model, temperature, max_tokens,
            thinking_enabled, thinking_intensity,
            max_tokens_param, thinking_config,
            stream=True,
            **kwargs
        )

        async with self.client.stream("POST", "/chat/completions", json=payload) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    data = line[6:]
                    if data.strip() == "[DONE]":
                        break
                    try:
                        chunk = json.loads(data)
                        delta = chunk["choices"][0].get("delta", {})
                        content = delta.get("content", "")
                        if content:
                            yield content
                    except json.JSONDecodeError:
                        continue

    def _build_payload(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float,
        max_tokens: int,
        thinking_enabled: bool,
        thinking_intensity: str,
        max_tokens_param: str,
        thinking_config: Any,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            max_tokens_param: max_tokens,
            **kwargs,
        }

        if thinking_config is not None and hasattr(thinking_config, 'build_thinking_payload'):
            thinking_params = thinking_config.build_thinking_payload(thinking_enabled, thinking_intensity)
            payload.update(thinking_params)

            if hasattr(thinking_config, 'apply_restrictions'):
                thinking_config.apply_restrictions(payload, thinking_enabled)

        return payload

    def _extract_json(self, text: str) -> Dict[str, Any]:
        import re
        json_pattern = r"```json\s*([\s\S]*?)\s*```"
        match = re.search(json_pattern, text)
        if match:
            return json.loads(match.group(1))
        brace_pattern = r"\{[\s\S]*\}"
        match = re.search(brace_pattern, text)
        if match:
            return json.loads(match.group(0))
        raise ValueError(f"无法从文本中提取JSON: {text[:100]}...")
