"""焦点小组场景"""

import asyncio
from datetime import datetime
from typing import Any, Dict, List

from ...models.scenario import AgentResponse, QuestionResult, ScenarioResult
from .base import Scenario


class FocusGroupScenario(Scenario):
    """焦点小组场景"""

    def __init__(self, session: Any):
        super().__init__(session)
        self.topic: str = ""
        self.max_rounds: int = 5
        self.min_participants: int = 3
        self.enable_moderator_guidance: bool = True

    async def initialize(self, config: Dict[str, Any]) -> None:
        """初始化场景"""
        self.topic = config.get("topic", self.session.survey.name)
        self.max_rounds = config.get("max_rounds", 5)
        self.min_participants = config.get("min_participants", 3)
        self.enable_moderator_guidance = config.get("enable_moderator_guidance", True)

    async def execute(self) -> ScenarioResult:
        """执行焦点小组讨论"""
        # 主持人开场
        opening = await self.session.moderator_manager.generate_opening(
            self.topic, list(self.session.agents.values())
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

        all_responses = []

        for round_num in range(self.max_rounds):
            # 检查暂停/停止
            await self.check_status()

            self.current_question = round_num

            # 广播轮次变更
            await self.session.broadcast({
                "type": "system_event",
                "event": "round_changed",
                "data": {
                    "round": round_num + 1,
                    "total_rounds": self.max_rounds,
                },
            })

            # 执行一轮讨论
            round_responses = await self._execute_round(round_num, all_responses)
            all_responses.extend(round_responses)

            # 创建问题结果
            question_result = QuestionResult(
                question_id=f"round_{round_num}",
                question_text=f"第{round_num + 1}轮讨论",
                responses=round_responses,
                follow_ups=[],
            )
            self.question_results.append(question_result)

            # 主持人引导
            if self.enable_moderator_guidance and round_num < self.max_rounds - 1:
                guidance = await self.session.moderator_manager.generate_guidance(
                    self.topic, round_responses, round_num
                )
                if guidance:
                    await self.session.broadcast({
                        "type": "agent_response",
                        "agent_id": "moderator",
                        "agent_name": "主持人",
                        "content": guidance,
                        "emotion": "neutral",
                        "emotion_intensity": 0.5,
                        "timestamp": datetime.now().isoformat(),
                    })

            # 检查是否话题枯竭
            if self._is_topic_exhausted(round_responses):
                break

            # 轮次间隔
            await asyncio.sleep(1.0)

        # 生成总结
        summary = await self.session.moderator_manager.generate_summary(
            self.topic, all_responses
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

    async def _execute_round(
        self,
        round_num: int,
        previous_responses: List[AgentResponse],
    ) -> List[AgentResponse]:
        """执行一轮讨论"""
        round_responses = []

        for agent_id, agent in self.session.agents.items():
            context = {
                "visibility": "open",
                "round": round_num,
                "topic": self.topic,
                "previous_responses": previous_responses + round_responses,
            }

            # Agent自由决定是否发言
            response = await agent.decide_and_respond(self.topic, context)

            if response:
                round_responses.append(response)
                await self.broadcast_response(response)

        return round_responses

    def _is_topic_exhausted(self, round_responses: List[AgentResponse]) -> bool:
        """检查话题是否枯竭"""
        # 如果这轮没有人发言，话题可能枯竭
        if not round_responses:
            return True

        # 如果发言都很短，可能话题枯竭
        avg_length = sum(len(r.content) for r in round_responses) / len(round_responses)
        if avg_length < 20:
            return True

        return False
