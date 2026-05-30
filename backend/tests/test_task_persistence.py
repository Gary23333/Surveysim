import os
import tempfile
from pathlib import Path

os.environ["DATABASE_URL"] = f"sqlite:///{Path(tempfile.mkdtemp()) / 'surveysim_test.db'}"
os.environ["DEBUG"] = "false"

from fastapi.testclient import TestClient

from virtual_survey.core.engine import SurveyEngine
from virtual_survey.main import app
from virtual_survey.models.task import AgentConfig, Task, TaskStatus
from virtual_survey.storage.database import init_db
from virtual_survey.storage import task_store


def make_task(task_id: str = "task-test") -> Task:
    return Task(
        id=task_id,
        name="Persistence test",
        survey_id="survey-test",
        status=TaskStatus.COMPLETED,
        agents=[
            AgentConfig(
                id="agent-1",
                name="Agent 1",
                persona_id="persona-1",
                provider_pack="OpenAI",
                model="gpt-4o-mini",
                behavior_prompt_id="neutral",
            )
        ],
    )


def make_result(task_id: str = "task-test") -> dict:
    return {
        "task_id": task_id,
        "status": "completed",
        "scenario_type": "survey",
        "total_questions": 1,
        "total_responses": 1,
        "total_follow_ups": 0,
        "avg_response_length": 12,
        "emotion_distribution": {"neutral": 1},
        "summary": "ok",
        "question_results": [
            {
                "question_id": "q1",
                "question_text": "Question?",
                "responses": [
                    {
                        "agent_id": "agent-1",
                        "agent_name": "Agent 1",
                        "content": "Answer",
                        "emotion": "neutral",
                        "emotion_intensity": 0.5,
                        "score": None,
                        "timestamp": "2026-05-31T00:00:00",
                    }
                ],
                "follow_ups": [],
            }
        ],
        "agents": [],
        "survey_feedback": [],
    }


def test_task_store_round_trip_and_delete():
    init_db()
    task = make_task("task-store")
    result = make_result("task-store")

    task_store.save_task_result(task, result)

    restored = task_store.get_task("task-store")
    assert restored is not None
    assert restored.name == "Persistence test"
    assert restored.status == TaskStatus.COMPLETED
    assert task_store.get_task_result("task-store")["total_questions"] == 1
    assert any(item.id == "task-store" for item in task_store.list_tasks())

    assert task_store.delete_task("task-store") is True
    assert task_store.get_task("task-store") is None


def test_task_api_reads_persisted_task_results_and_exports():
    init_db()
    task = make_task("task-api")
    task_store.save_task_result(task, make_result("task-api"))

    with TestClient(app) as client:
        detail = client.get("/api/v1/tasks/task-api/")
        assert detail.status_code == 200
        assert detail.json()["id"] == "task-api"

        status = client.get("/api/v1/tasks/task-api/status/")
        assert status.status_code == 200
        assert status.json()["status"] == "completed"

        results = client.get("/api/v1/tasks/task-api/results/")
        assert results.status_code == 200
        assert results.json()["total_questions"] == 1

        exported = client.get("/api/v1/tasks/task-api/export/csv/")
        assert exported.status_code == 200
        assert "题号" in exported.text
        assert "Answer" in exported.text


def test_engine_websocket_manager_backfills_existing_sessions():
    engine = SurveyEngine()

    class SessionStub:
        websocket_manager = None

    session = SessionStub()
    manager = object()
    engine.sessions["session-1"] = session

    engine.set_websocket_manager(manager)

    assert engine.websocket_manager is manager
    assert session.websocket_manager is manager
