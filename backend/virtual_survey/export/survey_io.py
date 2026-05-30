"""问卷导入导出"""

import json
from typing import Any, Dict, List

from ..models.survey import (
    Question,
    QuestionMode,
    QuestionType,
    SurveyCreate,
    SurveyDetail,
)


class SurveyExporter:
    """问卷导出器"""

    @staticmethod
    def to_json(survey: Dict[str, Any], pretty: bool = True) -> str:
        """导出为JSON格式"""
        data = {
            "version": "1.0",
            "metadata": {
                "name": survey.get("name", ""),
                "description": survey.get("description", ""),
                "author": survey.get("metadata", {}).get("author", "Virtual Survey"),
            },
            "questions": survey.get("questions", []),
        }

        if pretty:
            return json.dumps(data, ensure_ascii=False, indent=2)
        return json.dumps(data, ensure_ascii=False)

    @staticmethod
    def to_dict(survey: Dict[str, Any]) -> Dict[str, Any]:
        """导出为字典"""
        return {
            "version": "1.0",
            "metadata": {
                "name": survey.get("name", ""),
                "description": survey.get("description", ""),
            },
            "questions": survey.get("questions", []),
        }


class SurveyImporter:
    """问卷导入器"""

    @staticmethod
    def from_json(data: Dict[str, Any]) -> SurveyDetail:
        """从JSON导入"""
        questions = []

        for q in data.get("questions", []):
            # 映射题型
            q_type = q.get("type", "open_ended")
            try:
                question_type = QuestionType(q_type)
            except ValueError:
                question_type = QuestionType.OPEN_ENDED

            # 映射模式
            q_mode = q.get("mode", "global")
            try:
                question_mode = QuestionMode(q_mode)
            except ValueError:
                question_mode = QuestionMode.GLOBAL

            question = Question(
                id=q.get("id", ""),
                type=question_type,
                text=q.get("text", q.get("title", "")),
                options=q.get("options"),
                required=q.get("required", True),
                mode=question_mode,
                visibility=q.get("visibility"),
                follow_up_prompts=q.get("follow_up_prompts", []),
            )
            questions.append(question)

        return SurveyDetail(
            id=data.get("id", ""),
            name=data.get("name", data.get("title", "")),
            description=data.get("description", ""),
            version=data.get("version", "1.0"),
            questions=questions,
        )

    @staticmethod
    def from_string(json_str: str) -> SurveyDetail:
        """从JSON字符串导入"""
        data = json.loads(json_str)
        return SurveyImporter.from_json(data)
