"""问卷相关数据模型"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class QuestionType(str, Enum):
    """问题类型"""
    SINGLE_CHOICE = "single_choice"  # 单选题
    MULTIPLE_CHOICE = "multiple_choice"  # 多选题
    OPEN_ENDED = "open_ended"  # 开放题
    SCALE = "scale"  # 量表题
    RANKING = "ranking"  # 排序题
    MATRIX = "matrix"  # 矩阵题


class QuestionMode(str, Enum):
    """提问模式"""
    GLOBAL = "global"  # 全局提问：所有Agent同时回答
    SEQUENTIAL = "sequential"  # 顺序提问：逐个Agent回答
    OPEN = "open"  # 开放场景：自由讨论


class ScaleConfig(BaseModel):
    """量表配置"""
    min_value: int = Field(default=1, description="最小值")
    max_value: int = Field(default=5, description="最大值")
    min_label: str = Field(default="非常不满意", description="最小值标签")
    max_label: str = Field(default="非常满意", description="最大值标签")
    step: int = Field(default=1, description="步长")


class RatingConfig(BaseModel):
    """评分配置（1~10 打分）"""
    min_value: int = Field(default=1, description="最小值")
    max_value: int = Field(default=10, description="最大值")
    min_label: str = Field(default="非常不满意", description="最小值标签")
    max_label: str = Field(default="非常满意", description="最大值标签")


class FollowUpPrompt(BaseModel):
    """追问配置"""
    condition: str = Field(..., description="触发条件，如 'answer.length < 50'")
    prompt: str = Field(..., description="追问文本")


class QuestionCreate(BaseModel):
    """创建问题请求"""
    type: QuestionType = Field(..., description="问题类型")
    text: str = Field(..., min_length=1, description="问题文本")
    options: Optional[List[str]] = Field(default=None, description="选项（选择题）")
    scale_config: Optional[ScaleConfig] = Field(default=None, description="量表配置")
    required: bool = Field(default=True, description="是否必答")
    mode: QuestionMode = Field(default=QuestionMode.GLOBAL, description="提问模式")
    visibility: Optional[str] = Field(default=None, description="可见性")
    follow_up_prompts: List[FollowUpPrompt] = Field(default_factory=list, description="预设追问")
    enable_text: bool = Field(default=True, description="启用文字回答")
    enable_rating: bool = Field(default=False, description="启用程度评分")
    rating_config: Optional[RatingConfig] = Field(default=None, description="评分配置")


class QuestionUpdate(BaseModel):
    """更新问题请求"""
    type: Optional[QuestionType] = None
    text: Optional[str] = Field(default=None, min_length=1)
    options: Optional[List[str]] = None
    scale_config: Optional[ScaleConfig] = None
    required: Optional[bool] = None
    mode: Optional[QuestionMode] = None
    visibility: Optional[str] = None
    follow_up_prompts: Optional[List[FollowUpPrompt]] = None
    enable_text: Optional[bool] = None
    enable_rating: Optional[bool] = None
    rating_config: Optional[RatingConfig] = None


class Question(BaseModel):
    """问题"""
    id: str = Field(..., description="问题ID")
    type: QuestionType = Field(..., description="问题类型")
    text: str = Field(..., description="问题文本")
    options: Optional[List[str]] = Field(default=None, description="选项")
    scale_config: Optional[ScaleConfig] = Field(default=None, description="量表配置")
    required: bool = Field(default=True, description="是否必答")
    mode: QuestionMode = Field(default=QuestionMode.GLOBAL, description="提问模式")
    visibility: Optional[str] = Field(default=None, description="可见性")
    follow_up_prompts: List[FollowUpPrompt] = Field(default_factory=list, description="预设追问")
    enable_text: bool = Field(default=True, description="启用文字回答")
    enable_rating: bool = Field(default=False, description="启用程度评分")
    rating_config: Optional[RatingConfig] = Field(default=None, description="评分配置")


class SurveyMetadata(BaseModel):
    """问卷元数据"""
    author: Optional[str] = Field(default=None, description="作者")
    created_at: Optional[datetime] = Field(default=None, description="创建时间")
    updated_at: Optional[datetime] = Field(default=None, description="更新时间")
    tags: List[str] = Field(default_factory=list, description="标签")
    version: str = Field(default="1.0", description="版本")


class SurveyCreate(BaseModel):
    """创建问卷请求"""
    name: str = Field(..., min_length=1, max_length=200, description="问卷名称")
    description: str = Field(default="", description="问卷描述")
    questions: List[QuestionCreate] = Field(default_factory=list, description="问题列表")
    metadata: Optional[SurveyMetadata] = Field(default=None, description="元数据")
    scenario_type: Optional[str] = Field(default="survey", description="场景类型")


class SurveyUpdate(BaseModel):
    """更新问卷请求"""
    name: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = None
    questions: Optional[List[QuestionCreate]] = None
    metadata: Optional[SurveyMetadata] = None
    scenario_type: Optional[str] = None


class SurveySummary(BaseModel):
    """问卷摘要"""
    id: str
    name: str
    description: str
    question_count: int
    version: str
    created_at: Optional[datetime] = None
    scenario_type: Optional[str] = "survey"


class SurveyDetail(BaseModel):
    """问卷详情"""
    id: str
    name: str
    description: str
    version: str
    questions: List[Question]
    metadata: Optional[SurveyMetadata] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    scenario_type: Optional[str] = "survey"


class SurveyResponse(BaseModel):
    """问卷响应"""
    id: str
    name: str
    question_count: int


class SurveyTemplate(BaseModel):
    """问卷模板"""
    id: str
    name: str
    description: str
    category: str
    questions: List[Question]
    scenario_type: Optional[str] = "survey"


class SurveyImportRequest(BaseModel):
    """问卷导入请求"""
    format: str = Field(default="auto", description="格式：auto/json/wenjuanxing/tencent")
