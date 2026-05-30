"""经历锚点管理"""

from datetime import datetime
from typing import Any, Dict, List, Optional


class ExperienceAnchor:
    """经历锚点"""

    def __init__(
        self,
        content: str,
        context: str = "",
        importance: float = 0.5,
        timestamp: Optional[datetime] = None,
    ):
        self.content = content
        self.context = context
        self.importance = importance  # 0.0 - 1.0
        self.timestamp = timestamp or datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "content": self.content,
            "context": self.context,
            "importance": self.importance,
            "timestamp": self.timestamp.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ExperienceAnchor":
        return cls(
            content=data["content"],
            context=data.get("context", ""),
            importance=data.get("importance", 0.5),
            timestamp=datetime.fromisoformat(data["timestamp"]) if "timestamp" in data else None,
        )


class ExperienceStore:
    """经历存储"""

    def __init__(self, max_anchors: int = 10):
        self.anchors: List[ExperienceAnchor] = []
        self.max_anchors = max_anchors

    def add(
        self,
        content: str,
        context: str = "",
        importance: float = 0.5,
        timestamp: Optional[datetime] = None,
    ) -> ExperienceAnchor:
        """添加经历锚点"""
        anchor = ExperienceAnchor(
            content=content,
            context=context,
            importance=importance,
            timestamp=timestamp,
        )
        self.anchors.append(anchor)

        # 按重要性排序，保留最重要的N个
        self.anchors.sort(key=lambda x: x.importance, reverse=True)
        if len(self.anchors) > self.max_anchors:
            self.anchors = self.anchors[:self.max_anchors]

        return anchor

    def get_top(self, n: int) -> List[ExperienceAnchor]:
        """获取最重要的n个经历"""
        return self.anchors[:n]

    def get_recent(self, n: int) -> List[ExperienceAnchor]:
        """获取最近的n个经历"""
        sorted_anchors = sorted(self.anchors, key=lambda x: x.timestamp, reverse=True)
        return sorted_anchors[:n]

    def format_for_prompt(self, max_anchors: Optional[int] = None) -> str:
        """格式化为prompt文本"""
        anchors = self.anchors
        if max_anchors:
            anchors = anchors[:max_anchors]

        if not anchors:
            return "暂无关键经历记录"

        lines = []
        for i, anchor in enumerate(anchors, 1):
            importance_str = f"（重要性：{anchor.importance:.1f}）"
            lines.append(f"{i}. {anchor.content}{importance_str}")

        return "\n".join(lines)

    def clear(self) -> None:
        """清空经历"""
        self.anchors.clear()

    def __len__(self) -> int:
        return len(self.anchors)

    def to_list(self) -> List[Dict[str, Any]]:
        """转换为列表"""
        return [anchor.to_dict() for anchor in self.anchors]

    @classmethod
    def from_list(cls, data: List[Dict[str, Any]], max_anchors: int = 10) -> "ExperienceStore":
        """从列表创建"""
        store = cls(max_anchors=max_anchors)
        for item in data:
            anchor = ExperienceAnchor.from_dict(item)
            store.anchors.append(anchor)
        return store
