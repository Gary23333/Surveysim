"""FastAPI主应用"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api import (
    behavior_prompts_router,
    personas_router,
    providers_router,
    surveys_router,
    tasks_router,
    websocket_router,
)
from .config import settings
from .llm.manager import provider_manager
from .llm.adapters.openai import OpenAIProvider
from .llm.pack import pack_manager
from .storage.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期"""
    # 启动时初始化
    print("Starting Virtual Survey...")

    # 确保目录存在
    settings.ensure_dirs()

    # 初始化数据库
    init_db()

    # 加载Provider配置
    pack_manager.load_packs()

    # 注册所有Provider（包括未配置 API Key 的，查找时不会报错，实际调用时会提示）
    for pack_name in pack_manager.list_packs():
        pack = pack_manager.get_pack(pack_name)
        if pack:
            provider = OpenAIProvider(
                api_key=pack.api_key or "",
                base_url=pack.base_url,
                auth_header=pack.auth_header,
            )
            provider_manager.register(pack.name, provider)
            status = "configured" if pack.api_key else "no API key"
            print(f"{pack.name} provider registered ({status})")

    print("Virtual Survey started!")

    yield

    # 关闭时清理
    print("Shutting down Virtual Survey...")


# 创建FastAPI应用
app = FastAPI(
    title="Virtual Survey",
    description="大模型驱动的模拟问卷调查与群体调研平台",
    version="1.0.0",
    lifespan=lifespan,
    redirect_slashes=True,
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:3002", "http://127.0.0.1:3002"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(tasks_router)
app.include_router(surveys_router)
app.include_router(personas_router)
app.include_router(providers_router)
app.include_router(behavior_prompts_router)
app.include_router(websocket_router)


@app.get("/")
async def root():
    """根路径"""
    return {
        "name": "Virtual Survey",
        "version": "1.0.0",
        "description": "大模型驱动的模拟问卷调查与群体调研平台",
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "ok"}
