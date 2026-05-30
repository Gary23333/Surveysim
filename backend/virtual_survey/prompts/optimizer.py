"""LLM优化器"""

import json
from typing import Any, Dict, Optional

from ..llm.provider import LLMProvider


class PersonaOptimizer:
    """Persona优化器"""

    def __init__(self, provider: LLMProvider, model: str):
        self.provider = provider
        self.model = model

    async def optimize(
        self,
        base_persona: Dict[str, Any],
        target_description: str,
    ) -> Dict[str, Any]:
        """
        优化Persona

        Args:
            base_persona: 基础Persona
            target_description: 目标人群描述

        Returns:
            优化后的Persona
        """
        prompt = f"""你是一位专业的人口学研究者。请基于以下基础人格模板，针对特定人群进行优化。

## 基础人格模板
名称：{base_persona.get('name', '未知')}
人口统计：
- 年龄：{base_persona.get('demographics', {}).get('age', '未知')}
- 性别：{base_persona.get('demographics', {}).get('gender', '未知')}
- 城市：{base_persona.get('demographics', {}).get('city', '未知')}
- 职业：{base_persona.get('demographics', {}).get('occupation', '未知')}
- 收入：{base_persona.get('demographics', {}).get('income', '未知')}

心理画像：
- 价值观：{', '.join(base_persona.get('psychographics', {}).get('values', []))}
- 性格特征：{', '.join(base_persona.get('psychographics', {}).get('personality_traits', []))}
- 风险偏好：{base_persona.get('psychographics', {}).get('risk_appetite', '未知')}

背景故事：
{base_persona.get('background', {}).get('life_story', '未知')}

## 目标人群描述
{target_description}

## 任务
请优化上述人格模板，使其更符合目标人群的特征。需要调整：
1. 人口统计信息（如适用）
2. 心理画像（价值观、性格特征等）
3. 背景故事（使其更贴近目标人群的生活经历）
4. 当前关注点

请以JSON格式输出优化后的完整Persona：
{{
  "name": "优化后的名称",
  "demographics": {{
    "age": 年龄,
    "gender": "性别",
    "city": "城市",
    "education": "教育水平",
    "occupation": "职业",
    "income": "收入水平"
  }},
  "psychographics": {{
    "values": ["价值观1", "价值观2"],
    "personality_traits": ["性格特征1", "性格特征2"],
    "risk_appetite": "风险偏好",
    "tech_savviness": "科技接受度"
  }},
  "background": {{
    "life_story": "详细的背景故事",
    "key_experiences": ["关键经历1", "关键经历2"],
    "current_concerns": ["当前关注1", "当前关注2"]
  }},
  "initial_attitudes": {{
    "话题": "态度"
  }}
}}"""

        result = await self.provider.chat_json(
            messages=[{"role": "user", "content": prompt}],
            model=self.model,
            temperature=0.7,
        )

        return result

    async def generate(
        self,
        description: str,
        count: int = 1,
    ) -> list:
        """
        生成Persona

        Args:
            description: 人群描述
            count: 生成数量

        Returns:
            生成的Persona列表
        """
        prompt = f"""你是一位专业的人口学研究者。请根据以下描述生成{count}个不同的人物角色。

## 人群描述
{description}

## 要求
1. 每个人物要有独特的背景和经历
2. 人口统计信息要合理
3. 心理画像要符合人物特征
4. 背景故事要详细且真实

请以JSON格式输出：
{{
  "personas": [
    {{
      "name": "姓名",
      "demographics": {{
        "age": 年龄,
        "gender": "性别",
        "city": "城市",
        "education": "教育水平",
        "occupation": "职业",
        "income": "收入水平"
      }},
      "psychographics": {{
        "values": ["价值观1", "价值观2"],
        "personality_traits": ["性格特征1", "性格特征2"],
        "risk_appetite": "风险偏好",
        "tech_savviness": "科技接受度"
      }},
      "background": {{
        "life_story": "详细的背景故事",
        "key_experiences": ["关键经历1", "关键经历2"],
        "current_concerns": ["当前关注1", "当前关注2"]
      }},
      "initial_attitudes": {{
        "话题": "态度"
      }}
    }}
  ]
}}"""

        result = await self.provider.chat_json(
            messages=[{"role": "user", "content": prompt}],
            model=self.model,
            temperature=0.8,
        )

        return result.get("personas", [result] if "name" in result else [])


class PromptOptimizer:
    """提示词优化器"""

    def __init__(self, provider: LLMProvider, model: str):
        self.provider = provider
        self.model = model

    async def optimize_behavior_prompt(
        self,
        base_prompt: str,
        target_behavior: str,
    ) -> str:
        """
        优化行为提示词

        Args:
            base_prompt: 基础提示词
            target_behavior: 目标行为描述

        Returns:
            优化后的提示词
        """
        prompt = f"""你是一位专业的提示词工程师。请优化以下行为提示词，使其更符合目标行为。

## 基础提示词
{base_prompt}

## 目标行为
{target_behavior}

## 要求
1. 保持原提示词的核心要求
2. 添加针对目标行为的具体指导
3. 使用清晰、自然的语言
4. 避免过于复杂的指令

请直接输出优化后的提示词，不需要JSON格式。"""

        result = await self.provider.chat(
            messages=[{"role": "user", "content": prompt}],
            model=self.model,
            temperature=0.7,
        )

        return result
