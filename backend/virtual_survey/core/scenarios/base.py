"""场景基类"""

import asyncio
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List, Optional

from ...models.scenario import AgentResponse, QuestionResult, ScenarioResult, SurveyFeedback


class Scenario(ABC):
    """场景基类"""

    def __init__(self, session: Any):
        self.session = session
        self.responses: List[AgentResponse] = []
        self.question_results: List[QuestionResult] = []
        self.survey_feedback: List[SurveyFeedback] = []
        self.current_question: int = 0
        self._stop_flag: bool = False

    @abstractmethod
    async def initialize(self, config: Dict[str, Any]) -> None:
        """初始化场景"""
        pass

    @abstractmethod
    async def execute(self) -> ScenarioResult:
        """执行场景，返回结果"""
        pass

    @abstractmethod
    async def execute_question(self, question: Any, **kwargs) -> List[AgentResponse]:
        """执行单个问题"""
        pass

    async def broadcast_response(self, response: AgentResponse) -> None:
        """广播回答"""
        self.responses.append(response)
        await self.session.broadcast({
            "type": "agent_response",
            "agent_id": response.agent_id,
            "agent_name": response.agent_name,
            "content": response.content,
            "emotion": response.emotion,
            "emotion_intensity": response.emotion_intensity,
            "timestamp": response.timestamp,
            "metadata": response.metadata,
        })

    async def broadcast_question(self, question: Any, index: int, total: int) -> None:
        """广播问题变更"""
        await self.session.broadcast({
            "type": "system_event",
            "event": "question_changed",
            "data": {
                "index": index,
                "total": total,
                "question_id": question.id if hasattr(question, 'id') else str(index),
                "question_text": question.text if hasattr(question, 'text') else str(question),
            },
        })

    async def check_status(self) -> None:
        """检查状态（用于暂停/停止）"""
        if self._stop_flag:
            raise StopIteration("Task stopped")

        # 等待暂停恢复
        if hasattr(self.session, '_pause_event'):
            await self.session._pause_event.wait()

    def stop(self) -> None:
        """停止场景"""
        self._stop_flag = True

    async def _collect_feedback(self) -> None:
        """收集所有Agent对问卷的体验反馈"""
        questions_summary = f"共{len(self.question_results)}道题，包含多种题型（单选、多选、开放题、程度评分题）。"
        for agent_id, agent in self.session.agents.items():
            fb = await agent.rate_survey(questions_summary)
            if fb:
                self.survey_feedback.append({
                    "agent_id": fb.agent_id,
                    "agent_name": fb.agent_name,
                    "length_rating": fb.length_rating,
                    "difficulty_rating": fb.difficulty_rating,
                    "clarity_rating": fb.clarity_rating,
                    "fatigue_rating": fb.fatigue_rating,
                    "interest_rating": fb.interest_rating,
                    "comment": fb.comment,
                })

    def get_result(self) -> ScenarioResult:
        """获取结果"""
        # 计算统计信息
        total_responses = len(self.responses)
        total_follow_ups = sum(
            len(qr.follow_ups) for qr in self.question_results
        )

        # 计算平均回答长度
        if self.responses:
            avg_length = sum(len(r.content) for r in self.responses) / len(self.responses)
        else:
            avg_length = 0

        # 计算情绪分布
        emotion_dist = {}
        for response in self.responses:
            emotion = response.emotion
            emotion_dist[emotion] = emotion_dist.get(emotion, 0) + 1

        # 归一化情绪分布
        if emotion_dist:
            total = sum(emotion_dist.values())
            emotion_dist = {k: v / total for k, v in emotion_dist.items()}

        return ScenarioResult(
            scenario_type=self.__class__.__name__,
            total_questions=len(self.question_results),
            total_responses=total_responses,
            total_follow_ups=total_follow_ups,
            question_results=self.question_results,
            summary=self._generate_summary(emotion_dist, avg_length),
            emotion_distribution=emotion_dist,
            avg_response_length=avg_length,
            survey_feedback=self.survey_feedback,
        )

    def _generate_summary(self, emotion_dist: Dict[str, float], avg_length: float) -> str:
        """生成总结"""
        lines = [
            f"共收集 {len(self.responses)} 条回答",
            f"平均回答长度: {avg_length:.0f} 字",
        ]

        if emotion_dist:
            # 找出主要情绪
            main_emotion = max(emotion_dist.items(), key=lambda x: x[1])
            lines.append(f"主要情绪: {main_emotion[0]} ({main_emotion[1]:.0%})")

        return "\n".join(lines)
