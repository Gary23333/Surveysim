"""问卷格式兼容"""

import uuid
from typing import Any, Dict, List

from ..models.survey import Question, QuestionType, SurveyDetail


class WenjuanxingAdapter:
    """问卷星格式适配器"""

    @staticmethod
    def parse(data: Dict[str, Any]) -> SurveyDetail:
        """解析问卷星格式"""
        questions = []

        for i, q in enumerate(data.get("questions", [])):
            q_type = q.get("type")

            # 映射题型
            if q_type == "radio":
                question_type = QuestionType.SINGLE_CHOICE
            elif q_type == "checkbox":
                question_type = QuestionType.MULTIPLE_CHOICE
            elif q_type == "textarea":
                question_type = QuestionType.OPEN_ENDED
            elif q_type == "matrix":
                question_type = QuestionType.MATRIX
            elif q_type == "scale":
                question_type = QuestionType.SCALE
            else:
                question_type = QuestionType.OPEN_ENDED

            question = Question(
                id=f"q{i+1}",
                type=question_type,
                text=q.get("title", ""),
                options=q.get("options", []),
                required=q.get("required", True),
                mode="global",
                visibility="isolated",
            )
            questions.append(question)

        return SurveyDetail(
            id=str(uuid.uuid4()),
            name=data.get("title", ""),
            description=data.get("description", ""),
            version="1.0",
            questions=questions,
        )

    @staticmethod
    def export(survey: Dict[str, Any]) -> Dict[str, Any]:
        """导出为问卷星格式"""
        questions = []

        for q in survey.get("questions", []):
            q_type = q.get("type")

            # 映射题型
            if q_type == "single_choice":
                type_str = "radio"
            elif q_type == "multiple_choice":
                type_str = "checkbox"
            elif q_type == "open_ended":
                type_str = "textarea"
            else:
                type_str = "text"

            questions.append({
                "type": type_str,
                "title": q.get("text", ""),
                "options": q.get("options", []),
                "required": q.get("required", True),
            })

        return {
            "title": survey.get("name", ""),
            "description": survey.get("description", ""),
            "questions": questions,
        }


class TencentSurveyAdapter:
    """腾讯问卷格式适配器"""

    # 腾讯问卷题型映射
    TYPE_MAPPING = {
        1: QuestionType.SINGLE_CHOICE,
        2: QuestionType.MULTIPLE_CHOICE,
        3: QuestionType.OPEN_ENDED,
        4: QuestionType.SCALE,
        5: QuestionType.RANKING,
        6: QuestionType.MATRIX,
    }

    @staticmethod
    def parse(data: Dict[str, Any]) -> SurveyDetail:
        """解析腾讯问卷格式"""
        questions = []

        for i, q in enumerate(data.get("questions", [])):
            # 获取题型
            q_type = q.get("type", 3)
            question_type = TencentSurveyAdapter.TYPE_MAPPING.get(
                q_type, QuestionType.OPEN_ENDED
            )

            question = Question(
                id=f"q{i+1}",
                type=question_type,
                text=q.get("title", ""),
                options=[opt.get("text") for opt in q.get("options", [])],
                required=q.get("required", True),
                mode="global",
                visibility="isolated",
            )
            questions.append(question)

        return SurveyDetail(
            id=str(uuid.uuid4()),
            name=data.get("name", ""),
            description=data.get("description", ""),
            version="1.0",
            questions=questions,
        )

    @staticmethod
    def export(survey: Dict[str, Any]) -> Dict[str, Any]:
        """导出为腾讯问卷格式"""
        questions = []

        for q in survey.get("questions", []):
            q_type = q.get("type")

            # 映射题型
            if q_type == "single_choice":
                type_int = 1
            elif q_type == "multiple_choice":
                type_int = 2
            elif q_type == "open_ended":
                type_int = 3
            elif q_type == "scale":
                type_int = 4
            elif q_type == "ranking":
                type_int = 5
            else:
                type_int = 3

            questions.append({
                "type": type_int,
                "title": q.get("text", ""),
                "options": [{"text": opt} for opt in q.get("options", [])],
                "required": q.get("required", True),
            })

        return {
            "name": survey.get("name", ""),
            "description": survey.get("description", ""),
            "questions": questions,
        }
