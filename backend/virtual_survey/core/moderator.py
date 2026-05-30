"""AI主持人"""

import json
from datetime import datetime
from typing import Any, Dict, List, Optional

from ..llm.provider import LLMProvider
from ..models.scenario import AgentResponse, ModeratorDecision


class AIModerator:
    """AI主持人"""

    def __init__(self, provider: LLMProvider, model: str, behavior_prompt: str = "",
                 thinking_enabled: bool = False, thinking_intensity: str = "medium",
                 thinking_config: Any = None, max_tokens_param: str = "max_tokens"):
        self.provider = provider
        self.model = model
        self.behavior_prompt = behavior_prompt
        self.thinking_enabled = thinking_enabled
        self.thinking_intensity = thinking_intensity
        self.thinking_config = thinking_config
        self.max_tokens_param = max_tokens_param
        self.decision_history: List[ModeratorDecision] = []

    def _chat_kwargs(self, temperature: float = 0.7) -> Dict[str, Any]:
        return dict(
            thinking_enabled=self.thinking_enabled,
            thinking_intensity=self.thinking_intensity,
            thinking_config=self.thinking_config,
            max_tokens_param=self.max_tokens_param,
            temperature=temperature,
        )

    async def generate_opening(
        self,
        topic: str,
        agents: List[Any],
    ) -> str:
        agents_desc = "\n".join([f"- {a.name}" for a in agents])
        prompt = f"""你是一位专业的调研主持人。请为以下调研活动生成开场白。

调研主题：{topic}

参与者：
{agents_desc}

要求：
1. 简洁友好，不超过100字
2. 说明调研目的
3. 介绍参与者（不透露AI身份）
4. 营造轻松氛围
5. 引导开始讨论

请直接输出开场白内容，不需要JSON格式。"""

        return await self.provider.chat(
            [{"role": "user", "content": prompt}],
            self.model,
            **self._chat_kwargs(0.7),
        )

    async def evaluate_response(
        self,
        question: str,
        response: AgentResponse,
        agent: Any,
    ) -> ModeratorDecision:
        demo = agent.persona.get("demographics", {}) if isinstance(agent.persona, dict) else getattr(agent.persona, 'demographics', {})
        occupation = demo.get("occupation", "") if isinstance(demo, dict) else getattr(demo, 'occupation', '')

        prompt = f"""你是一位专业的调研主持人。请评估以下回答是否需要追问。

问题：{question}
回答者：{agent.name}（{occupation}）
回答内容：{response.content}
回答长度：{len(response.content)}字

判断标准：
1. 回答过短（<30字）→ 追问详情
2. 回答模糊（"还行"、"一般"、"还好"）→ 追问具体
3. 与之前态度矛盾 → 温和指出并询问
4. 与人设不符 → 确认理解
5. 回答完整详细 → 继续下一题

请以JSON格式输出：
{{
  "action": "continue" | "follow_up",
  "reason": "判断理由",
  "target": "agent_id 或 null",
  "content": "主持人说的话（如果action是follow_up）",
  "follow_up_question": "追问问题（如果action是follow_up）",
  "trigger": "触发条件：length/vague/contradiction/anomaly"
}}"""

        result = await self.provider.chat_json(
            [{"role": "user", "content": prompt}],
            self.model,
            **self._chat_kwargs(0.3),
        )

        decision = ModeratorDecision(
            action=result.get("action", "continue"),
            reason=result.get("reason", ""),
            target=result.get("target"),
            content=result.get("content"),
            follow_up_question=result.get("follow_up_question"),
            trigger=result.get("trigger"),
        )

        self.decision_history.append(decision)
        return decision

    async def generate_follow_up(
        self,
        original_question: str,
        response: str,
        trigger: str,
    ) -> str:
        trigger_prompts = {
            "length": "回答过于简短，需要更多细节",
            "vague": "回答模糊，需要更具体",
            "contradiction": "回答与之前态度矛盾，需要澄清",
            "anomaly": "回答与人设不符，需要确认",
        }
        trigger_desc = trigger_prompts.get(trigger, "需要深入了解")

        prompt = f"""你是一位专业的调研主持人。请生成一个追问问题。

原问题：{original_question}
回答：{response}
追问原因：{trigger_desc}

要求：
1. 追问要自然，不像审问
2. 针对回答中的具体内容
3. 引导受访者展开说明
4. 不要重复原问题

请直接输出追问问题，不需要JSON格式。"""

        return await self.provider.chat(
            [{"role": "user", "content": prompt}],
            self.model,
            **self._chat_kwargs(0.7),
        )

    async def generate_guidance(
        self,
        topic: str,
        recent_responses: List[AgentResponse],
        round_num: int,
    ) -> Optional[str]:
        if not recent_responses:
            return None

        responses_summary = "\n".join(
            [f"- {r.agent_name}: {r.content[:50]}..." for r in recent_responses[:5]]
        )

        prompt = f"""你是一位焦点小组主持人。讨论已进行{round_num + 1}轮。

主题：{topic}

最近发言：
{responses_summary}

请判断是否需要引导讨论，如果需要请生成引导语。

引导方向：
1. 如果讨论偏离主题 → 温和拉回
2. 如果有人沉默太久 → 邀请发言
3. 如果讨论陷入僵局 → 提出新角度
4. 如果讨论充分 → 可以结束

请以JSON格式输出：
{{
  "should_guide": true/false,
  "guidance": "引导语（如果should_guide为true）",
  "reason": "判断理由"
}}"""

        result = await self.provider.chat_json(
            [{"role": "user", "content": prompt}],
            self.model,
            **self._chat_kwargs(0.5),
        )

        if result.get("should_guide"):
            return result.get("guidance")
        return None

    async def generate_summary(
        self,
        topic: str,
        all_responses: List[AgentResponse],
    ) -> str:
        key_points = []
        for response in all_responses[:20]:
            if len(response.content) > 30:
                key_points.append(f"- {response.agent_name}: {response.content[:100]}...")

        points_text = "\n".join(key_points) if key_points else "暂无详细讨论"

        prompt = f"""你是一位专业的调研主持人。请为以下讨论生成总结。

主题：{topic}

讨论要点：
{points_text}

要求：
1. 总结主要观点和共识
2. 指出分歧和争议
3. 提炼关键洞察
4. 不超过200字

请直接输出总结内容，不需要JSON格式。"""

        return await self.provider.chat(
            [{"role": "user", "content": prompt}],
            self.model,
            **self._chat_kwargs(0.5),
        )
