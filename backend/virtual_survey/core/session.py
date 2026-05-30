"""会话管理"""

import asyncio
from datetime import datetime
from typing import Any, Dict, List, Optional


class SurveyWrapper:
    """问卷数据包装器，支持 dict 和对象两种方式访问"""
    def __init__(self, data: Any):
        self._data = data if isinstance(data, dict) else {}

    @property
    def name(self):
        return self._data.get("name", "") if isinstance(self._data, dict) else getattr(self._data, 'name', "")
    
    @property
    def questions(self) -> List[Any]:
        if isinstance(self._data, dict):
            return [SurveyQuestionWrapper(q) for q in self._data.get("questions", [])]
        return [SurveyQuestionWrapper(getattr(q, '__dict__', {})) if not isinstance(q, dict) else SurveyQuestionWrapper(q) for q in getattr(self._data, 'questions', [])]

    def get(self, key: str, default=None):
        return self._data.get(key, default) if isinstance(self._data, dict) else getattr(self._data, key, default)


class SurveyQuestionWrapper:
    def __init__(self, data):
        self._data = data if isinstance(data, dict) else {}
        self.text = self._data.get("text", "") if isinstance(self._data, dict) else getattr(self._data, 'text', '')
        self.id = self._data.get("id", "") if isinstance(self._data, dict) else getattr(self._data, 'id', '')
        self.type = self._data.get("type", "") if isinstance(self._data, dict) else getattr(self._data, 'type', '')
        self.mode = self._data.get("mode", "global") if isinstance(self._data, dict) else getattr(self._data, 'mode', 'global')
        self.visibility = self._data.get("visibility", "isolated") if isinstance(self._data, dict) else getattr(self._data, 'visibility', 'isolated')
        self.enable_text = self._data.get("enable_text", True) if isinstance(self._data, dict) else getattr(self._data, 'enable_text', True)
        self.enable_rating = self._data.get("enable_rating", False) if isinstance(self._data, dict) else getattr(self._data, 'enable_rating', False)
        self.rating_config = self._data.get("rating_config") if isinstance(self._data, dict) else getattr(self._data, 'rating_config', None)


from ..llm.manager import provider_manager
from ..llm.pack import pack_manager
from ..models.scenario import AgentResponse, ScenarioResult
from ..models.task import Task, TaskStatus
from .moderator import AIModerator
from .moderator_manager import ModeratorManager
from .respondent import RespondentAgent
from .scenarios import (
    DebateScenario,
    FocusGroupScenario,
    IDIScenario,
    Scenario,
    SurveyScenario,
)


