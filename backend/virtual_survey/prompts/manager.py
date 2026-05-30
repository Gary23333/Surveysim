"""提示词管理器"""

from pathlib import Path
from typing import Any, Dict, List, Optional

from jinja2 import Environment, FileSystemLoader, select_autoescape

from ..config import settings


class PromptManager:
    """提示词管理器"""

    def __init__(self, template_dir: Optional[Path] = None):
        self.template_dir = template_dir or settings.BASE_DIR / "virtual_survey" / "prompts" / "templates"
        self.env = Environment(
            loader=FileSystemLoader(str(self.template_dir)),
            autoescape=select_autoescape(["html"]),
            trim_blocks=True,
            lstrip_blocks=True,
        )

    def render_respondent(
        self,
        persona: Any,
        memory_context: str,
        behavior_prompt: str,
        scenario_context: str = "",
        other_agents_state: str = "",
    ) -> str:
        """
        渲染受访者提示词

        Args:
            persona: Persona对象
            memory_context: 记忆上下文
            behavior_prompt: 行为提示词
            scenario_context: 场景上下文
            other_agents_state: 其他Agent状态

        Returns:
            渲染后的提示词
        """
        template = self.env.get_template("respondent.jinja2")
        return template.render(
            persona=persona,
            memory_context=memory_context,
            behavior_prompt=behavior_prompt,
            scenario_context=scenario_context,
            other_agents_state=other_agents_state,
        )

    def render_moderator(
        self,
        survey: Any,
        progress: Dict[str, int],
        mode: str,
        visibility: str,
        agents_summary: str,
        current_question: str,
        latest_response: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        渲染主持人提示词

        Args:
            survey: 问卷对象
            progress: 进度信息
            mode: 模式
            visibility: 可见性
            agents_summary: Agent摘要
            current_question: 当前问题
            latest_response: 最新回答

        Returns:
            渲染后的提示词
        """
        template = self.env.get_template("moderator.jinja2")
        return template.render(
            survey=survey,
            progress=progress,
            mode=mode,
            visibility=visibility,
            agents_summary=agents_summary,
            current_question=current_question,
            latest_response=latest_response,
        )

    def render_attitude_extraction(
        self,
        question: str,
        response: str,
        persona_summary: str,
    ) -> str:
        """
        渲染态度提取提示词

        Args:
            question: 问题
            response: 回答
            persona_summary: Persona摘要

        Returns:
            渲染后的提示词
        """
        template = self.env.get_template("attitude_extraction.jinja2")
        return template.render(
            question=question,
            response=response,
            persona_summary=persona_summary,
        )

    def render_experience_extraction(
        self,
        response: str,
        persona_summary: str,
    ) -> str:
        """
        渲染经历提取提示词

        Args:
            response: 回答
            persona_summary: Persona摘要

        Returns:
            渲染后的提示词
        """
        template = self.env.get_template("experience_extraction.jinja2")
        return template.render(
            response=response,
            persona_summary=persona_summary,
        )

    def list_templates(self) -> List[str]:
        """列出所有模板"""
        return [f.stem for f in self.template_dir.glob("*.jinja2")]

    def get_template(self, name: str) -> Any:
        """获取模板"""
        return self.env.get_template(f"{name}.jinja2")


# 全局提示词管理器实例
prompt_manager = PromptManager()
