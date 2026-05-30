"""深度访谈场景"""

import asyncio
from datetime import datetime
from typing import Any, Dict, List

from ...models.scenario import AgentResponse, FollowUpResult, QuestionResult, ScenarioResult
from .base import Scenario


class IDIScenario(Scenario):
    """深度访谈场景（一对一）"""

    def __init__(self, session: Any):
        super().__init__(session)
        self.target_agent_id: str = ""
        self.max_questions: int = 10
        self.enable_deep_follow_up: bool = True
        self.max_follow_up_depth: int = 3

    async def initialize(self, config: Dict[str, Any]) -> None:
        """初始化场景"""
        self.target_agent_id = config.get(
            "target_agent_id",
            list(self.session.agents.keys())[0] if self.session.agents else ""
        )
        self.max_questions = config.get("max_questions", 10)
        self.enable_deep_follow_up = config.get("enable_deep_follow_up", True)
        self.max_follow_up_depth = config.get("max_follow_up_depth", 3)

    async def execute(self) -> ScenarioResult:
        """执行深度访谈"""
        # 获取目标Agent
        target_agent = self.session.agents.get(self.target_agent_id)
        if not target_agent:
            raise ValueError(f"Target agent '{self.target_agent_id}' not found")

        # 主持人开场
        opening = await self.session.moderator_manager.generate_opening(
            self.session.survey.name, [target_agent]
        )

        await self.session.broadcast({
            "type": "agent_response",
            "agent_id": "moderator",
            "agent_name": "主持人",
            "content": opening,
            "emotion": "neutral",
            "emotion_intensity": 0.5,
            "timestamp": datetime.now().isoformat(),
        })

        questions = self.session.survey.questions[:self.max_questions]

        for i, question in enumerate(questions):
            # 检查暂停/停止
            await self.check_status()

            self.current_question = i

            # 广播问题变更
            await self.broadcast_question(question, i, len(questions))

            # Agent回答
            response = await target_agent.respond(
                question.text, {"visibility": "isolated"}
            )
            await self.broadcast_response(response)

            # 创建问题结果
            question_result = QuestionResult(
                question_id=question.id,
                question_text=question.text,
                responses=[response],
                follow_ups=[],
            )

            # 深度追问
            if self.enable_deep_follow_up:
                follow_ups = await self._conduct_follow_ups(
                    target_agent, question, response
                )
                question_result.follow_ups = follow_ups

            self.question_results.append(question_result)

            # 问题间隔
            await asyncio.sleep(1.0)

        # 生成总结
        summary = await self.session.moderator_manager.generate_summary(
            self.session.survey.name, self.responses
        )

        await self.session.broadcast({
            "type": "agent_response",
            "agent_id": "moderator",
            "agent_name": "主持人",
            "content": summary,
            "emotion": "neutral",
            "emotion_intensity": 0.5,
            "timestamp": datetime.now().isoformat(),
        })

        return self.get_result()

    async def _conduct_follow_ups(
        self,
        agent: Any,
        question: Any,
        initial_response: AgentResponse,
    ) -> List[FollowUpResult]:
        """进行深度追问"""
        follow_ups = []
        current_response = initial_response

        for depth in range(self.max_follow_up_depth):
            # 获取主持人决策
            decision = await self.session.moderator_manager.evaluate_response(
                question.text, current_response, agent
            )

            if decision.action != "follow_up":
                break

            # 主持人追问
            if decision.content:
                await self.session.broadcast({
                    "type": "agent_response",
                    "agent_id": "moderator",
                    "agent_name": "主持人",
                    "content": decision.content,
                    "emotion": "neutral",
                    "emotion_intensity": 0.5,
                    "timestamp": datetime.now().isoformat(),
                })

            # Agent回答追问
            current_response = await agent.respond(
                decision.follow_up_question or decision.content,
                {"visibility": "isolated", "is_follow_up": True}
            )
            await self.broadcast_response(current_response)

            follow_ups.append(FollowUpResult(
                question=decision.follow_up_question or decision.content,
                response=current_response,
                depth=depth + 1,
            ))

        return follow_ups
