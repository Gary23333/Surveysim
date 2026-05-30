"""态度状态管理"""

from datetime import datetime
from typing import Any, Dict, List, Optional


class AttitudeChange:
    """态度变化"""

    def __init__(
        self,
        stance: str,
        intensity: float,
        context: str = "",
        timestamp: Optional[datetime] = None,
    ):
        self.stance = stance  # positive/negative/neutral/mixed
        self.intensity = intensity  # 0.0 - 1.0
        self.context = context
        self.timestamp = timestamp or datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stance": self.stance,
            "intensity": self.intensity,
            "context": self.context,
            "timestamp": self.timestamp.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AttitudeChange":
        return cls(
            stance=data["stance"],
            intensity=data["intensity"],
            context=data.get("context", ""),
            timestamp=datetime.fromisoformat(data["timestamp"]) if "timestamp" in data else None,
        )


class AttitudeTimeline:
    """态度时间线"""

    def __init__(self, topic: str):
        self.topic = topic
        self.changes: List[AttitudeChange] = []

    def add_change(
        self,
        stance: str,
        intensity: float,
        context: str = "",
        timestamp: Optional[datetime] = None,
    ) -> AttitudeChange:
        """添加态度变化"""
        change = AttitudeChange(
            stance=stance,
            intensity=intensity,
            context=context,
            timestamp=timestamp,
        )
        self.changes.append(change)
        return change

    def get_current(self) -> Optional[AttitudeChange]:
        """获取当前态度"""
        return self.changes[-1] if self.changes else None

    def get_trend(self) -> str:
        """获取态度趋势"""
        if len(self.changes) < 2:
            return "stable"

        recent = self.changes[-3:] if len(self.changes) >= 3 else self.changes
        intensities = [c.intensity for c in recent]

        # 计算趋势
        if all(intensities[i] <= intensities[i + 1] for i in range(len(intensities) - 1)):
            return "improving"
        elif all(intensities[i] >= intensities[i + 1] for i in range(len(intensities) - 1)):
            return "declining"
        else:
            return "fluctuating"

    def format_for_prompt(self) -> str:
        """格式化为prompt文本"""
        if not self.changes:
            return f"- {self.topic}: 未知"

        current = self.get_current()
        if not current:
            return f"- {self.topic}: 未知"

        stance_labels = {
            "positive": "积极",
            "negative": "消极",
            "neutral": "中立",
            "mixed": "复杂",
        }
        stance_label = stance_labels.get(current.stance, current.stance)
        trend = self.get_trend()
        trend_labels = {
            "improving": "上升",
            "declining": "下降",
            "stable": "稳定",
            "fluctuating": "波动",
        }
        trend_label = trend_labels.get(trend, trend)

        return f"- {self.topic}: {stance_label}（强度{current.intensity:.1f}，趋势{trend_label}）"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "topic": self.topic,
            "changes": [c.to_dict() for c in self.changes],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AttitudeTimeline":
        timeline = cls(topic=data["topic"])
        for change_data in data.get("changes", []):
            change = AttitudeChange.from_dict(change_data)
            timeline.changes.append(change)
        return timeline


class AttitudeState:
    """态度状态"""

    def __init__(self):
        self.attitudes: Dict[str, AttitudeTimeline] = {}

    def update(
        self,
        topic: str,
        stance: str,
        intensity: float,
        context: str = "",
        timestamp: Optional[datetime] = None,
    ) -> None:
        """更新态度"""
        if topic not in self.attitudes:
            self.attitudes[topic] = AttitudeTimeline(topic)

        self.attitudes[topic].add_change(
            stance=stance,
            intensity=intensity,
            context=context,
            timestamp=timestamp,
        )

    def get_attitude(self, topic: str) -> Optional[AttitudeTimeline]:
        """获取话题态度"""
        return self.attitudes.get(topic)

    def get_all_topics(self) -> List[str]:
        """获取所有话题"""
        return list(self.attitudes.keys())

    def format_for_prompt(self) -> str:
        """格式化为prompt文本"""
        if not self.attitudes:
            return "暂无态度记录"

        lines = []
        for timeline in self.attitudes.values():
            lines.append(timeline.format_for_prompt())

        return "\n".join(lines)

    def to_dict(self) -> Dict[str, Any]:
        return {
            topic: timeline.to_dict()
            for topic, timeline in self.attitudes.items()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AttitudeState":
        state = cls()
        for topic, timeline_data in data.items():
            timeline = AttitudeTimeline.from_dict(timeline_data)
            state.attitudes[topic] = timeline
        return state
