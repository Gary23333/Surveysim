"""受访者Agent"""

import asyncio
import json
from datetime import datetime
from typing import Any, Dict, List, Optional

from ..llm.provider import LLMProvider
from ..memory.store import AgentMemory
from ..models.scenario import AgentResponse
from ..prompts.manager import prompt_manager


class RespondentAgent:
    """受访者Agent"""

    def __init__(
        self,
        id: str,
        name: str,
        persona: Any,
        provider: LLMProvider,
        model: str,
        behavior_prompt: str = "",
        memory_config: Optional[Dict[str, Any]] = None,
        thinking_enabled: bool = False,
        thinking_intensity: str = "medium",
        thinking_config: Any = None,
        max_tokens_param: str = "max_tokens",
    ):
        self.id = id
        self.name = name
        self.persona = persona
        self.provider = provider
        self.model = model
        self.behavior_prompt = behavior_prompt
        self.thinking_enabled = thinking_enabled
        self.thinking_intensity = thinking_intensity
        self.thinking_config = thinking_config
        self.max_tokens_param = max_tokens_param

        # 初始化记忆
        config = memory_config or {}
        self.memory = AgentMemory(
            agent_id=id,
            history_size=config.get("history_size", 10),
            max_anchors=config.get("max_anchors", 10),
        )

        # 状态
        self.state = "idle"  # idle/thinking/responding/error
        self.emotion = "neutral"
        self.emotion_intensity = 0.5
        self.debate_stance: Optional[str] = None

    async def respond(
        self,
        question: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentResponse:
        """回答问题"""
        self.state = "thinking"
        context = context or {}

        try:
            # 构建prompt
            system_prompt = self._build_system_prompt(context)
            user_prompt = self._build_user_prompt(question, context)

            # 调用LLM
            response_data = await self.provider.chat_json(
                [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                self.model,
                temperature=0.7,
                thinking_enabled=self.thinking_enabled,
                thinking_intensity=self.thinking_intensity,
                thinking_config=self.thinking_config,
                max_tokens_param=self.max_tokens_param,
            )

            # 解析响应
            content = response_data.get("content", "")
            emotion = response_data.get("emotion", "neutral")
            emotion_intensity = response_data.get("emotion_intensity", 0.5)
            score = response_data.get("score")
            if score is not None:
                try:
                    score = int(score)
                except (ValueError, TypeError):
                    score = None

            # 更新状态
            self.state = "responding"
            self.emotion = emotion
            self.emotion_intensity = emotion_intensity

            # 更新记忆
            self.memory.update_from_response(question, content, {
                "emotion": emotion,
                "emotion_intensity": emotion_intensity,
            })

            # 异步提取态度变化
            asyncio.create_task(self._extract_attitudes(question, content))

            return AgentResponse(
                agent_id=self.id,
                agent_name=self.name,
                content=content,
                emotion=emotion,
                emotion_intensity=emotion_intensity,
                score=score,
                timestamp=datetime.now().isoformat(),
            )

        except Exception as e:
            self.state = "error"
            # 返回错误响应
            return AgentResponse(
                agent_id=self.id,
                agent_name=self.name,
                content=f"[回答生成失败: {str(e)}]",
                emotion="error",
                emotion_intensity=0.0,
                timestamp=datetime.now().isoformat(),
            )

        finally:
            self.state = "idle"

    async def decide_and_respond(
        self,
        topic: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> Optional[AgentResponse]:
        """决定是否发言并回应（焦点小组场景）"""
        context = context or {}

        # 先判断是否要发言
        should_speak = await self._should_speak(topic, context)

        if not should_speak:
            return None

        return await self.respond(topic, context)

    async def _should_speak(self, topic: str, context: Dict[str, Any]) -> bool:
        """判断是否应该发言"""
        previous = context.get("previous_responses", [])

        prompt = f"""你是{self.name}，{self.persona.demographics.occupation}。

讨论话题：{topic}

之前的讨论：
{self._format_previous_responses(previous)}

请判断你是否想要发言。
考虑：
1. 你是否有独特的观点？
2. 你是否想回应其他人？
3. 你是否有相关经历想分享？

输出JSON：{{"should_speak": true/false, "reason": "理由"}}"""

        try:
            result = await self.provider.chat_json(
                [{"role": "user", "content": prompt}],
                self.model,
                temperature=0.5,
                thinking_enabled=self.thinking_enabled,
                thinking_intensity=self.thinking_intensity,
                thinking_config=self.thinking_config,
                max_tokens_param=self.max_tokens_param,
            )
            return result.get("should_speak", False)
        except Exception:
            return True  # 默认发言

    def _build_system_prompt(self, context: Dict[str, Any]) -> str:
        """构建系统提示词"""
        visibility = context.get("visibility", "isolated")
        memory_context = self.memory.get_prompt_context(visibility)

        other_agents_state = ""
        if visibility == "open" and "previous_responses" in context:
            other_agents_state = self._format_other_agents_state(
                context["previous_responses"]
            )

        # 使用模板渲染
        return prompt_manager.render_respondent(
            persona=self.persona,
            memory_context=memory_context,
            behavior_prompt=self.behavior_prompt,
            scenario_context=context.get("scenario", ""),
            other_agents_state=other_agents_state,
        )

    def _build_user_prompt(self, question: str, context: Dict[str, Any]) -> str:
        """构建用户提示词"""
        prompt = f"问题：{question}"

        if context.get("is_follow_up"):
            prompt = f"追问：{question}"

        if context.get("debate_mode"):
            stance = context.get("stance", "neutral")
            stance_label = "正方" if stance == "pro" else "反方"
            prompt = f"请从{stance_label}角度论述：{question}"

        if context.get("is_summary"):
            prompt = f"请总结：{question}"

        if context.get("enable_rating"):
            rc = context.get("rating_config") or {}
            mn = rc.get("min_value", 1) if isinstance(rc, dict) else getattr(rc, 'min_value', 1)
            mx = rc.get("max_value", 10) if isinstance(rc, dict) else getattr(rc, 'max_value', 10)
            ml = rc.get("min_label", "") if isinstance(rc, dict) else getattr(rc, 'min_label', '')
            xl = rc.get("max_label", "") if isinstance(rc, dict) else getattr(rc, 'max_label', '')
            prompt += f"\n\n这是一道程度评分题，请在 JSON 输出中额外包含 \"score\" 字段，给出 {mn}~{mx} 的整数评分："
            prompt += f"\n- {mn} 分 = {ml}"
            prompt += f"\n- {mx} 分 = {xl}"

            if context.get("enable_text", True):
                prompt += "\n同时请用文字说明你的评分理由。"

        return prompt

    def _format_previous_responses(self, responses: List[AgentResponse]) -> str:
        """格式化之前的回答"""
        if not responses:
            return "暂无其他人的回答"

        lines = []
        for r in responses[-5:]:  # 最近5条
            lines.append(f"- {r.agent_name}: {r.content[:100]}...")

        return "\n".join(lines)

    def _format_other_agents_state(self, responses: List[AgentResponse]) -> str:
        """格式化其他Agent状态"""
        if not responses:
            return ""

        lines = ["【其他参与者的发言】"]
        for r in responses[-3:]:  # 最近3条
            emotion_label = self._get_emotion_label(r.emotion)
            lines.append(
                f"- {r.agent_name}: 情绪={emotion_label}({r.emotion_intensity:.1f})，"
                f"说\"{r.content[:50]}...\""
            )

        return "\n".join(lines)

    def _get_emotion_label(self, emotion: str) -> str:
        """获取情绪标签"""
        emotion_labels = {
            "happy": "开心",
            "sad": "难过",
            "angry": "生气",
            "surprised": "惊讶",
            "neutral": "平静",
            "thinking": "思考",
            "confused": "困惑",
            "excited": "兴奋",
            "worried": "担忧",
            "curious": "好奇",
            "satisfied": "满意",
            "dissatisfied": "不满",
        }
        return emotion_labels.get(emotion, emotion)

    async def _extract_attitudes(self, question: str, response: str) -> None:
        """异步提取态度变化"""
        try:
            persona_summary = self._get_persona_summary()

            prompt = prompt_manager.render_attitude_extraction(
                question=question,
                response=response,
                persona_summary=persona_summary,
            )

            result = await self.provider.chat_json(
                [{"role": "user", "content": prompt}],
                self.model,
                temperature=0.3,
                thinking_enabled=self.thinking_enabled,
                thinking_intensity=self.thinking_intensity,
                thinking_config=self.thinking_config,
                max_tokens_param=self.max_tokens_param,
            )

            # 更新态度
            for attitude in result.get("attitudes", []):
                self.memory.update_attitude(
                    topic=attitude["topic"],
                    stance=attitude["stance"],
                    intensity=attitude["intensity"],
                    context=attitude.get("evidence", ""),
                )

            # 更新经历
            for exp in result.get("experiences", []):
                self.memory.add_experience(
                    content=exp["content"],
                    context=question,
                    importance=exp.get("importance", 0.5),
                )

        except Exception:
            pass  # 态度提取失败不影响主流程

    def _get_persona_summary(self) -> str:
        """获取Persona摘要"""
        demo = self.persona.get("demographics", {}) if isinstance(self.persona, dict) else (self.persona.demographics if hasattr(self.persona, 'demographics') else {})
        name = self.name
        age = demo.get("age", 0) if isinstance(demo, dict) else getattr(demo, 'age', 0)
        gender = demo.get("gender", "") if isinstance(demo, dict) else getattr(demo, 'gender', '')
        occupation = demo.get("occupation", "") if isinstance(demo, dict) else getattr(demo, 'occupation', '')
        return f"{name}，{age}岁，{gender}性，{occupation}"

    def get_state(self) -> Dict[str, Any]:
        """获取状态"""
        return {
            "id": self.id,
            "name": self.name,
            "state": self.state,
            "emotion": self.emotion,
            "emotion_intensity": self.emotion_intensity,
        }

    async def rate_survey(self, questions_summary: str = "") -> Optional[Any]:
        """Agent 对整个问卷的体验反馈"""
        demo = self.persona.get("demographics", {}) if isinstance(self.persona, dict) else (
            self.persona.demographics if hasattr(self.persona, 'demographics') else {})
        occupation = demo.get("occupation", "") if isinstance(demo, dict) else getattr(demo, 'occupation', '')

        prompt = f"""你是 {self.name}（{occupation}），刚刚完成了一份问卷调研。

问卷概况：{questions_summary}

请从以下5个维度对这份问卷进行 1~10 分的打分，并留下一句评语：

1. 问卷长度感知 (length_rating)：1=太短了，意犹未尽 → 10=太长了，希望缩短
2. 回答难度 (difficulty_rating)：1=非常容易回答 → 10=非常困难
3. 问题清晰度 (clarity_rating)：1=问题很模糊 → 10=问题非常清晰明确
4. 疲劳感受 (fatigue_rating)：1=完全没感到疲劳 → 10=极度疲劳
5. 兴趣程度 (interest_rating)：1=毫无兴趣 → 10=非常有兴趣

请以JSON格式输出：
{{
  "length_rating": 1~10的整数,
  "difficulty_rating": 1~10的整数,
  "clarity_rating": 1~10的整数,
  "fatigue_rating": 1~10的整数,
  "interest_rating": 1~10的整数,
  "comment": "你的一句话评语"
}}"""

        try:
            from ..models.scenario import SurveyFeedback
            result = await self.provider.chat_json(
                [{"role": "user", "content": prompt}],
                self.model,
                temperature=0.5,
                thinking_config=self.thinking_config,
                max_tokens_param=self.max_tokens_param,
            )
            return SurveyFeedback(
                agent_id=self.id,
                agent_name=self.name,
                length_rating=int(result.get("length_rating", 5)),
                difficulty_rating=int(result.get("difficulty_rating", 5)),
                clarity_rating=int(result.get("clarity_rating", 5)),
                fatigue_rating=int(result.get("fatigue_rating", 5)),
                interest_rating=int(result.get("interest_rating", 5)),
                comment=str(result.get("comment", "")).replace("\n", " ").replace("\r", "")[:200],
            )
        except Exception as e:
            from ..models.scenario import SurveyFeedback
            return SurveyFeedback(
                agent_id=self.id, agent_name=self.name,
                length_rating=5, difficulty_rating=5, clarity_rating=5,
                fatigue_rating=5, interest_rating=5,
                comment=f"[反馈收集失败: {str(e)[:50]}]",
            )
