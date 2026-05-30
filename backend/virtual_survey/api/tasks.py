"""任务API"""

import uuid
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, BackgroundTasks, HTTPException

from ..core.engine import engine
from ..models.task import (
    Task,
    TaskCreate,
    TaskDetail,
    TaskResponse,
    TaskResults,
    TaskStatus,
    TaskSummary,
    TaskUpdate,
)
from ..storage.config_store import survey_store
from ..export.result_io import ResultExporter

router = APIRouter(prefix="/api/v1/tasks", tags=["tasks"])


@router.post("/", response_model=TaskResponse)
async def create_task(task_data: TaskCreate, background_tasks: BackgroundTasks):
    """创建调研任务"""
    # 验证问卷存在
    survey = survey_store.get_custom(task_data.survey_id)
    if not survey:
        # 尝试从模板获取
        survey = survey_store.get_template(task_data.survey_id)
    if not survey:
        raise HTTPException(status_code=404, detail="Survey not found")

    # 创建任务
    task = Task(
        id=str(uuid.uuid4()),
        name=task_data.name,
        description=task_data.description,
        scenario_type=task_data.scenario_type,
        status=TaskStatus.PENDING,
        survey_id=task_data.survey_id,
        agents=task_data.agents,
        moderator=task_data.moderator,
        settings=task_data.settings,
        created_at=datetime.now(),
    )

    # 创建会话
    try:
        await engine.create_session(task, survey)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    return TaskResponse(
        id=task.id,
        name=task.name,
        scenario_type=task.scenario_type,
        status=task.status,
        created_at=task.created_at,
    )


@router.get("/", response_model=List[TaskSummary])
async def list_tasks(
    status: Optional[str] = None,
    scenario_type: Optional[str] = None,
    page: int = 1,
    size: int = 20,
):
    """获取任务列表"""
    tasks = []

    for task_id in engine.list_sessions():
        session = engine.sessions.get(task_id)
        if not session:
            continue

        task = session.task

        if status and task.status.value != status:
            continue

        if scenario_type and task.scenario_type.value != scenario_type:
            continue

        progress = None
        if session.scenario:
            survey_questions = session.survey.get("questions", []) if isinstance(session.survey, dict) else getattr(session.survey, 'questions', [])
            progress = {
                "current": session.scenario.current_question,
                "total": len(survey_questions),
                "answered": len(session.scenario.responses),
            }

        tasks.append(TaskSummary(
            id=task.id,
            name=task.name,
            scenario_type=task.scenario_type,
            status=task.status,
            agent_count=len(task.agents),
            created_at=task.created_at,
            started_at=task.started_at,
            completed_at=task.completed_at,
            progress=progress,
        ))

    # 分页
    start = (page - 1) * size
    end = start + size

    return tasks[start:end]


@router.get("/{task_id}/", response_model=TaskDetail)
async def get_task(task_id: str):
    """获取任务详情"""
    session = engine.sessions.get(task_id)
    if not session:
        raise HTTPException(status_code=404, detail="Task not found")

    task = session.task

    return TaskDetail(
        id=task.id,
        name=task.name,
        description=task.description,
        scenario_type=task.scenario_type,
        status=task.status,
        survey_id=task.survey_id,
        agents=task.agents,
        moderator=task.moderator,
        settings=task.settings,
        created_at=task.created_at,
        started_at=task.started_at,
        completed_at=task.completed_at,
        error_message=task.error_message,
    )


