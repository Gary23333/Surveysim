"""YAML配置文件存储"""

import os
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from ..config import settings


class ConfigStore:
    """配置文件存储"""

    def __init__(self, config_dir: Optional[Path] = None):
        self.config_dir = config_dir or settings.CONFIGS_DIR

    def _get_file_path(self, config_type: str, name: str, is_template: bool = False) -> Path:
        """获取配置文件路径"""
        if is_template:
            return self.config_dir / config_type / "templates" / f"{name}.yaml"
        return self.config_dir / config_type / f"{name}.yaml"

    def read_yaml(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """读取YAML文件"""
        if not file_path.exists():
            return None
        with open(file_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    def write_yaml(self, file_path: Path, data: Dict[str, Any]) -> None:
        """写入YAML文件"""
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

    def delete_yaml(self, file_path: Path) -> bool:
        """删除YAML文件"""
        if file_path.exists():
            file_path.unlink()
            return True
        return False

    def list_configs(self, config_type: str, is_template: bool = False) -> List[Dict[str, Any]]:
        """列出配置文件"""
        if is_template:
            config_dir = self.config_dir / config_type / "templates"
        else:
            config_dir = self.config_dir / config_type

        if not config_dir.exists():
            return []

        configs = []
        for file_path in config_dir.glob("*.yaml"):
            data = self.read_yaml(file_path)
            if data:
                data["_file"] = file_path.stem
                configs.append(data)
        return configs

    def get_config(self, config_type: str, name: str, is_template: bool = False) -> Optional[Dict[str, Any]]:
        """获取配置"""
        file_path = self._get_file_path(config_type, name, is_template)
        return self.read_yaml(file_path)

    def save_config(self, config_type: str, name: str, data: Dict[str, Any], is_template: bool = False) -> None:
        """保存配置"""
        file_path = self._get_file_path(config_type, name, is_template)
        self.write_yaml(file_path, data)

    def delete_config(self, config_type: str, name: str, is_template: bool = False) -> bool:
        """删除配置"""
        file_path = self._get_file_path(config_type, name, is_template)
        return self.delete_yaml(file_path)


class ProviderConfigStore:
    """Provider配置存储"""

    def __init__(self):
        self.store = ConfigStore()

    def list_providers(self) -> List[Dict[str, Any]]:
        """列出所有Provider"""
        return self.store.list_configs("providers")

    def get_provider(self, name: str) -> Optional[Dict[str, Any]]:
        """获取Provider配置"""
        return self.store.get_config("providers", name)

    def save_provider(self, name: str, data: Dict[str, Any]) -> None:
        """保存Provider配置"""
        # 确保有name字段
        data["name"] = name
        self.store.save_config("providers", name, data)

    def delete_provider(self, name: str) -> bool:
        """删除Provider配置"""
        return self.store.delete_config("providers", name)


class PersonaConfigStore:
    """Persona配置存储"""

    def __init__(self):
        self.store = ConfigStore()

    def list_templates(self) -> List[Dict[str, Any]]:
        return self.store.list_configs("personas", is_template=True)

    def get_template(self, template_id: str) -> Optional[Dict[str, Any]]:
        return self.store.get_config("personas", template_id, is_template=True)

    def list_custom(self) -> List[Dict[str, Any]]:
        return self.store.list_configs("personas/custom")

    def get_custom(self, persona_id: str) -> Optional[Dict[str, Any]]:
        return self.store.get_config("personas/custom", persona_id)

    def save_custom(self, persona_id: str, data: Dict[str, Any]) -> None:
        data["id"] = persona_id
        self.store.save_config("personas/custom", persona_id, data)

    def delete_custom(self, persona_id: str) -> bool:
        return self.store.delete_config("personas/custom", persona_id)


class PersonaGroupStore:
    """人格分组存储"""

    def __init__(self):
        self.store = ConfigStore()

    def list_groups(self) -> List[Dict[str, Any]]:
        return self.store.list_configs("personas/groups")

    def get_group(self, group_id: str) -> Optional[Dict[str, Any]]:
        return self.store.get_config("personas/groups", group_id)

    def save_group(self, group_id: str, data: Dict[str, Any]) -> None:
        data["id"] = group_id
        self.store.save_config("personas/groups", group_id, data)

    def delete_group(self, group_id: str) -> bool:
        return self.store.delete_config("personas/groups", group_id)

    def get_groups_for_persona(self, persona_id: str) -> List[str]:
        """获取某个人格所属的所有分组名称"""
        groups = []
        for g in self.list_groups():
            if persona_id in g.get("persona_ids", []):
                groups.append(g.get("name", g.get("id", "")))
        return groups


class SurveyConfigStore:
    """问卷配置存储"""

    def __init__(self):
        self.store = ConfigStore()

    def list_templates(self) -> List[Dict[str, Any]]:
        """列出所有问卷模板"""
        return self.store.list_configs("surveys", is_template=True)

    def get_template(self, template_id: str) -> Optional[Dict[str, Any]]:
        """获取问卷模板"""
        return self.store.get_config("surveys", template_id, is_template=True)

    def list_custom(self) -> List[Dict[str, Any]]:
        """列出所有自定义问卷"""
        return self.store.list_configs("surveys/custom")

    def get_custom(self, survey_id: str) -> Optional[Dict[str, Any]]:
        """获取自定义问卷"""
        return self.store.get_config("surveys/custom", survey_id)

    def save_custom(self, survey_id: str, data: Dict[str, Any]) -> None:
        """保存自定义问卷"""
        data["id"] = survey_id
        self.store.save_config("surveys/custom", survey_id, data)

    def delete_custom(self, survey_id: str) -> bool:
        """删除自定义问卷"""
        return self.store.delete_config("surveys/custom", survey_id)


class BehaviorPromptStore:
    """行为提示词存储"""

    def __init__(self):
        self.store = ConfigStore()

    def list_prompts(self) -> List[Dict[str, Any]]:
        """列出所有行为提示词"""
        return self.store.list_configs("behavior_prompts")

    def get_prompt(self, prompt_id: str) -> Optional[Dict[str, Any]]:
        """获取行为提示词"""
        return self.store.get_config("behavior_prompts", prompt_id)

    def save_prompt(self, prompt_id: str, data: Dict[str, Any]) -> None:
        """保存行为提示词"""
        data["id"] = prompt_id
        self.store.save_config("behavior_prompts", prompt_id, data)

    def delete_prompt(self, prompt_id: str) -> bool:
        """删除行为提示词"""
        return self.store.delete_config("behavior_prompts", prompt_id)


# 全局配置存储实例
provider_store = ProviderConfigStore()
persona_store = PersonaConfigStore()
survey_store = SurveyConfigStore()
behavior_prompt_store = BehaviorPromptStore()
persona_group_store = PersonaGroupStore()
