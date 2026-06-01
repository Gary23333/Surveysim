"""主持人管理器"""

import asyncio
from typing import Any, Dict, List, Optional

from ..models.scenario import AgentResponse, ModeratorDecision
from .moderator import AIModerator


class HumanModerator:
    """人类主持人"""

    def __init__(self, websocket_manager: Any = None, session_id: str = ""):
        self.websocket_manager = websocket_manager
        self.session_id = session_id
        self.is_active = False
        self._command_queue: asyncio.Queue = asyncio.Queue()

    async def activate(self) -> None:
        """激活人类主持人"""
        self.is_active = True

    async def deactivate(self) -> None:
        """停用人类主持人"""
        self.is_active = False

    async def send_command(self, command: Dict[str, Any]) -> None:
        """发送指令（从 WebSocket 层调用）"""
        await self._command_queue.put(command)

    async def receive_command(self) -> Dict[str, Any]:
        """接收指令（阻塞等待人类输入）"""
        return await self._command_queue.get()

    async def evaluate_response(
        self,
        question: str,
        response: AgentResponse,
        agent: Any,
    ) -> ModeratorDecision:
        """人类主持人评估 — 等待人类通过 WebSocket 发送决策"""
        # 广播等待指示
        await self._broadcast_awaiting("decision", question=question, agent_name=agent.name)
        # 等待人类指令
        command = await self.receive_command()

        return ModeratorDecision(
            action=command.get("action", "continue"),
            reason="Human decision",
            target=command.get("target"),
            content=command.get("content"),
            follow_up_question=command.get("follow_up_question"),
        )

    async def wait_for_input(self, input_type: str, **context) -> str:
        """等待人类输入（开场白/引导语/总结等）"""
        await self._broadcast_awaiting(input_type, **context)
        command = await self.receive_command()
        return command.get("content", "")

    async def _broadcast_awaiting(self, input_type: str, **context) -> None:
        """广播等待主持人输入的事件"""
        if self.websocket_manager and self.session_id:
            await self.websocket_manager.broadcast(self.session_id, {
                "type": "system_event",
                "event": "awaiting_moderator_input",
                "data": {
                    "input_type": input_type,
                    **context,
                },
            })


class ModeratorManager:
    """主持人管理器，支持AI/人类切换"""

    def __init__(
        self,
        ai_moderator: Optional[AIModerator] = None,
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
        """生成开场白 — 人类模式下等待输入，AI模式下自动生成"""
        if self.current_type == "human":
            agents_desc = ", ".join([a.name for a in agents])
            return await self.human_moderator.wait_for_input(
                "opening", topic=topic, agents=agents_desc
            )
        if not self.ai_moderator:
            return f"欢迎参加本次调研，主题是：{topic}"
        return await self.ai_moderator.generate_opening(topic, agents)

    async def evaluate_response(
        self,
        question: str,
        response: AgentResponse,
        agent: Any,
    ) -> ModeratorDecision:
        """评估回答"""
        if self.current_type == "human":
            return await self.human_moderator.evaluate_response(question, response, agent)
        if not self.ai_moderator:
            return ModeratorDecision(action="continue", reason="No moderator configured")
        return await self.ai_moderator.evaluate_response(question, response, agent)

    async def generate_guidance(
        self,
        topic: str,
        recent_responses: List[AgentResponse],
        round_num: int,
    ) -> Optional[str]:
        """生成引导 — 人类模式下等待输入"""
        if self.current_type == "human":
            return await self.human_moderator.wait_for_input(
                "guidance", topic=topic, round=round_num
            )
        if not self.ai_moderator:
            return None
        return await self.ai_moderator.generate_guidance(topic, recent_responses, round_num)

    async def generate_summary(
        self,
        topic: str,
        all_responses: List[AgentResponse],
    ) -> str:
        """生成总结 — 人类模式下等待输入"""
        if self.current_type == "human":
            response_count = len(all_responses)
            return await self.human_moderator.wait_for_input(
                "summary", topic=topic, response_count=response_count
            )
        if not self.ai_moderator:
            return f"本次调研主题：{topic}，共收集 {len(all_responses)} 条回答。"
        return await self.ai_moderator.generate_summary(topic, all_responses)
