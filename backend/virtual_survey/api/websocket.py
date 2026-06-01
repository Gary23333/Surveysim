"""WebSocket端点"""

import asyncio
from datetime import datetime
from typing import Any, Dict, Set

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from ..core.engine import engine

router = APIRouter()


class ConnectionManager:
    """WebSocket连接管理器"""

    def __init__(self):
        # session_id -> set of websockets
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        self._lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket, session_id: str):
        """连接"""
        await websocket.accept()

        async with self._lock:
            if session_id not in self.active_connections:
                self.active_connections[session_id] = set()
            self.active_connections[session_id].add(websocket)

    def disconnect(self, websocket: WebSocket, session_id: str):
        """断开连接"""
        if session_id in self.active_connections:
            self.active_connections[session_id].discard(websocket)
            if not self.active_connections[session_id]:
                del self.active_connections[session_id]

    async def broadcast(self, session_id: str, message: Dict[str, Any]):
        """向会话内所有客户端广播消息"""
        if session_id not in self.active_connections:
            return

        disconnected = set()

        for websocket in self.active_connections[session_id]:
            try:
                await websocket.send_json(message)
            except Exception:
                disconnected.add(websocket)

        # 清理断开的连接
        for ws in disconnected:
            self.disconnect(ws, session_id)

    async def send_personal(self, websocket: WebSocket, message: Dict[str, Any]):
        """发送给特定客户端"""
        try:
            await websocket.send_json(message)
        except Exception:
            pass

    def get_connection_count(self, session_id: str) -> int:
        """获取连接数"""
        return len(self.active_connections.get(session_id, set()))


# 全局连接管理器
ws_manager = ConnectionManager()
engine.set_websocket_manager(ws_manager)


@router.websocket("/ws/sessions/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """WebSocket端点"""
    # 检查session是否存在
    if not engine.has_session(session_id):
        await websocket.close(code=4004, reason="Session not found")
        return

    # 连接
    await ws_manager.connect(websocket, session_id)

    try:
        # 发送当前状态
        status = await engine.get_session_status(session_id)
        await ws_manager.send_personal(websocket, {
            "type": "system_event",
            "event": "connected",
            "data": status,
        })

        # 确保连接前已创建的会话也能广播实时消息
        engine.set_websocket_manager(ws_manager)

        # 监听消息
        while True:
            try:
                data = await asyncio.wait_for(
                    websocket.receive_json(),
                    timeout=30.0,  # 30秒超时
                )

                # 处理消息
                await handle_websocket_message(
                    session_id=session_id,
                    data=data,
                    websocket=websocket,
                )

            except asyncio.TimeoutError:
                # 发送心跳
                await ws_manager.send_personal(websocket, {
                    "type": "heartbeat",
                    "timestamp": datetime.now().isoformat(),
                })

    except WebSocketDisconnect:
        ws_manager.disconnect(websocket, session_id)

    except Exception as e:
        print(f"WebSocket error: {e}")
        ws_manager.disconnect(websocket, session_id)


async def handle_websocket_message(
    session_id: str,
    data: Dict[str, Any],
    websocket: WebSocket,
):
    """处理WebSocket消息"""
    message_type = data.get("type")

    if message_type == "moderator_command":
        # 主持人指令 — 统一由 session.handle_command 处理
        # 也转发到 HumanModerator 队列（session 内部处理）
        await engine.handle_command(session_id, data)

    elif message_type == "moderator_takeover":
        # 统一的 takeover/release 处理
        action = data.get("action")
        session = engine.sessions.get(session_id)
        if session and session.moderator_manager:
            if action == "takeover":
                await session.moderator_manager.switch_to_human()
                await engine.pause_task(session_id)
                await ws_manager.broadcast(session_id, {
                    "type": "system_event",
                    "event": "moderator_switched",
                    "data": {"type": "human", "name": data.get("human_name", "主持人")},
                })
            elif action == "release":
                await session.moderator_manager.switch_to_ai()
                await engine.resume_task(session_id)
                await ws_manager.broadcast(session_id, {
                    "type": "system_event",
                    "event": "moderator_switched",
                    "data": {"type": "ai"},
                })

    elif message_type == "request_status":
        # 请求状态更新
        status = await engine.get_session_status(session_id)
        await ws_manager.send_personal(websocket, {
            "type": "system_event",
            "event": "status_update",
            "data": status,
        })

    elif message_type == "request_history":
        # 请求历史记录
        session = engine.sessions.get(session_id)
        if session and session.results:
            await ws_manager.send_personal(websocket, {
                "type": "history",
                "data": session.get_results(),
            })

    else:
        # 未知消息类型
        await ws_manager.send_personal(websocket, {
            "type": "error",
            "message": f"Unknown message type: {message_type}",
        })
