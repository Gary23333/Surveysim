"""ProviderPack配置管理"""

import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from ..config import settings


class ModelInfo:
    """模型信息"""

    def __init__(self, id: str, name: str, max_tokens: int = 4096,
                 supports_thinking: bool = False, default_thinking: bool = False):
        self.id = id
        self.name = name
        self.max_tokens = max_tokens
        self.supports_thinking = supports_thinking
        self.default_thinking = default_thinking

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "max_tokens": self.max_tokens,
            "supports_thinking": self.supports_thinking,
            "default_thinking": self.default_thinking,
        }


class ThinkingConfig:
    """思考模式配置"""

    def __init__(
        self,
        mode: str = "none",
        toggle_key: Optional[str] = None,
        toggle_value: Optional[str] = None,
        effort_key: Optional[str] = None,
        effort_values: Optional[List[str]] = None,
        effort_off_value: Optional[str] = None,
        restrictions: Optional[Dict[str, Any]] = None,
    ):
        self.mode = mode  # "toggle" | "effort" | "effort_only" | "none"
        self.toggle_key = toggle_key
        self.toggle_value = toggle_value
        self.effort_key = effort_key
        self.effort_values = effort_values or []
        self.effort_off_value = effort_off_value
        self.restrictions = restrictions or {}

    def build_thinking_payload(self, thinking_enabled: bool, intensity: str = "medium") -> Dict[str, Any]:
        """构建思考模式相关的API payload参数"""
        params = {}

        if self.mode == "toggle":
            if thinking_enabled and self.toggle_key and self.toggle_value:
                self._set_nested(params, self.toggle_key, self.toggle_value)
        elif self.mode == "effort":
            if thinking_enabled:
                if self.toggle_key and self.toggle_value:
                    self._set_nested(params, self.toggle_key, self.toggle_value)
                if self.effort_key:
                    params[self.effort_key] = intensity
        elif self.mode == "effort_only":
            if thinking_enabled and self.effort_key:
                params[self.effort_key] = intensity
            elif not thinking_enabled and self.effort_off_value and self.effort_key:
                params[self.effort_key] = self.effort_off_value

        return params

    def apply_restrictions(self, payload: Dict[str, Any], thinking_enabled: bool) -> None:
        """应用思考模式下的参数限制"""
        if not thinking_enabled:
            return
        for key, restriction in self.restrictions.items():
            if isinstance(restriction, dict):
                if restriction.get("disabled"):
                    payload.pop(key, None)
                elif "override" in restriction:
                    payload[key] = restriction["override"]

    @staticmethod
    def _set_nested(d: Dict, path: str, value: Any) -> None:
        """设置嵌套字典值，如 'thinking.type' -> d['thinking']['type'] = value"""
        keys = path.split(".")
        for key in keys[:-1]:
            if key not in d:
                d[key] = {}
            d = d[key]
        d[keys[-1]] = value

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]]) -> "ThinkingConfig":
        if not data:
            return cls(mode="none")
        return cls(
            mode=data.get("mode", "none"),
            toggle_key=data.get("toggle_key"),
            toggle_value=data.get("toggle_value"),
            effort_key=data.get("effort_key"),
            effort_values=data.get("effort_values", []),
            effort_off_value=data.get("effort_off_value"),
            restrictions=data.get("restrictions", {}),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "mode": self.mode,
            "toggle_key": self.toggle_key,
            "toggle_value": self.toggle_value,
            "effort_key": self.effort_key,
            "effort_values": self.effort_values,
            "effort_off_value": self.effort_off_value,
            "restrictions": self.restrictions,
        }


