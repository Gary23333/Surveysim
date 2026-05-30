"""API路由"""

from .behavior_prompts import router as behavior_prompts_router
from .providers import router as providers_router
from .surveys import router as surveys_router
from .tasks import router as tasks_router
from .personas import router as personas_router
from .websocket import router as websocket_router, ws_manager

__all__ = [
    "tasks_router",
    "surveys_router",
    "personas_router",
    "providers_router",
    "behavior_prompts_router",
    "websocket_router",
    "ws_manager",
]
