"""任务相关数据模型"""

from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class TaskStatus(str, Enum):
    """任务状态"""
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    ERROR = "error"
    STOPPED = "stopped"


class ScenarioType(str, Enum):
    """调研场景类型"""
    SURVEY = "survey"  # 问卷调查
    FOCUS_GROUP = "focus_group"  # 焦点小组
    IDI = "idi"  # 深度访谈
    DEBATE = "debate"  # 辩论讨论


class Visibility(str, Enum):
    """可见性模式"""
    ISOLATED = "isolated"  # 隔离：只看到自己和主持人
    OPEN = "open"  # 开放：看到所有人的对话


class ModeratorType(str, Enum):
    """主持人类型"""
    AI = "ai"
    HUMAN = "human"


class MemoryConfig(BaseModel):
    """记忆配置"""
    history_size: int = Field(default=10, description="对话历史窗口大小")
    max_anchors: int = Field(default=10, description="最大经历锚点数")
    enable_attitude_tracking: bool = Field(default=True, description="启用态度追踪")


class AgentConfig(BaseModel):
    """Agent配置"""
    id: str = Field(..., description="Agent ID")
    name: str = Field(..., description="显示名称")
    persona_id: str = Field(..., description="关联的Persona ID")
    provider_pack: str = Field(..., description="LLM配置包名称")
    model: str = Field(..., description="模型名称")
    behavior_prompt_id: str = Field(..., description="行为提示词ID")
    memory_config: MemoryConfig = Field(default_factory=MemoryConfig, description="记忆配置")
    thinking_enabled: bool = Field(default=False, description="启用思考模式")
    thinking_intensity: str = Field(default="medium", description="思考强度: low/medium/high/max/minimal")


class ModeratorConfig(BaseModel):
    """主持人配置"""
    type: ModeratorType = Field(default=ModeratorType.AI, description="主持人类型")
    provider_pack: Optional[str] = Field(default=None, description="AI主持人LLM配置包")
    model: Optional[str] = Field(default=None, description="AI主持人模型")
    behavior_prompt_id: str = Field(default="neutral", description="主持人行为提示词ID")
    human_name: Optional[str] = Field(default=None, description="人类主持人名称")
    thinking_enabled: bool = Field(default=False, description="启用思考模式")
    thinking_intensity: str = Field(default="medium", description="思考强度")


class TaskSettings(BaseModel):
    """任务设置"""
    default_visibility: Visibility = Field(
        default=Visibility.ISOLATED,
        description="默认可见性"
    )
    auto_follow_up: bool = Field(default=True, description="是否自动追问")
    follow_up_threshold: int = Field(default=30, description="追问阈值（回答长度）")
    max_follow_up_depth: int = Field(default=3, description="最大追问深度")
    delay_between_questions: float = Field(default=2.0, description="问题间隔（秒）")
    memory_window_size: int = Field(default=10, description="记忆窗口大小")


class Task(BaseModel):
    """任务"""
    id: str = Field(..., description="任务ID")
    name: str = Field(..., min_length=1, max_length=200, description="任务名称")
    description: str = Field(default="", description="任务描述")
    scenario_type: ScenarioType = Field(default=ScenarioType.SURVEY, description="场景类型")
    status: TaskStatus = Field(default=TaskStatus.PENDING, description="任务状态")
    survey_id: str = Field(..., description="关联问卷ID")
    agents: List[AgentConfig] = Field(..., min_length=1, description="Agent配置列表")
    moderator: ModeratorConfig = Field(default_factory=ModeratorConfig, description="主持人配置")
    settings: TaskSettings = Field(default_factory=TaskSettings, description="任务设置")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    started_at: Optional[datetime] = Field(default=None, description="开始时间")
    completed_at: Optional[datetime] = Field(default=None, description="完成时间")
    error_message: Optional[str] = Field(default=None, description="错误信息")


class TaskCreate(BaseModel):
    """创建任务请求"""
    name: str = Field(..., min_length=1, max_length=200, description="任务名称")
    description: str = Field(default="", description="任务描述")
    scenario_type: ScenarioType = Field(default=ScenarioType.SURVEY, description="场景类型")
    survey_id: str = Field(..., description="关联问卷ID")
    agents: List[AgentConfig] = Field(..., min_length=1, description="Agent配置列表")
    moderator: ModeratorConfig = Field(default_factory=ModeratorConfig, description="主持人配置")
    settings: TaskSettings = Field(default_factory=TaskSettings, description="任务设置")


class TaskUpdate(BaseModel):
    """更新任务请求"""
    name: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = None
    settings: Optional[TaskSettings] = None


class TaskSummary(BaseModel):
    """任务摘要"""
    id: str
    name: str
    scenario_type: ScenarioType
    status: TaskStatus
    agent_count: int
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    progress: Optional[dict] = Field(default=None, description="进度信息 {current, total, answered}")


class TaskDetail(BaseModel):
    """任务详情"""
    id: str
    name: str
    description: str
    scenario_type: ScenarioType
    status: TaskStatus
    survey_id: str
    agents: List[AgentConfig]
    moderator: ModeratorConfig
    settings: TaskSettings
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None


class TaskResponse(BaseModel):
    """任务响应"""
    id: str
    name: str
    scenario_type: ScenarioType
    status: TaskStatus
    created_at: datetime


class TaskResults(BaseModel):
    """任务结果"""
    task_id: str
    status: str
    scenario_type: str = ""
    total_questions: int = 0
    total_responses: int = 0
    total_follow_ups: int = 0
    avg_response_length: float = 0.0
    emotion_distribution: dict = Field(default_factory=dict)
    question_results: list = Field(default_factory=list)
    summary: str = ""
    agents: list = Field(default_factory=list)
    survey_feedback: list = Field(default_factory=list)
    summary: str = ""
