"""任务执行引擎"""

import asyncio
from datetime import datetime
from typing import Any, Dict, List, Optional

from ..llm.manager import provider_manager
from ..models.task import Task, TaskStatus
from ..storage.config_store import persona_store, survey_store, behavior_prompt_store
from .session import Session


class SurveyEngine:
    """调研引擎"""

    def __init__(self, websocket_manager: Any = None):
        self.websocket_manager = websocket_manager
        self.sessions: Dict[str, Session] = {}
        self._running_tasks: Dict[str, asyncio.Task] = {}

    async def create_session(
        self,
        task: Task,
        survey: Any,
    ) -> Session:
        """创建会话"""
        # 加载Persona
        personas = {}
        for agent_config in task.agents:
            persona_data = persona_store.get_custom(agent_config.persona_id)
            if persona_data:
                personas[agent_config.persona_id] = persona_data

        # 加载行为提示词
        behavior_prompts = {}
        prompts = behavior_prompt_store.list_prompts()
        for prompt in prompts:
            behavior_prompts[prompt["id"]] = prompt.get("prompt", "")

        # 创建会话
        session = Session(
            task=task,
            survey=survey,
            personas=personas,
            behavior_prompts=behavior_prompts,
            websocket_manager=self.websocket_manager,
        )

        # 初始化Agent
        await session.initialize_agents()

        self.sessions[task.id] = session
        return session

    async def start_task(self, task_id: str) -> str:
        """启动任务"""
        session = self.sessions.get(task_id)
        if not session:
            raise ValueError(f"Session {task_id} not found")

        # 更新任务状态
        session.task.status = TaskStatus.RUNNING
        session.task.started_at = datetime.now()

        # 后台执行
        async_task = asyncio.create_task(self._run_session(session))
        self._running_tasks[task_id] = async_task

        return task_id

    async def _run_session(self, session: Session) -> None:
        """运行会话"""
        try:
            await session.run()
            session.task.status = TaskStatus.COMPLETED
            session.task.completed_at = datetime.now()
        except Exception as e:
            import traceback
            session.task.status = TaskStatus.ERROR
            session.task.error_message = str(e)
            print(f"Session error: {e}")
            traceback.print_exc()
        finally:
            # 清理
            if session.task.id in self._running_tasks:
                del self._running_tasks[session.task.id]

    async def pause_task(self, task_id: str) -> None:
        """暂停任务"""
        session = self.sessions.get(task_id)
        if session:
            await session.pause()
            session.task.status = TaskStatus.PAUSED

    async def resume_task(self, task_id: str) -> None:
        """恢复任务"""
        session = self.sessions.get(task_id)
        if session:
            await session.resume()
            session.task.status = TaskStatus.RUNNING

    async def stop_task(self, task_id: str) -> None:
        """停止任务"""
        session = self.sessions.get(task_id)
        if session:
            await session.stop()
            session.task.status = TaskStatus.STOPPED

            # 取消异步任务
            if task_id in self._running_tasks:
                self._running_tasks[task_id].cancel()
                del self._running_tasks[task_id]

    async def handle_command(self, session_id: str, command: Dict[str, Any]) -> None:
        """处理指令"""
        session = self.sessions.get(session_id)
        if session:
            await session.handle_command(command)

    async def get_session_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """获取会话状态"""
        session = self.sessions.get(task_id)
        if session:
            return session.get_status()
        return None

    async def get_session_results(self, task_id: str) -> Optional[Dict[str, Any]]:
        """获取会话结果"""
        session = self.sessions.get(task_id)
        if session:
            return session.get_results()
        return None

    def remove_session(self, task_id: str) -> bool:
        """移除会话"""
        if task_id in self.sessions:
            # 检查是否还在运行
            if task_id in self._running_tasks:
                return False

            del self.sessions[task_id]
            return True
        return False

    def list_sessions(self) -> List[str]:
        """列出所有会话"""
        return list(self.sessions.keys())

    def has_session(self, task_id: str) -> bool:
        """检查会话是否存在"""
        return task_id in self.sessions


# 全局引擎实例
engine = SurveyEngine()
