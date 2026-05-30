"""LLM Provider管理器"""

import asyncio
from typing import Any, Dict, List, Optional

from .provider import LLMProvider
from .rate_limiter import rate_limiter_manager


class ProviderManager:
    """Provider管理器"""

    def __init__(self):
        self._providers: Dict[str, LLMProvider] = {}
        self._configs: Dict[str, Dict[str, Any]] = {}

    def register(self, name: str, provider: LLMProvider, config: Optional[Dict[str, Any]] = None) -> None:
        """
        注册Provider

        Args:
            name: Provider名称
            provider: Provider实例
            config: Provider配置
        """
        self._providers[name] = provider
        self._configs[name] = config or {}

    def get(self, name: str) -> Optional[LLMProvider]:
        """获取Provider"""
        return self._providers.get(name)

    def get_config(self, name: str) -> Dict[str, Any]:
        """获取Provider配置"""
        return self._configs.get(name, {})

    def list_providers(self) -> List[str]:
        """列出所有Provider"""
        return list(self._providers.keys())

    def has_provider(self, name: str) -> bool:
        """检查Provider是否存在"""
        return name in self._providers

    async def get_response(
        self,
        provider_name: str,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2048,
        json_mode: bool = False,
        **kwargs: Any,
    ) -> str:
        """
        获取LLM响应（带限流和重试）

        Args:
            provider_name: Provider名称
            model: 模型名称
            messages: 消息列表
            temperature: 温度参数
            max_tokens: 最大token数
            json_mode: 是否返回JSON
            **kwargs: 其他参数

        Returns:
            响应内容
        """
        provider = self.get(provider_name)
        if not provider:
            raise ValueError(f"Provider '{provider_name}' not found")

        # 限流
        bucket_name = provider_name.lower()
        if bucket_name in rate_limiter_manager._buckets:
            await rate_limiter_manager.acquire(bucket_name)

        # 重试机制
        max_retries = 3
        last_error = None

        for attempt in range(max_retries):
            try:
                if json_mode:
                    result = await provider.chat_json(
                        messages, model, temperature, max_tokens, **kwargs
                    )
                    import json
                    return json.dumps(result, ensure_ascii=False)
                else:
                    return await provider.chat(
                        messages, model, temperature, max_tokens, **kwargs
                    )
            except Exception as e:
                last_error = e
                if attempt < max_retries - 1:
                    # 指数退避
                    wait_time = 2 ** attempt
                    await asyncio.sleep(wait_time)

        raise last_error  # type: ignore

    async def get_json_response(
        self,
        provider_name: str,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2048,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        获取JSON响应

        Args:
            provider_name: Provider名称
            model: 模型名称
            messages: 消息列表
            temperature: 温度参数
            max_tokens: 最大token数
            **kwargs: 其他参数

        Returns:
            JSON响应
        """
        provider = self.get(provider_name)
        if not provider:
            raise ValueError(f"Provider '{provider_name}' not found")

        # 限流
        bucket_name = provider_name.lower()
        if bucket_name in rate_limiter_manager._buckets:
            await rate_limiter_manager.acquire(bucket_name)

        # 重试机制
        max_retries = 3
        last_error = None

        for attempt in range(max_retries):
            try:
                return await provider.chat_json(
                    messages, model, temperature, max_tokens, **kwargs
                )
            except Exception as e:
                last_error = e
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt
                    await asyncio.sleep(wait_time)

        raise last_error  # type: ignore


# 全局Provider管理器实例
provider_manager = ProviderManager()
