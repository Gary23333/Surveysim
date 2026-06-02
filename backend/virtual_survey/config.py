"""配置管理"""

import os
from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """应用配置"""

    # 服务配置
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True

    # 数据库配置
    DATABASE_URL: str = "sqlite:///./data/surveysim.db"

    # LLM配置（供应商 API Key）
    MIMO_API_KEY: Optional[str] = None
    DEEPSEEK_API_KEY: Optional[str] = None
    VOLCENGINE_API_KEY: Optional[str] = None

    # 路径配置
    BASE_DIR: Path = Path(__file__).parent.parent
    CONFIGS_DIR: Path = BASE_DIR / "configs"
    DATA_DIR: Path = BASE_DIR / "data"

    # 模型配置
    DEFAULT_MODEL: str = "gpt-4o-mini"
    DEFAULT_TEMPERATURE: float = 0.7
    DEFAULT_MAX_TOKENS: int = 2048

    # 会话配置
    MAX_AGENTS: int = 15
    MAX_QUESTIONS: int = 50
    MAX_CONVERSATION_HISTORY: int = 50

    # WebSocket配置
    WS_HEARTBEAT_INTERVAL: int = 30

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

    def get_configs_dir(self) -> Path:
        """获取配置目录"""
        return self.CONFIGS_DIR

    def get_providers_dir(self) -> Path:
        """获取Provider配置目录"""
        return self.CONFIGS_DIR / "providers"

    def get_personas_dir(self) -> Path:
        """获取Persona配置目录"""
        return self.CONFIGS_DIR / "personas"

    def get_surveys_dir(self) -> Path:
        """获取问卷配置目录"""
        return self.CONFIGS_DIR / "surveys"

    def get_behavior_prompts_dir(self) -> Path:
        """获取行为提示词配置目录"""
        return self.CONFIGS_DIR / "behavior_prompts"

    def get_scenarios_dir(self) -> Path:
        """获取场景配置目录"""
        return self.CONFIGS_DIR / "scenarios"

    def get_templates_dir(self, config_type: str) -> Path:
        """获取模板目录"""
        return self.CONFIGS_DIR / config_type / "templates"

    def ensure_dirs(self) -> None:
        """确保所有目录存在"""
        self.DATA_DIR.mkdir(parents=True, exist_ok=True)
        self.CONFIGS_DIR.mkdir(parents=True, exist_ok=True)
        for subdir in ["providers", "personas/templates", "personas/custom",
                       "surveys/templates", "surveys/custom",
                       "behavior_prompts", "scenarios"]:
            (self.CONFIGS_DIR / subdir).mkdir(parents=True, exist_ok=True)


# 全局配置实例
settings = Settings()


def get_settings() -> Settings:
    """获取配置实例"""
    return settings
