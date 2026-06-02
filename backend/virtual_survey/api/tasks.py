"""任务API"""

import uuid
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from ..core.engine import engine
from ..core.moderator import AIModerator
from ..export.result_io import ResultExporter
from ..llm.manager import provider_manager
from ..models.task import (
    Task,
    TaskCreate,
    TaskDetail,
    TaskResponse,
    TaskResults,
    TaskStatus,
    TaskSummary,
)
from ..storage import task_store
from ..storage.config_store import survey_store

router = APIRouter(prefix="/api/v1/tasks", tags=["tasks"])


def _load_survey(survey_id: str):
    survey = survey_store.get_custom(survey_id)
    if not survey:
        survey = survey_store.get_template(survey_id)
    return survey


async def _ensure_session(task_id: str):
    session = engine.sessions.get(task_id)
    if session:
        return session

    task = task_store.get_task(task_id)
    if not task:
        return None

    survey = _load_survey(task.survey_id)
    if not survey:
        raise HTTPException(status_code=404, detail="Survey not found")

    return await engine.create_session(task, survey)


def _build_progress(session=None, results: Optional[dict] = None):
    if session and session.scenario:
        return {
            "current": session.scenario.current_question,
            "total": len(session.survey.questions),
            "answered": len(session.scenario.responses),
        }
    if results:
        total = results.get("total_questions", 0)
        answered = sum(
            len(question.get("responses", []))
            for question in results.get("question_results", [])
            if isinstance(question, dict)
        )
        return {"current": total, "total": total, "answered": answered}
    return None


@router.post("/", response_model=TaskResponse)
async def create_task(task_data: TaskCreate):
    """创建调研任务"""
    # 验证问卷存在
    survey = _load_survey(task_data.survey_id)
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
        task_store.save_task(task)
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

    persisted_tasks = {task.id: task for task in task_store.list_tasks(status, scenario_type)}
    for task_id in engine.list_sessions():
        session = engine.sessions.get(task_id)
        if session:
            persisted_tasks[task_id] = session.task

    for task in persisted_tasks.values():
        if status and task.status.value != status:
            continue

        if scenario_type and task.scenario_type.value != scenario_type:
            continue

        session = engine.sessions.get(task.id)
        progress = _build_progress(session, task_store.get_task_result(task.id))

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
    task = session.task if session else task_store.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

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
    session = await _ensure_session(task_id)
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
    if not engine.has_session(task_id) and not task_store.get_task(task_id):
        raise HTTPException(status_code=404, detail="Task not found")

    session = engine.sessions.get(task_id)
    if session and session.task.status in [TaskStatus.RUNNING, TaskStatus.PAUSED]:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete running task"
        )

    engine.remove_session(task_id)
    task_store.delete_task(task_id)
    return {"message": "Task deleted", "task_id": task_id}


@router.get("/{task_id}/results/", response_model=TaskResults)
async def get_results(task_id: str):
    """获取任务结果"""
    results = await engine.get_session_results(task_id)
    if not results:
        results = task_store.get_task_result(task_id)
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
        results = task_store.get_task_result(task_id)
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
        task = task_store.get_task(task_id)
        results = task_store.get_task_result(task_id)
        if task:
            status = {
                "task_id": task.id,
                "status": task.status.value,
                "agents": {},
                "progress": _build_progress(results=results),
            }
    if not status:
        raise HTTPException(status_code=404, detail="Task not found")

    return status


class SummarizeRequest(BaseModel):
    question_ids: Optional[List[str]] = Field(default=None, description="要总结的题目ID列表，默认全部")


@router.post("/{task_id}/results/summarize/")
async def summarize_question_results(task_id: str, request: SummarizeRequest = SummarizeRequest()):
    """为每道题生成 AI 总结"""
    # 获取 session 和结果
    session = engine.sessions.get(task_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    results = await engine.get_session_results(task_id)
    if not results:
        raise HTTPException(status_code=404, detail="Results not found")

    question_results = results.get("question_results", [])
    if not question_results:
        return {"summaries": {}}

    # 确定要总结的题目
    target_ids = set(request.question_ids) if request.question_ids else None

    # 从 session 获取 provider: 优先用 AI moderator 的, 否则用第一个 agent 的
    provider = None
    model = "gpt-4o-mini"
    if session.moderator_manager and session.moderator_manager.ai_moderator:
        provider = session.moderator_manager.ai_moderator.provider
        model = session.moderator_manager.ai_moderator.model
    elif session.task.agents:
        first_agent = session.task.agents[0]
        pack = provider_manager.get(first_agent.provider_pack)
        if pack:
            provider = pack.get("provider")
            model = first_agent.model or pack.get("default_model", "gpt-4o-mini")

    if not provider:
        raise HTTPException(status_code=400, detail="No LLM provider available for summarization")

    moderator = AIModerator(provider, model)

    summaries = {}
    for qr in question_results:
        qid = qr.get("question_id", "")
        if target_ids and qid not in target_ids:
            continue

        question_text = qr.get("question_text", "")
        responses_data = qr.get("responses", [])

        if not responses_data:
            summaries[qid] = "暂无回答数据"
            continue

        # 构建 AgentResponse 对象列表
        from ..models.scenario import AgentResponse
        agent_responses = []
        for r in responses_data:
            agent_responses.append(AgentResponse(
                agent_id=r.get("agent_id", ""),
                agent_name=r.get("agent_name", ""),
                content=r.get("content", ""),
                emotion=r.get("emotion", "neutral"),
                emotion_intensity=r.get("emotion_intensity", 0.5),
                timestamp=r.get("timestamp", ""),
                score=r.get("score"),
            ))

        try:
            summary = await moderator.generate_question_summary(question_text, agent_responses)
            summaries[qid] = summary
            # 写回 session 的 results
            if session.results:
                for sqr in session.results.question_results:
                    if sqr.question_id == qid:
                        sqr.ai_summary = summary
                        break
        except Exception as e:
            summaries[qid] = f"总结生成失败: {str(e)}"

    return {"summaries": summaries}

