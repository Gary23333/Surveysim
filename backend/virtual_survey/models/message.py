"""WebSocket消息数据模型"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class MessageType(str, Enum):
    """消息类型"""
    # Server -> Client
    AGENT_RESPONSE = "agent_response"
    AGENT_STATE = "agent_state"
    SYSTEM_EVENT = "system_event"
    EMOTION_BROADCAST = "emotion_broadcast"
    HEARTBEAT = "heartbeat"
    ERROR = "error"
    HISTORY = "history"

    # Client -> Server
    MODERATOR_COMMAND = "moderator_command"
    MODERATOR_TAKEOVER = "moderator_takeover"
    REQUEST_STATUS = "request_status"
    REQUEST_HISTORY = "request_history"


class AgentState(str, Enum):
    """Agent状态"""
    IDLE = "idle"
    THINKING = "thinking"
    RESPONDING = "responding"
    ERROR = "error"


class ProgressInfo(BaseModel):
    """进度信息"""
    current: int = Field(default=0, description="当前问题索引")
    total: int = Field(default=0, description="总问题数")


# ============ Server -> Client Messages ============

class AgentResponseMessage(BaseModel):
    """Agent回答消息"""
    type: str = Field(default="agent_response", description="消息类型")
    agent_id: str = Field(..., description="Agent ID")
    agent_name: str = Field(..., description="Agent名称")
    content: str = Field(..., description="回答内容")
    emotion: str = Field(default="neutral", description="情绪")
    emotion_intensity: float = Field(default=0.5, ge=0, le=1, description="情绪强度")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat(), description="时间戳")
    question_id: Optional[str] = Field(default=None, description="问题ID")


class AgentStateMessage(BaseModel):
    """Agent状态消息"""
    type: str = Field(default="agent_state", description="消息类型")
    agent_id: str = Field(..., description="Agent ID")
    state: AgentState = Field(..., description="Agent状态")
    emotion: str = Field(default="neutral", description="情绪")
    progress: Optional[ProgressInfo] = Field(default=None, description="进度信息")


class SystemEventMessage(BaseModel):
    """系统事件消息"""
    type: str = Field(default="system_event", description="消息类型")
    event: str = Field(..., description="事件类型")
    data: Dict[str, Any] = Field(default_factory=dict, description="事件数据")


class EmotionBroadcastMessage(BaseModel):
    """情绪广播消息"""
    type: str = Field(default="emotion_broadcast", description="消息类型")
    agent_id: str = Field(..., description="Agent ID")
    agent_name: str = Field(..., description="Agent名称")
    emotion: str = Field(..., description="情绪")
    intensity: float = Field(..., ge=0, le=1, description="强度")
    context: str = Field(default="", description="上下文")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat(), description="时间戳")


class HeartbeatMessage(BaseModel):
    """心跳消息"""
    type: str = Field(default="heartbeat", description="消息类型")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat(), description="时间戳")


class ErrorMessage(BaseModel):
    """错误消息"""
    type: str = Field(default="error", description="消息类型")
    message: str = Field(..., description="错误信息")
    code: Optional[str] = Field(default=None, description="错误代码")


# ============ Client -> Server Messages ============

class ModeratorCommandMessage(BaseModel):
    """主持人指令消息"""
    type: str = Field(default="moderator_command", description="消息类型")
    command: str = Field(..., description="指令类型：ask_question/follow_up/skip/change_visibility/end")
    target: Optional[str] = Field(default=None, description="目标Agent ID，空=全部")
    question: Optional[str] = Field(default=None, description="问题内容")
    visibility: Optional[str] = Field(default=None, description="可见性")


class ModeratorTakeoverMessage(BaseModel):
    """主持人接管消息"""
    type: str = Field(default="moderator_takeover", description="消息类型")
    action: str = Field(..., description="动作：takeover/release")
    human_name: Optional[str] = Field(default=None, description="人类主持人名称")


class RequestStatusMessage(BaseModel):
    """请求状态消息"""
    type: str = Field(default="request_status", description="消息类型")


class RequestHistoryMessage(BaseModel):
    """请求历史消息"""
    type: str = Field(default="request_history", description="消息类型")


# ============ Union Types ============

class WSMessage(BaseModel):
    """WebSocket消息基类"""
    type: str = Field(..., description="消息类型")


class TaskStatusData(BaseModel):
    """任务状态数据"""
    task_id: str
    status: str
    agents: Dict[str, Any]
    progress: ProgressInfo