class ProviderPack:
    """Provider配置包"""

    def __init__(
        self,
        name: str,
        base_url: str,
        api_key: str,
        default_model: str,
        models: List[ModelInfo],
        api_params: Optional[Dict[str, Any]] = None,
        thinking_config: Optional[ThinkingConfig] = None,
    ):
        self.name = name
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.default_model = default_model
        self.models = models
        self.api_params = api_params or {}
        self.thinking_config = thinking_config or ThinkingConfig()

    @property
    def max_tokens_param(self) -> str:
        return self.api_params.get("max_tokens_param", "max_tokens")

    @property
    def auth_header(self) -> str:
        return self.api_params.get("auth_header", "Authorization")

    def get_model(self, model_id: str) -> Optional[ModelInfo]:
        for model in self.models:
            if model.id == model_id:
                return model
        return None

    def get_model_ids(self) -> List[str]:
        return [model.id for model in self.models]

    def get_max_tokens(self, model_id: str) -> int:
        model = self.get_model(model_id)
        return model.max_tokens if model else 4096

    def build_thinking_payload(self, thinking_enabled: bool, intensity: str = "medium") -> Dict[str, Any]:
        return self.thinking_config.build_thinking_payload(thinking_enabled, intensity)

    def apply_thinking_restrictions(self, payload: Dict[str, Any], thinking_enabled: bool) -> None:
        self.thinking_config.apply_restrictions(payload, thinking_enabled)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "base_url": self.base_url,
            "api_key": "***" if self.api_key else None,
            "default_model": self.default_model,
            "models": [model.to_dict() for model in self.models],
            "api_params": self.api_params,
            "thinking_config": self.thinking_config.to_dict(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ProviderPack":
        api_key = data.get("api_key", "")
        api_key = cls._resolve_env_vars(api_key)

        models = []
        for model_data in data.get("models", []):
            models.append(ModelInfo(
                id=model_data["id"],
                name=model_data.get("name", model_data["id"]),
                max_tokens=model_data.get("max_tokens", 4096),
                supports_thinking=model_data.get("supports_thinking", False),
                default_thinking=model_data.get("default_thinking", False),
            ))

        thinking_config = ThinkingConfig.from_dict(data.get("thinking_config"))

        return cls(
            name=data["name"],
            base_url=data.get("base_url", ""),
            api_key=api_key,
            default_model=data.get("default_model", ""),
            models=models,
            api_params=data.get("api_params", {}),
            thinking_config=thinking_config,
        )

    @staticmethod
    def _resolve_env_vars(value: str) -> str:
        pattern = r"\$\{(\w+)\}"
        matches = re.findall(pattern, value)
        for match in matches:
            env_value = os.environ.get(match, "")
            value = value.replace(f"${{{match}}}", env_value)
        return value


class ProviderPackManager:
    """ProviderPack管理器"""

    def __init__(self, config_dir: Optional[Path] = None):
        self.config_dir = config_dir or settings.get_providers_dir()
        self._packs: Dict[str, ProviderPack] = {}

    def load_packs(self) -> None:
        if not self.config_dir.exists():
            return
        for file_path in self.config_dir.glob("*.yaml"):
            try:
                pack = self._load_pack(file_path)
                if pack:
                    self._packs[pack.name] = pack
            except Exception as e:
                print(f"Failed to load provider pack {file_path}: {e}")

    def _load_pack(self, file_path: Path) -> Optional[ProviderPack]:
        with open(file_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        if not data:
            return None
        return ProviderPack.from_dict(data)

    def get_pack(self, name: str) -> Optional[ProviderPack]:
        return self._packs.get(name)

    def list_packs(self) -> List[str]:
        return list(self._packs.keys())

    def add_pack(self, pack: ProviderPack) -> None:
        self._packs[pack.name] = pack

    def remove_pack(self, name: str) -> bool:
        if name in self._packs:
            del self._packs[name]
            return True
        return False

    def save_pack(self, pack: ProviderPack) -> None:
        self.config_dir.mkdir(parents=True, exist_ok=True)
        file_path = self.config_dir / f"{pack.name.lower().replace(' ', '_')}.yaml"
        data = {
            "name": pack.name,
            "base_url": pack.base_url,
            "api_key": pack.api_key,
            "default_model": pack.default_model,
            "models": [model.to_dict() for model in pack.models],
            "api_params": pack.api_params,
            "thinking_config": pack.thinking_config.to_dict(),
        }
        with open(file_path, "w", encoding="utf-8") as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)


pack_manager = ProviderPackManager()