class Session:
    """调研会话"""

    def __init__(
        self,
        task: Task,
        survey: Any,
        personas: Dict[str, Any],
        behavior_prompts: Dict[str, str],
        websocket_manager: Any,
    ):
        self.task = task
        self.survey = SurveyWrapper(survey)
        self.personas = personas
        self.behavior_prompts = behavior_prompts
        self.websocket_manager = websocket_manager

        self.agents: Dict[str, RespondentAgent] = {}
        self.moderator_manager: Optional[ModeratorManager] = None
        self.scenario: Optional[Scenario] = None

        self.status = "pending"
        self.results: Optional[ScenarioResult] = None
        self._pause_event = asyncio.Event()
        self._pause_event.set()  # 初始不暂停
        self._stop_flag = False

    async def initialize_agents(self) -> None:
        """初始化所有Agent"""
        for agent_config in self.task.agents:
            # 获取Provider
            provider = provider_manager.get(agent_config.provider_pack)
            if not provider:
                raise ValueError(f"Provider '{agent_config.provider_pack}' not found")

            # 获取Pack配置
            pack = pack_manager.get_pack(agent_config.provider_pack)
            tc = pack.thinking_config if pack else None
            mtp = pack.max_tokens_param if pack else "max_tokens"

            # 获取Persona
            persona = self.personas.get(agent_config.persona_id)
            if not persona:
                raise ValueError(f"Persona '{agent_config.persona_id}' not found")

            # 获取行为提示词
            behavior_prompt = self.behavior_prompts.get(
                agent_config.behavior_prompt_id, ""
            )

            # 创建Agent
            agent = RespondentAgent(
                id=agent_config.id,
                name=agent_config.name,
                persona=persona,
                provider=provider,
                model=agent_config.model,
                behavior_prompt=behavior_prompt,
                memory_config=agent_config.memory_config.dict() if agent_config.memory_config else {},
                thinking_enabled=agent_config.thinking_enabled,
                thinking_intensity=agent_config.thinking_intensity,
                thinking_config=tc,
                max_tokens_param=mtp,
            )

            self.agents[agent_config.id] = agent

        # 初始化主持人（始终创建 ModeratorManager，支持 AI/人工切换）
        moderator_config = self.task.moderator
        ai_moderator = None
        if moderator_config.type == "ai" or True:
            provider_name = moderator_config.provider_pack or list(self.agents.values())[0].id if self.agents else None
            ai_provider = provider_manager.get(provider_name) if provider_name else None
            if not ai_provider:
                ai_provider = list(provider_manager._providers.values())[0] if provider_manager._providers else None
            
            if ai_provider:
                pack = pack_manager.get_pack(provider_name) if provider_name else None
                mtc = pack.thinking_config if pack else None
                mmtp = pack.max_tokens_param if pack else "max_tokens"

                ai_moderator = AIModerator(
                    provider=ai_provider,
                    model=moderator_config.model or (pack.default_model if pack else "gpt-4o-mini"),
                    behavior_prompt=self.behavior_prompts.get(moderator_config.behavior_prompt_id, ""),
                    thinking_enabled=moderator_config.thinking_enabled,
                    thinking_intensity=moderator_config.thinking_intensity,
                    thinking_config=mtc,
                    max_tokens_param=mmtp,
                )

        self.moderator_manager = ModeratorManager(ai_moderator) if ai_moderator else ModeratorManager()
        if moderator_config.type == "human":
            await self.moderator_manager.switch_to_human()

        # 初始化场景
        scenario_type = self.task.scenario_type
        if scenario_type == "survey":
            self.scenario = SurveyScenario(self)
        elif scenario_type == "focus_group":
            self.scenario = FocusGroupScenario(self)
        elif scenario_type == "idi":
            self.scenario = IDIScenario(self)
        elif scenario_type == "debate":
            self.scenario = DebateScenario(self)
        else:
            raise ValueError(f"Unknown scenario type: {scenario_type}")

    async def run(self) -> None:
        """执行调研"""
        self.status = "running"
        await self._broadcast_status()

        try:
            # 初始化场景
            await self.scenario.initialize(self.task.settings.dict())

            # 执行场景
            self.results = await self.scenario.execute()

            self.status = "completed"

        except StopIteration:
            self.status = "stopped"

        except Exception as e:
            self.status = "error"
            self.results = ScenarioResult(
                scenario_type=self.scenario.__class__.__name__,
                total_questions=0,
                total_responses=0,
                total_follow_ups=0,
                question_results=[],
                summary=f"执行失败: {str(e)}",
            )
            raise

        finally:
            await self._broadcast_status()

    async def pause(self) -> None:
        """暂停会话"""
        self.status = "paused"
        self._pause_event.clear()
        await self._broadcast_status()

    async def resume(self) -> None:
        """恢复会话"""
        self.status = "running"
        self._pause_event.set()
        await self._broadcast_status()

    async def stop(self) -> None:
        """停止会话"""
        self._stop_flag = True
        if self.scenario:
            self.scenario.stop()
        self.status = "stopped"
        await self._broadcast_status()

    async def check_status(self) -> None:
        """检查状态（用于暂停/停止）"""
        if self._stop_flag:
            raise StopIteration("Task stopped")

        await self._pause_event.wait()

    async def broadcast(self, message: Dict[str, Any]) -> None:
        """广播消息"""
        if self.websocket_manager:
            await self.websocket_manager.broadcast(self.task.id, message)

    async def _broadcast_status(self) -> None:
        """广播状态变更"""
        await self.broadcast({
            "type": "system_event",
            "event": "status_changed",
            "data": {
                "task_id": self.task.id,
                "status": self.status,
                "agents": {
                    agent_id: agent.get_state()
                    for agent_id, agent in self.agents.items()
                },
                "progress": {
                    "current": self.scenario.current_question if self.scenario else 0,
                    "total": len(self.survey.questions),
                },
            },
        })

    async def handle_command(self, command: Dict[str, Any]) -> None:
        """处理主持人指令"""
        cmd_type = command.get("command")

        if cmd_type == "next_question":
            questions = self.survey.questions
            idx = command.get("index", self.scenario.current_question if self.scenario else 0)
            if idx >= len(questions):
                await self.broadcast({"type": "system_event", "event": "all_questions_done", "data": {"total": len(questions)}})
                return
            q = questions[idx]
            q_text = q.text if hasattr(q, 'text') else str(q)
            q_mode = q.mode if hasattr(q, 'mode') else "global"

            self.scenario.current_question = idx
            await self.broadcast_question_raw(idx, len(questions), q_text)

            # 并行触发所有Agent回答
            tasks = []
            for agent_id, agent in self.agents.items():
                tasks.append(agent.respond(q_text, {"visibility": "open" if q_mode == "open" else "isolated"}))
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            resp_count = 0
            for r in responses:
                if isinstance(r, AgentResponse):
                    resp_count += 1
                    await self.broadcast_response(r)

            await self.broadcast({
                "type": "system_event", "event": "question_answered",
                "data": {"index": idx, "total": len(questions), "responses": resp_count, "agents": len(self.agents)},
            })

        elif cmd_type == "ask_question":
            target = command.get("target")
            question = command.get("question")
            if target == "all":
                for agent in self.agents.values():
                    response = await agent.respond(question, {"visibility": "open"})
                    await self.broadcast_response(response)
            else:
                agent = self.agents.get(target)
                if agent:
                    response = await agent.respond(question, {"visibility": "isolated"})
                    await self.broadcast_response(response)

        elif cmd_type == "follow_up":
            target = command.get("target")
            question = command.get("question")
            agent = self.agents.get(target)
            if agent:
                response = await agent.respond(question, {"visibility": "isolated", "is_follow_up": True})
                await self.broadcast_response(response)

        elif cmd_type == "change_visibility":
            visibility = command.get("visibility")
            self.task.settings.default_visibility = visibility

        elif cmd_type == "moderator_takeover":
            action = command.get("action")
            if action == "takeover":
                await self.moderator_manager.switch_to_human()
                await self.broadcast({"type": "system_event", "event": "moderator_switched", "data": {"type": "human"}})
            elif action == "release":
                await self.moderator_manager.switch_to_ai()
                await self.broadcast({"type": "system_event", "event": "moderator_switched", "data": {"type": "ai"}})

    async def broadcast_question_raw(self, index: int, total: int, text: str) -> None:
        await self.broadcast({
            "type": "system_event",
            "event": "question_changed",
            "data": {"index": index, "total": total, "question_text": text},
        })

    async def broadcast_response(self, response: AgentResponse) -> None:
        await self.broadcast({
            "type": "agent_response",
            "agent_id": response.agent_id,
            "agent_name": response.agent_name,
            "content": response.content,
            "emotion": response.emotion,
            "emotion_intensity": response.emotion_intensity,
            "timestamp": response.timestamp,
            "score": response.score,
        })

    def get_status(self) -> Dict[str, Any]:
        """获取状态"""
        return {
            "task_id": self.task.id,
            "status": self.status,
            "agents": {
                agent_id: agent.get_state()
                for agent_id, agent in self.agents.items()
            },
            "progress": {
                "current": self.scenario.current_question if self.scenario else 0,
                "total": len(self.survey.questions),
            },
        }

    def get_results(self) -> Optional[Dict[str, Any]]:
        """获取结果"""
        if not self.results:
            return None

        # 构建Agent参与信息列表
        agent_info_list = []
        for ac in self.task.agents:
            pdata = self.personas.get(ac.persona_id, {})
            agent_info_list.append({
                "agent_id": ac.id,
                "agent_name": ac.name,
                "persona_id": ac.persona_id,
                "persona_name": pdata.get("name", ac.name) if isinstance(pdata, dict) else getattr(pdata, 'name', ac.name),
                "occupation": pdata.get("demographics", {}).get("occupation", "") if isinstance(pdata, dict) else "",
                "provider_pack": ac.provider_pack,
                "model": ac.model,
                "behavior_prompt_id": ac.behavior_prompt_id,
                "thinking_enabled": ac.thinking_enabled,
                "thinking_intensity": ac.thinking_intensity,
            })

        return {
            "task_id": self.task.id,
            "status": self.status,
            "scenario_type": self.results.scenario_type,
            "total_questions": self.results.total_questions,
            "total_responses": self.results.total_responses,
            "total_follow_ups": self.results.total_follow_ups,
            "avg_response_length": self.results.avg_response_length,
            "emotion_distribution": self.results.emotion_distribution,
            "summary": self.results.summary,
            "agents": agent_info_list,
            "question_results": [
                {
                    "question_id": qr.question_id,
                    "question_text": qr.question_text,
                        "responses": [
                        {
                            "agent_id": r.agent_id,
                            "agent_name": r.agent_name,
                            "content": r.content,
                            "emotion": r.emotion,
                            "emotion_intensity": r.emotion_intensity,
                            "score": r.score,
                            "timestamp": r.timestamp,
                        }
                        for r in qr.responses
                    ],
                    "follow_ups": [
                        {
                            "question": fu.question,
                            "response": {
                                "agent_id": fu.response.agent_id,
                                "agent_name": fu.response.agent_name,
                                "content": fu.response.content,
                                "emotion": fu.response.emotion,
                            } if fu.response else None,
                            "depth": fu.depth,
                        }
                        for fu in qr.follow_ups
                    ],
                }
                for qr in self.results.question_results
            ],
            "survey_feedback": self.results.survey_feedback or [],
        }
