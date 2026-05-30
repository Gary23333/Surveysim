"""主持人管理器"""

import asyncio
from typing import Any, Dict, List, Optional

from ..models.scenario import AgentResponse, ModeratorDecision
from .moderator import AIModerator


class HumanModerator:
    """人类主持人"""

    def __init__(self, websocket: Any = None):
        self.websocket = websocket
        self.is_active = False
        self._command_queue: asyncio.Queue = asyncio.Queue()

    async def activate(self) -> None:
        """激活人类主持人"""
        self.is_active = True

    async def deactivate(self) -> None:
        """停用人类主持人"""
        self.is_active = False

    async def send_command(self, command: Dict[str, Any]) -> None:
        """发送指令"""
        await self._command_queue.put(command)

    async def receive_command(self) -> Dict[str, Any]:
        """接收指令"""
        return await self._command_queue.get()

    async def evaluate_response(
        self,
        question: str,
        response: AgentResponse,
        agent: Any,
    ) -> ModeratorDecision:
        """人类主持人评估"""
        # 等待人类指令
        command = await self.receive_command()

        return ModeratorDecision(
            action=command.get("action", "continue"),
            reason="Human decision",
            target=command.get("target"),
            content=command.get("content"),
            follow_up_question=command.get("follow_up_question"),
        )


class ModeratorManager:
    """主持人管理器，支持AI/人类切换"""

    def __init__(
        self,
        ai_moderator: AIModerator,
        human_moderator: Optional[HumanModerator] = None,
    ):
        self.ai_moderator = ai_moderator
        self.human_moderator = human_moderator or HumanModerator()
        self.current_type = "ai"

    @property
    def current(self) -> Any:
        """获取当前主持人"""
        if self.current_type == "ai":
            return self.ai_moderator
        return self.human_moderator

    async def switch_to_human(self) -> None:
        """切换到人类主持人"""
        self.current_type = "human"
        await self.human_moderator.activate()

    async def switch_to_ai(self) -> None:
        """切换到AI主持人"""
        self.current_type = "ai"
        await self.human_moderator.deactivate()

    async def generate_opening(
        self,
        topic: str,
        agents: List[Any],
    ) -> str:
        """生成开场白"""
        return await self.ai_moderator.generate_opening(topic, agents)

    async def evaluate_response(
        self,
        question: str,
        response: AgentResponse,
        agent: Any,
    ) -> ModeratorDecision:
        """评估回答"""
        if self.current_type == "ai":
            return await self.ai_moderator.evaluate_response(question, response, agent)
        else:
            return await self.human_moderator.evaluate_response(question, response, agent)

    async def generate_guidance(
        self,
        topic: str,
        recent_responses: List[AgentResponse],
        round_num: int,
    ) -> Optional[str]:
        """生成引导"""
        return await self.ai_moderator.generate_guidance(topic, recent_responses, round_num)

    async def generate_summary(
        self,
        topic: str,
        all_responses: List[AgentResponse],
    ) -> str:
        """生成总结"""
        return await self.ai_moderator.generate_summary(topic, all_responses)