@router.post("/{task_id}/start/")
async def start_task(task_id: str):
    """启动任务"""
    session = engine.sessions.get(task_id)
    if not session:
        raise HTTPException(status_code=404, detail="Task not found")

    if session.task.status != TaskStatus.PENDING:
        raise HTTPException(
            status_code=400,
            detail=f"Task is not in pending status, current: {session.task.status.value}"
        )

    try:
        await engine.start_task(task_id)
        return {"message": "Task started", "task_id": task_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{task_id}/pause/")
async def pause_task(task_id: str):
    """暂停任务"""
    session = engine.sessions.get(task_id)
    if not session:
        raise HTTPException(status_code=404, detail="Task not found")

    if session.task.status != TaskStatus.RUNNING:
        raise HTTPException(
            status_code=400,
            detail="Task is not running"
        )

    await engine.pause_task(task_id)
    return {"message": "Task paused", "task_id": task_id}


@router.post("/{task_id}/resume/")
async def resume_task(task_id: str):
    """恢复任务"""
    session = engine.sessions.get(task_id)
    if not session:
        raise HTTPException(status_code=404, detail="Task not found")

    if session.task.status != TaskStatus.PAUSED:
        raise HTTPException(
            status_code=400,
            detail="Task is not paused"
        )

    await engine.resume_task(task_id)
    return {"message": "Task resumed", "task_id": task_id}


@router.post("/{task_id}/stop/")
async def stop_task(task_id: str):
    """停止任务"""
    session = engine.sessions.get(task_id)
    if not session:
        raise HTTPException(status_code=404, detail="Task not found")

    if session.task.status not in [TaskStatus.RUNNING, TaskStatus.PAUSED]:
        raise HTTPException(
            status_code=400,
            detail="Task is not running or paused"
        )

    await engine.stop_task(task_id)
    return {"message": "Task stopped", "task_id": task_id}


@router.delete("/{task_id}/")
async def delete_task(task_id: str):
    """删除任务"""
    if not engine.has_session(task_id):
        raise HTTPException(status_code=404, detail="Task not found")

    session = engine.sessions.get(task_id)
    if session and session.task.status in [TaskStatus.RUNNING, TaskStatus.PAUSED]:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete running task"
        )

    engine.remove_session(task_id)
    return {"message": "Task deleted", "task_id": task_id}


@router.get("/{task_id}/results/", response_model=TaskResults)
async def get_results(task_id: str):
    """获取任务结果"""
    results = await engine.get_session_results(task_id)
    if not results:
        raise HTTPException(status_code=404, detail="Results not found")

    # 补充 Agent 配置信息
    session = engine.sessions.get(task_id)
    if session:
        agent_info_list = []
        for ac in session.task.agents:
            pdata = session.personas.get(ac.persona_id, {})
            agent_info_list.append({
                "agent_id": ac.id, "agent_name": ac.name,
                "persona_id": ac.persona_id,
                "persona_name": pdata.get("name", ac.name) if isinstance(pdata, dict) else (pdata.name if hasattr(pdata, 'name') else ac.name),
                "occupation": pdata.get("demographics", {}).get("occupation", "") if isinstance(pdata, dict) else "",
                "provider_pack": ac.provider_pack, "model": ac.model,
                "behavior_prompt_id": ac.behavior_prompt_id,
                "thinking_enabled": ac.thinking_enabled, "thinking_intensity": ac.thinking_intensity,
            })
        results["agents"] = agent_info_list
        if session.scenario and session.scenario.survey_feedback:
            fb_list = []
            for fb in session.scenario.survey_feedback:
                if isinstance(fb, dict):
                    fb_list.append(fb)
                else:
                    fb_list.append({"agent_id": fb.agent_id, "agent_name": fb.agent_name,
                                    "length_rating": fb.length_rating, "difficulty_rating": fb.difficulty_rating,
                                    "clarity_rating": fb.clarity_rating, "fatigue_rating": fb.fatigue_rating,
                                    "interest_rating": fb.interest_rating, "comment": fb.comment})
            results["survey_feedback"] = fb_list

    return results


@router.get("/{task_id}/export/{format}/")
async def export_results(task_id: str, format: str):
    """导出任务结果（json/csv）"""
    results = await engine.get_session_results(task_id)
    if not results:
        raise HTTPException(status_code=404, detail="Results not found")

    if format == "csv":
        csv_data = ResultExporter.to_csv(results)
        from fastapi.responses import PlainTextResponse
        return PlainTextResponse(csv_data, media_type="text/csv",
                                  headers={"Content-Disposition": f"attachment; filename=results_{task_id[:8]}.csv"})
    else:
        return ResultExporter.to_json_dict(results)


@router.get("/{task_id}/status/")
async def get_task_status(task_id: str):
    """获取任务状态"""
    status = await engine.get_session_status(task_id)
    if not status:
        raise HTTPException(status_code=404, detail="Task not found")

    return status

