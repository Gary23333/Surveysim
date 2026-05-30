"""记忆存储整合"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from .attitude import AttitudeState
from .conversation import ConversationHistory
from .experience import ExperienceStore


class AgentMemory:
    """Agent记忆系统"""

    def __init__(
        self,
        agent_id: str,
        history_size: int = 10,
        max_anchors: int = 10,
    ):
        self.agent_id = agent_id
        self.conversation = ConversationHistory(max_size=history_size)
        self.attitudes = AttitudeState()
        self.experiences = ExperienceStore(max_anchors=max_anchors)

    def get_prompt_context(self, visibility: str = "isolated") -> str:
        """
        获取记忆上下文（用于注入prompt）

        Args:
            visibility: 可见性模式

        Returns:
            格式化的记忆上下文
        """
        # 对话历史
        history = self.conversation.get_filtered(visibility, self.agent_id)
        history_text = self._format_history(history)

        # 态度状态
        attitudes_text = self.attitudes.format_for_prompt()

        # 经历锚点
        experiences_text = self.experiences.format_for_prompt()

        return f"""
## 近期对话
{history_text}

## 当前态度
{attitudes_text}

## 关键经历
{experiences_text}
"""

    def _format_history(self, entries: list) -> str:
        """格式化对话历史"""
        if not entries:
            return "暂无对话历史"

        lines = []
        for entry in entries[-5:]:  # 只显示最近5条
            role_name = self._get_role_name(entry.role)
            lines.append(f"[{entry.timestamp.strftime('%H:%M')}] {role_name}: {entry.content[:100]}...")

        return "\n".join(lines)

    def _get_role_name(self, role: str) -> str:
        """获取角色名称"""
        role_names = {
            "system": "系统",
            "moderator": "主持人",
            "user": "用户",
        }
        return role_names.get(role, role)

    def update_from_response(
        self,
        question: str,
        response: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """从回答中更新记忆"""
        # 添加对话记录
        self.conversation.add("user", question)
        self.conversation.add(self.agent_id, response, metadata)

    def update_attitude(
        self,
        topic: str,
        stance: str,
        intensity: float,
        context: str = "",
    ) -> None:
        """更新态度"""
        self.attitudes.update(
            topic=topic,
            stance=stance,
            intensity=intensity,
            context=context,
        )

    def add_experience(
        self,
        content: str,
        context: str = "",
        importance: float = 0.5,
    ) -> None:
        """添加经历"""
        self.experiences.add(
            content=content,
            context=context,
            importance=importance,
        )

    def clear(self) -> None:
        """清空所有记忆"""
        self.conversation.clear()
        self.attitudes = AttitudeState()
        self.experiences.clear()

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "agent_id": self.agent_id,
            "conversation": self.conversation.to_list(),
            "attitudes": self.attitudes.to_dict(),
            "experiences": self.experiences.to_list(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgentMemory":
        """从字典创建"""
        memory = cls(agent_id=data["agent_id"])
        memory.conversation = ConversationHistory.from_list(data.get("conversation", []))
        memory.attitudes = AttitudeState.from_dict(data.get("attitudes", {}))
        memory.experiences = ExperienceStore.from_list(data.get("experiences", []))
        return memory


class MemoryManager:
    """记忆管理器"""

    def __init__(self):
        self._memories: Dict[str, AgentMemory] = {}

    def get_or_create(
        self,
        agent_id: str,
        history_size: int = 10,
        max_anchors: int = 10,
    ) -> AgentMemory:
        """获取或创建Agent记忆"""
        if agent_id not in self._memories:
            self._memories[agent_id] = AgentMemory(
                agent_id=agent_id,
                history_size=history_size,
                max_anchors=max_anchors,
            )
        return self._memories[agent_id]

    def get(self, agent_id: str) -> Optional[AgentMemory]:
        """获取Agent记忆"""
        return self._memories.get(agent_id)

    def remove(self, agent_id: str) -> bool:
        """移除Agent记忆"""
        if agent_id in self._memories:
            del self._memories[agent_id]
            return True
        return False

    def clear(self) -> None:
        """清空所有记忆"""
        self._memories.clear()

    def list_agents(self) -> List[str]:
        """列出所有Agent ID"""
        return list(self._memories.keys())

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            agent_id: memory.to_dict()
            for agent_id, memory in self._memories.items()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MemoryManager":
        """从字典创建"""
        manager = cls()
        for agent_id, memory_data in data.items():
            memory = AgentMemory.from_dict(memory_data)
            manager._memories[agent_id] = memory
        return manager


# 全局记忆管理器实例
memory_manager = MemoryManager()
