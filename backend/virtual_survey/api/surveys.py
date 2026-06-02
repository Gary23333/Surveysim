"""问卷API"""

import json
import uuid
from typing import List, Optional

from fastapi import APIRouter, HTTPException, UploadFile

from ..export.compatibility import WenjuanxingAdapter
from ..export.survey_io import SurveyExporter, SurveyImporter
from ..models.survey import (
    SurveyCreate,
    SurveyDetail,
    SurveyResponse,
    SurveySummary,
    SurveyTemplate,
    SurveyUpdate,
)
from ..storage.config_store import survey_store

router = APIRouter(prefix="/api/v1/surveys", tags=["surveys"])


@router.post("/", response_model=SurveyResponse)
async def create_survey(survey_data: SurveyCreate):
    """创建问卷"""
    survey_id = str(uuid.uuid4())

    # 转换为字典
    data = survey_data.dict()
    data["id"] = survey_id
    data["version"] = "1.0"

    # 保存
    survey_store.save_custom(survey_id, data)

    return SurveyResponse(
        id=survey_id,
        name=survey_data.name,
        question_count=len(survey_data.questions),
    )


@router.get("/", response_model=List[SurveySummary])
async def list_surveys():
    """获取问卷列表"""
    surveys = []

    # 自定义问卷
    for survey in survey_store.list_custom():
        surveys.append(SurveySummary(
            id=survey.get("id", ""),
            name=survey.get("name", ""),
            description=survey.get("description", ""),
            question_count=len(survey.get("questions", [])),
            version=survey.get("version", "1.0"),
            scenario_type=survey.get("scenario_type", "survey"),
        ))

    return surveys


@router.get("/templates", response_model=List[SurveyTemplate])
async def list_survey_templates():
    """获取问卷模板列表"""
    templates = []

    for template in survey_store.list_templates():
        templates.append(SurveyTemplate(
            id=template.get("id", ""),
            name=template.get("name", ""),
            description=template.get("description", ""),
            category=template.get("category", ""),
            questions=template.get("questions", []),
            scenario_type=template.get("scenario_type", "survey"),
        ))

    return templates


@router.get("/{survey_id}", response_model=SurveyDetail)
async def get_survey(survey_id: str):
    """获取问卷详情"""
    # 先从自定义问卷查找
    survey = survey_store.get_custom(survey_id)

    # 再从模板查找
    if not survey:
        survey = survey_store.get_template(survey_id)

    if not survey:
        raise HTTPException(status_code=404, detail="Survey not found")

    return SurveyDetail(
        id=survey.get("id", survey_id),
        name=survey.get("name", ""),
        description=survey.get("description", ""),
        version=survey.get("version", "1.0"),
        questions=survey.get("questions", []),
        scenario_type=survey.get("scenario_type", "survey"),
    )


@router.put("/{survey_id}", response_model=SurveyResponse)
async def update_survey(survey_id: str, survey_data: SurveyUpdate):
    """更新问卷"""
    # 获取现有问卷
    survey = survey_store.get_custom(survey_id)
    if not survey:
        raise HTTPException(status_code=404, detail="Survey not found")

    # 更新字段
    if survey_data.name is not None:
        survey["name"] = survey_data.name
    if survey_data.description is not None:
        survey["description"] = survey_data.description
    if survey_data.questions is not None:
        survey["questions"] = [q.dict() for q in survey_data.questions]
    if survey_data.scenario_type is not None:
        survey["scenario_type"] = survey_data.scenario_type

    # 保存
    survey_store.save_custom(survey_id, survey)

    return SurveyResponse(
        id=survey_id,
        name=survey.get("name", ""),
        question_count=len(survey.get("questions", [])),
    )


@router.delete("/{survey_id}")
async def delete_survey(survey_id: str):
    """删除问卷"""
    if not survey_store.delete_custom(survey_id):
        raise HTTPException(status_code=404, detail="Survey not found")

    return {"message": "Survey deleted", "survey_id": survey_id}


@router.post("/import", response_model=SurveyResponse)
async def import_survey(file: UploadFile, format: str = "auto"):
    """导入问卷"""
    try:
        content = await file.read()
        data = json.loads(content)

        # 自动检测格式
        if format == "auto":
            if "questions" in data and "title" in data:
                format = "wenjuanxing"
            elif "questions" in data and "name" in data:
                format = "json"
            else:
                format = "json"

        # 解析
        if format == "wenjuanxing":
            survey = WenjuanxingAdapter.parse(data)
        else:
            survey = SurveyImporter.from_json(data)

        # 保存
        survey_store.save_custom(survey.id, survey.dict())

        return SurveyResponse(
            id=survey.id,
            name=survey.name,
            question_count=len(survey.questions),
        )

    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON file")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{survey_id}/export")
async def export_survey(survey_id: str, format: str = "json"):
    """导出问卷"""
    # 获取问卷
    survey = survey_store.get_custom(survey_id)
    if not survey:
        survey = survey_store.get_template(survey_id)

    if not survey:
        raise HTTPException(status_code=404, detail="Survey not found")

    # 导出
    if format == "wenjuanxing":
        return WenjuanxingAdapter.export(survey)
    else:
        return survey


@router.post("/from-template/{template_id}", response_model=SurveyResponse)
async def create_from_template(template_id: str):
    """从模板创建问卷"""
    template = survey_store.get_template(template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    # 创建副本
    survey_id = str(uuid.uuid4())
    survey = template.copy()
    survey["id"] = survey_id
    survey["name"] = f"{template.get('name', '')} - 副本"

    # 保存
    survey_store.save_custom(survey_id, survey)

    return SurveyResponse(
        id=survey_id,
        name=survey["name"],
        question_count=len(survey.get("questions", [])),
    )
