"""辩论讨论场景"""

import asyncio
from datetime import datetime
from typing import Any, Dict, List

from ...models.scenario import AgentResponse, QuestionResult, ScenarioResult
from .base import Scenario


class DebateScenario(Scenario):
    """辩论讨论场景"""

    def __init__(self, session: Any):
        super().__init__(session)
        self.topic: str = ""
        self.rounds: int = 3
        self.enable_summary: bool = True
        self.pro_team: List[Any] = []
        self.con_team: List[Any] = []

    async def initialize(self, config: Dict[str, Any]) -> None:
        """初始化场景"""
        self.topic = config.get("topic", self.session.survey.name)
        self.rounds = config.get("rounds", 3)
        self.enable_summary = config.get("enable_summary", True)

        # 将Agent分为正反方
        agents_list = list(self.session.agents.values())
        mid = len(agents_list) // 2
        self.pro_team = agents_list[:mid]
        self.con_team = agents_list[mid:]

        # 为每个Agent分配立场
        for agent in self.pro_team:
            agent.debate_stance = "pro"
        for agent in self.con_team:
            agent.debate_stance = "con"

    async def execute(self) -> ScenarioResult:
        """执行辩论"""
        # 主持人开场
        opening = await self.session.moderator_manager.generate_opening(
            self.topic,
            list(self.session.agents.values()),
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

        # 广播辩论主题
        await self.session.broadcast({
            "type": "system_event",
            "event": "debate_topic",
            "data": {
                "topic": self.topic,
                "pro_team": [a.name for a in self.pro_team],
                "con_team": [a.name for a in self.con_team],
            },
        })

        all_responses = []

        for round_num in range(self.rounds):
            # 检查暂停/停止
            await self.check_status()

            self.current_question = round_num

            # 广播轮次变更
            await self.session.broadcast({
                "type": "system_event",
                "event": "round_changed",
                "data": {
                    "round": round_num + 1,
                    "total_rounds": self.rounds,
                    "phase": "debate",
                },
            })

            # 正方发言
            pro_responses = await self._team_speak(
                self.pro_team, self.topic, round_num, "pro", all_responses
            )
            all_responses.extend(pro_responses)

            # 反方发言
            con_responses = await self._team_speak(
                self.con_team, self.topic, round_num, "con", all_responses
            )
            all_responses.extend(con_responses)

            # 创建问题结果
            question_result = QuestionResult(
                question_id=f"round_{round_num}",
                question_text=f"第{round_num + 1}轮辩论",
                responses=pro_responses + con_responses,
                follow_ups=[],
            )
            self.question_results.append(question_result)

            # 轮次间隔
            await asyncio.sleep(1.0)

        # 总结陈词
        if self.enable_summary:
            await self._generate_summaries(list(self.session.agents.values()))

        return self.get_result()

    async def _team_speak(
        self,
        team: List[Any],
        topic: str,
        round_num: int,
        stance: str,
        previous_responses: List[AgentResponse],
    ) -> List[AgentResponse]:
        """团队发言"""
        responses = []

        for agent in team:
            context = {
                "visibility": "open",
                "round": round_num,
                "topic": topic,
                "stance": stance,
                "previous_responses": previous_responses + responses,
                "debate_mode": True,
            }

            prompt = f"请从{stance}方角度论述：{topic}"
            response = await agent.respond(prompt, context)
            responses.append(response)
            await self.broadcast_response(response)

        return responses

    async def _generate_summaries(self, agents: List[Any]) -> None:
        """生成总结陈词"""
        # 广播总结阶段
        await self.session.broadcast({
            "type": "system_event",
            "event": "round_changed",
            "data": {
                "round": self.rounds + 1,
                "total_rounds": self.rounds,
                "phase": "summary",
            },
        })

        # 正方总结
        pro_summary_agent = self.pro_team[0] if self.pro_team else None
        if pro_summary_agent:
            pro_summary = await pro_summary_agent.respond(
                f"请作为正方代表，总结你们关于'{self.topic}'的观点",
                {"visibility": "open", "is_summary": True, "stance": "pro"}
            )
            await self.broadcast_response(pro_summary)

        # 反方总结
        con_summary_agent = self.con_team[0] if self.con_team else None
        if con_summary_agent:
            con_summary = await con_summary_agent.respond(
                f"请作为反方代表，总结你们关于'{self.topic}'的观点",
                {"visibility": "open", "is_summary": True, "stance": "con"}
            )
            await self.broadcast_response(con_summary)

        # 主持人总结
        summary = await self.session.moderator_manager.generate_summary(
            self.topic, self.responses
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
