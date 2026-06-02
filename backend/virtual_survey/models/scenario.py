"""场景配置数据模型"""

from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class SurveyScenarioConfig(BaseModel):
    """问卷调查场景配置"""
    default_mode: str = Field(default="global", description="默认提问模式")
    default_visibility: str = Field(default="isolated", description="默认可见性")
    enable_follow_up: bool = Field(default=True, description="启用追问")
    follow_up_threshold: int = Field(default=30, description="追问阈值")


class FocusGroupScenarioConfig(BaseModel):
    """焦点小组场景配置"""
    topic: str = Field(..., description="讨论主题")
    max_rounds: int = Field(default=5, ge=1, le=20, description="最大讨论轮数")
    min_participants: int = Field(default=2, ge=2, description="最少参与人数")
    enable_moderator_guidance: bool = Field(default=True, description="启用主持人引导")


class IDIScenarioConfig(BaseModel):
    """深度访谈场景配置"""
    target_agent_id: str = Field(..., description="目标Agent ID")
    max_questions: int = Field(default=10, ge=1, le=50, description="最大问题数")
    enable_deep_follow_up: bool = Field(default=True, description="启用深度追问")
    max_follow_up_depth: int = Field(default=3, ge=1, le=10, description="最大追问深度")


class DebateScenarioConfig(BaseModel):
    """辩论讨论场景配置"""
    topic: str = Field(..., description="辩论主题")
    rounds: int = Field(default=3, ge=1, le=10, description="辩论轮数")
    pro_team_size: Optional[int] = Field(default=None, description="正方人数")
    con_team_size: Optional[int] = Field(default=None, description="反方人数")
    enable_summary: bool = Field(default=True, description="启用总结陈词")


class ScenarioConfig(BaseModel):
    """场景配置"""
    scenario_type: str = Field(..., description="场景类型")
    survey: Optional[SurveyScenarioConfig] = Field(default=None, description="问卷调查配置")
    focus_group: Optional[FocusGroupScenarioConfig] = Field(default=None, description="焦点小组配置")
    idi: Optional[IDIScenarioConfig] = Field(default=None, description="深度访谈配置")
    debate: Optional[DebateScenarioConfig] = Field(default=None, description="辩论讨论配置")


class ModeratorDecision(BaseModel):
    """主持人决策"""
    action: str = Field(..., description="动作：continue/follow_up/skip/end")
    reason: str = Field(default="", description="决策理由")
    target: Optional[str] = Field(default=None, description="目标Agent ID")
    content: Optional[str] = Field(default=None, description="主持人说的话")
    follow_up_question: Optional[str] = Field(default=None, description="追问问题")
    trigger: Optional[str] = Field(default=None, description="触发条件")


class AgentResponse(BaseModel):
    """Agent回答"""
    agent_id: str = Field(..., description="Agent ID")
    agent_name: str = Field(..., description="Agent名称")
    content: str = Field(..., description="回答内容")
    emotion: str = Field(default="neutral", description="情绪")
    emotion_intensity: float = Field(default=0.5, ge=0, le=1, description="情绪强度")
    timestamp: str = Field(..., description="时间戳")
    score: Optional[int] = Field(default=None, description="评分数值（1~10）")
    metadata: Dict = Field(default_factory=dict, description="元数据")


class FollowUpResult(BaseModel):
    """追问结果"""
    question: str = Field(..., description="追问问题")
    response: Optional[AgentResponse] = Field(default=None, description="回答")
    depth: int = Field(default=1, description="追问深度")


class QuestionResult(BaseModel):
    """问题结果"""
    question_id: str = Field(..., description="问题ID")
    question_text: str = Field(..., description="问题文本")
    responses: List[AgentResponse] = Field(default_factory=list, description="回答列表")
    follow_ups: List[FollowUpResult] = Field(default_factory=list, description="追问列表")
    ai_summary: Optional[str] = Field(default=None, description="AI 总结")


class ScenarioResult(BaseModel):
    """场景结果"""
    scenario_type: str = Field(..., description="场景类型")
    total_questions: int = Field(default=0, description="总问题数")
    total_responses: int = Field(default=0, description="总回答数")
    total_follow_ups: int = Field(default=0, description="总追问数")
    question_results: List[QuestionResult] = Field(default_factory=list, description="问题结果列表")
    summary: Optional[str] = Field(default=None, description="总结")
    emotion_distribution: Dict[str, float] = Field(default_factory=dict, description="情绪分布")
    avg_response_length: float = Field(default=0.0, description="平均回答长度")
    survey_feedback: list = Field(default_factory=list, description="问卷体验反馈")


class SurveyFeedback(BaseModel):
    """问卷体验反馈（Agent 对整个问卷的评分）"""
    agent_id: str = Field(..., description="Agent ID")
    agent_name: str = Field(..., description="Agent名称")
    length_rating: int = Field(..., ge=1, le=10, description="长度评分 1太短~10太长")
    difficulty_rating: int = Field(..., ge=1, le=10, description="难度评分 1容易~10困难")
    clarity_rating: int = Field(..., ge=1, le=10, description="清晰度评分 1模糊~10清晰")
    fatigue_rating: int = Field(..., ge=1, le=10, description="疲劳度评分 1无疲劳~10极度疲劳")
    interest_rating: int = Field(..., ge=1, le=10, description="兴趣度评分 1无兴趣~10极有兴趣")
    comment: str = Field(default="", description="文字评语")
