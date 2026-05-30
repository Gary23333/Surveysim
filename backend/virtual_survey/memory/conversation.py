"""对话历史管理"""

from datetime import datetime
from typing import Any, Dict, List, Optional


class ConversationEntry:
    """对话记录"""

    def __init__(
        self,
        role: str,
        content: str,
        timestamp: Optional[datetime] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        self.role = role
        self.content = content
        self.timestamp = timestamp or datetime.now()
        self.metadata = metadata or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ConversationEntry":
        return cls(
            role=data["role"],
            content=data["content"],
            timestamp=datetime.fromisoformat(data["timestamp"]) if "timestamp" in data else None,
            metadata=data.get("metadata", {}),
        )


class ConversationHistory:
    """对话历史"""

    def __init__(self, max_size: int = 10):
        self.entries: List[ConversationEntry] = []
        self.max_size = max_size

    def add(
        self,
        role: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> ConversationEntry:
        """添加对话记录"""
        entry = ConversationEntry(role=role, content=content, metadata=metadata)
        self.entries.append(entry)

        # 滑动窗口：超过最大长度时移除最早的记录
        if len(self.entries) > self.max_size:
            self.entries.pop(0)

        return entry

    def get_recent(self, n: int) -> List[ConversationEntry]:
        """获取最近n条记录"""
        return self.entries[-n:]

    def get_filtered(
        self,
        visibility: str,
        agent_id: str,
    ) -> List[ConversationEntry]:
        """
        根据可见性过滤对话历史

        Args:
            visibility: 可见性模式（isolated/open）
            agent_id: 当前Agent ID

        Returns:
            过滤后的对话记录
        """
        if visibility == "open":
            return self.entries.copy()

        # isolated模式：只保留系统消息、主持人消息和自己的消息
        return [
            entry for entry in self.entries
            if entry.role in ["system", "moderator"] or entry.role == agent_id
        ]

    def format_for_prompt(self, max_entries: Optional[int] = None) -> str:
        """格式化为prompt文本"""
        entries = self.entries
        if max_entries:
            entries = entries[-max_entries:]

        if not entries:
            return "暂无对话历史"

        lines = []
        for entry in entries:
            role_name = self._get_role_name(entry.role)
            lines.append(f"[{entry.timestamp.strftime('%H:%M')}] {role_name}: {entry.content}")

        return "\n".join(lines)

    def _get_role_name(self, role: str) -> str:
        """获取角色名称"""
        role_names = {
            "system": "系统",
            "moderator": "主持人",
            "user": "用户",
        }
        return role_names.get(role, role)

    def clear(self) -> None:
        """清空对话历史"""
        self.entries.clear()

    def __len__(self) -> int:
        return len(self.entries)

    def to_list(self) -> List[Dict[str, Any]]:
        """转换为列表"""
        return [entry.to_dict() for entry in self.entries]

    @classmethod
    def from_list(cls, data: List[Dict[str, Any]], max_size: int = 10) -> "ConversationHistory":
        """从列表创建"""
        history = cls(max_size=max_size)
        for item in data:
            entry = ConversationEntry.from_dict(item)
            history.entries.append(entry)
        return history
