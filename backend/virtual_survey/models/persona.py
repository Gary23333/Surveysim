"""Persona相关数据模型"""

from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class Demographics(BaseModel):
    """人口统计"""
    age: int = Field(..., ge=1, le=120, description="年龄")
    gender: str = Field(..., description="性别")
    city: str = Field(..., description="居住城市")
    education: str = Field(..., description="教育水平")
    occupation: str = Field(..., description="职业")
    income: str = Field(default="", description="收入水平")
    marital_status: Optional[str] = Field(default=None, description="婚姻状况")
    has_children: Optional[bool] = Field(default=None, description="是否有子女")


class Psychographics(BaseModel):
    """心理画像"""
    values: List[str] = Field(default_factory=list, description="核心价值观")
    personality_traits: List[str] = Field(default_factory=list, description="性格特征")
    risk_appetite: str = Field(default="moderate", description="风险偏好")
    tech_savviness: str = Field(default="moderate", description="科技接受度")
    political_leaning: Optional[str] = Field(default=None, description="政治倾向")


class Background(BaseModel):
    """背景故事"""
    life_story: str = Field(default="", description="生平简述")
    key_experiences: List[str] = Field(default_factory=list, description="关键经历")
    current_concerns: List[str] = Field(default_factory=list, description="当前关注")
    daily_routine: Optional[str] = Field(default=None, description="日常生活")


class PersonaCreate(BaseModel):
    """创建Persona请求"""
    name: str = Field(..., min_length=1, max_length=100, description="人格名称")
    demographics: Demographics
    psychographics: Psychographics = Field(default_factory=Psychographics)
    background: Background = Field(default_factory=Background)
    initial_attitudes: Dict[str, str] = Field(default_factory=dict, description="初始态度")


class PersonaUpdate(BaseModel):
    """更新Persona请求"""
    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    demographics: Optional[Demographics] = None
    psychographics: Optional[Psychographics] = None
    background: Optional[Background] = None
    initial_attitudes: Optional[Dict[str, str]] = None


class PersonaSummary(BaseModel):
    """Persona摘要"""
    id: str
    name: str
    age: int
    gender: str
    occupation: str
    city: str
    groups: List[str] = Field(default_factory=list, description="所属分组名称列表")


class PersonaDetail(BaseModel):
    """Persona详情"""
    id: str
    name: str
    version: str
    template_id: Optional[str] = None
    demographics: Demographics
    psychographics: Psychographics
    background: Background
    initial_attitudes: Dict[str, str]
    groups: List[str] = Field(default_factory=list, description="所属分组名称列表")


class PersonaResponse(BaseModel):
    """Persona响应"""
    id: str
    name: str
    version: str
    groups: List[str] = Field(default_factory=list, description="所属分组名称列表")


class PersonaTemplate(BaseModel):
    """Persona模板"""
    id: str
    name: str
    emoji: str
    description: str
    demographics: Demographics
    psychographics: Psychographics
    background: Background
    initial_attitudes: Dict[str, str]


class PersonaOptimizeRequest(BaseModel):
    """Persona优化请求"""
    template_id: Optional[str] = Field(default=None, description="基础模板ID")
    persona_id: Optional[str] = Field(default=None, description="已有Persona ID")
    target_description: str = Field(..., min_length=10, description="目标人群描述")
    provider_pack: str = Field(default="OpenAI", description="用于优化的LLM Provider")
    model: str = Field(default="gpt-4o-mini", description="用于优化的模型")


class PersonaGenerateRequest(BaseModel):
    """Persona生成请求"""
    description: str = Field(..., min_length=10, description="人群描述")
    count: int = Field(default=1, ge=1, le=10, description="生成数量")


# ===== 人格分组相关模型 =====

class PersonaGroupCreate(BaseModel):
    """创建分组请求"""
    name: str = Field(..., min_length=1, max_length=100, description="分组名称")
    description: str = Field(default="", description="分组描述")
    persona_ids: List[str] = Field(default_factory=list, description="包含的人格ID列表")


class PersonaGroupUpdate(BaseModel):
    """更新分组请求"""
    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    description: Optional[str] = None
    persona_ids: Optional[List[str]] = None


class PersonaGroup(BaseModel):
    """分组"""
    id: str
    name: str
    description: str = ""
    persona_ids: List[str] = Field(default_factory=list)
    created_at: str = ""
