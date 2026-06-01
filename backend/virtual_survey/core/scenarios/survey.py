"""问卷调查场景"""

import asyncio
from datetime import datetime
from typing import Any, Dict, List, Optional

from ...models.scenario import (
    AgentResponse,
    FollowUpResult,
    ModeratorDecision,
    QuestionResult,
    ScenarioResult,
)
from .base import Scenario


class SurveyScenario(Scenario):
    """问卷调查场景"""

    def __init__(self, session: Any):
        super().__init__(session)
        self.default_mode: str = "global"
        self.default_visibility: str = "isolated"
        self.enable_follow_up: bool = True
        self.follow_up_threshold: int = 30

    async def initialize(self, config: Dict[str, Any]) -> None:
        """初始化场景"""
        self.default_mode = config.get("default_mode", "global")
        self.default_visibility = config.get("default_visibility", "isolated")
        self.enable_follow_up = config.get("enable_follow_up", True)
        self.follow_up_threshold = config.get("follow_up_threshold", 30)

    async def execute(self) -> ScenarioResult:
        """执行问卷调查"""
        questions = self.session.survey.questions

        for i, question in enumerate(questions):
            # 检查暂停/停止
            await self.check_status()

            self.current_question = i

            # 人工主持人模式：等待人类推进到下一题
            if self.is_human_moderator:
                await self.wait_for_next_question()
                # 人工模式下，题目由 handle_command 的 next_question 驱动回答
                # 跳过自动执行，只收集已有的回答
                continue

            # 广播问题变更
            await self.broadcast_question(question, i, len(questions))

            # 获取问题的模式和可见性
            mode = getattr(question, 'mode', self.default_mode) or self.default_mode
            visibility = getattr(question, 'visibility', self.default_visibility) or self.default_visibility

            # 执行问题
            responses = await self.execute_question(question, mode=mode, visibility=visibility)

            # 创建问题结果
            question_result = QuestionResult(
                question_id=question.id,
                question_text=question.text,
                responses=responses,
                follow_ups=[],
            )

            # 检查是否需要追问
            if self.enable_follow_up:
                follow_ups = await self._check_follow_ups(question, responses)
                question_result.follow_ups = follow_ups

            self.question_results.append(question_result)

            # 问题间隔
            delay = self.session.task.settings.delay_between_questions
            if delay > 0:
                await asyncio.sleep(delay)

        # 收集问卷体验反馈（AI 模式下自动收集）
        if not self.is_human_moderator:
            await self._collect_feedback()

        return self.get_result()

    async def execute_question(
        self,
        question: Any,
        mode: str = "global",
        visibility: str = "isolated",
        **kwargs,
    ) -> List[AgentResponse]:
        """执行单个问题"""
        if mode == "global":
            return await self._execute_global(question, visibility)
        elif mode == "sequential":
            return await self._execute_sequential(question, visibility)
        elif mode == "open":
            return await self._execute_open(question, visibility)
        else:
            return await self._execute_global(question, visibility)

    async def _execute_global(
        self,
        question: Any,
        visibility: str,
    ) -> List[AgentResponse]:
        """全局提问：所有Agent同时回答"""
        tasks = []
        ctx = {"visibility": visibility}
        if getattr(question, 'enable_rating', False):
            ctx["enable_rating"] = True
            ctx["enable_text"] = getattr(question, 'enable_text', True)
            ctx["rating_config"] = getattr(question, 'rating_config', None)
            if isinstance(ctx["rating_config"], dict):
                ctx["rating_config"] = ctx["rating_config"]
            elif ctx["rating_config"] is not None:
                ctx["rating_config"] = {"min_value": 1, "max_value": 10,
                    "min_label": getattr(ctx["rating_config"], 'min_label', ''),
                    "max_label": getattr(ctx["rating_config"], 'max_label', '')}
        for agent_id, agent in self.session.agents.items():
            tasks.append(agent.respond(question.text, ctx))

        responses = await asyncio.gather(*tasks, return_exceptions=True)

        # 过滤异常
        valid_responses = []
        for response in responses:
            if isinstance(response, AgentResponse):
                valid_responses.append(response)
                await self.broadcast_response(response)
            elif isinstance(response, Exception):
                print(f"Agent response error: {response}")

        return valid_responses

    async def _execute_sequential(
        self,
        question: Any,
        visibility: str,
    ) -> List[AgentResponse]:
        """顺序提问：逐个Agent回答"""
        responses = []
        for agent_id, agent in self.session.agents.items():
            ctx = {"visibility": visibility}
            if getattr(question, 'enable_rating', False):
                self._add_rating_ctx(ctx, question)
            if visibility == "open" and responses:
                ctx["previous_responses"] = responses
            response = await agent.respond(question.text, ctx)
            responses.append(response)
            await self.broadcast_response(response)
        return responses

    async def _execute_open(
        self,
        question: Any,
        visibility: str,
    ) -> List[AgentResponse]:
        """开放场景：自由讨论"""
        responses = []
        max_rounds = 3
        for round_num in range(max_rounds):
            round_responses = []
            for agent_id, agent in self.session.agents.items():
                ctx = {"visibility": "open", "round": round_num, "previous_responses": responses}
                if getattr(question, 'enable_rating', False):
                    self._add_rating_ctx(ctx, question)
                response = await agent.respond(question.text, ctx)
                if response.content:
                    round_responses.append(response)
                    await self.broadcast_response(response)
            responses.extend(round_responses)
            if not round_responses:
                break
        return responses

    def _add_rating_ctx(self, ctx: dict, question: Any):
        ctx["enable_rating"] = True
        ctx["enable_text"] = getattr(question, 'enable_text', True)
        ctx["rating_config"] = getattr(question, 'rating_config', None) or {"min_value": 1, "max_value": 10, "min_label": "", "max_label": ""}

    async def _check_follow_ups(
        self,
        question: Any,
        responses: List[AgentResponse],
    ) -> List[FollowUpResult]:
        """检查是否需要追问"""
        follow_ups = []

        for response in responses:
            # 检查回答长度
            if len(response.content) < self.follow_up_threshold:
                follow_up = await self._do_follow_up(
                    question, response, "length"
                )
                if follow_up:
                    follow_ups.append(follow_up)
                continue

            # 检查模糊回答
            vague_words = ["还行", "一般", "还好", "不错", "可以", "不知道"]
            if any(word in response.content for word in vague_words):
                follow_up = await self._do_follow_up(
                    question, response, "vague"
                )
                if follow_up:
                    follow_ups.append(follow_up)

        return follow_ups

    async def _do_follow_up(
        self,
        question: Any,
        response: AgentResponse,
        trigger: str,
    ) -> Optional[FollowUpResult]:
        """执行追问"""
        # 获取主持人决策
        decision = await self.session.moderator_manager.evaluate_response(
            question.text, response, self.session.agents[response.agent_id]
        )

        if decision.action != "follow_up":
            return None

        # 广播主持人追问
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
        agent = self.session.agents[response.agent_id]
        follow_up_response = await agent.respond(
            decision.follow_up_question or decision.content,
            {"visibility": "isolated", "is_follow_up": True}
        )

        # 广播回答
        await self.broadcast_response(follow_up_response)

        return FollowUpResult(
            question=decision.follow_up_question or decision.content,
            response=follow_up_response,
            depth=1,
        )
