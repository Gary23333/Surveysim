"""任务持久化存储"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import Column
from sqlalchemy.types import JSON
from sqlmodel import Field, SQLModel, select

from ..models.task import Task
from .database import get_db_session


class TaskRecord(SQLModel, table=True):
    """任务与结果记录。"""

    id: str = Field(primary_key=True)
    status: str = Field(index=True)
    scenario_type: str = Field(index=True)
    created_at: datetime = Field(index=True)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    task_data: Dict[str, Any] = Field(sa_column=Column(JSON, nullable=False))
    result_data: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))


def save_task(task: Task) -> None:
    """新增或更新任务。"""
    with get_db_session() as db:
        record = db.get(TaskRecord, task.id)
        task_data = task.model_dump(mode="json")
        if record:
            record.status = task.status.value
            record.scenario_type = task.scenario_type.value
            record.created_at = task.created_at
            record.started_at = task.started_at
            record.completed_at = task.completed_at
            record.task_data = task_data
        else:
            record = TaskRecord(
                id=task.id,
                status=task.status.value,
                scenario_type=task.scenario_type.value,
                created_at=task.created_at,
                started_at=task.started_at,
                completed_at=task.completed_at,
                task_data=task_data,
            )
            db.add(record)


def save_task_result(task: Task, result: Dict[str, Any]) -> None:
    """保存任务状态和最终结果。"""
    with get_db_session() as db:
        record = db.get(TaskRecord, task.id)
        task_data = task.model_dump(mode="json")
        if not record:
            record = TaskRecord(
                id=task.id,
                status=task.status.value,
                scenario_type=task.scenario_type.value,
                created_at=task.created_at,
                started_at=task.started_at,
                completed_at=task.completed_at,
                task_data=task_data,
                result_data=result,
            )
            db.add(record)
            return

        record.status = task.status.value
        record.scenario_type = task.scenario_type.value
        record.created_at = task.created_at
        record.started_at = task.started_at
        record.completed_at = task.completed_at
        record.task_data = task_data
        record.result_data = result


def get_task(task_id: str) -> Optional[Task]:
    """读取任务。"""
    with get_db_session() as db:
        record = db.get(TaskRecord, task_id)
        if not record:
            return None
        return Task.model_validate(record.task_data)


def get_task_result(task_id: str) -> Optional[Dict[str, Any]]:
    """读取任务结果。"""
    with get_db_session() as db:
        record = db.get(TaskRecord, task_id)
        return record.result_data if record else None


def list_tasks(status: Optional[str] = None, scenario_type: Optional[str] = None) -> List[Task]:
    """读取任务列表。"""
    with get_db_session() as db:
        statement = select(TaskRecord)
        if status:
            statement = statement.where(TaskRecord.status == status)
        if scenario_type:
            statement = statement.where(TaskRecord.scenario_type == scenario_type)
        statement = statement.order_by(TaskRecord.created_at.desc())
        records = db.exec(statement).all()
        return [Task.model_validate(record.task_data) for record in records]


def delete_task(task_id: str) -> bool:
    """删除任务。"""
    with get_db_session() as db:
        record = db.get(TaskRecord, task_id)
        if not record:
            return False
        db.delete(record)
        return True
