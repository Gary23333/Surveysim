"""Provider配置API"""

from typing import List, Optional
import httpx

from fastapi import APIRouter, HTTPException

from ..llm.pack import ModelInfo, ProviderPack, pack_manager
from ..storage.config_store import provider_store

router = APIRouter(prefix="/api/v1/providers", tags=["providers"])


@router.get("/")
async def list_providers():
    """获取Provider列表"""
    providers = provider_store.list_providers()
    return providers


@router.get("/{provider_name}")
async def get_provider(provider_name: str):
    """获取Provider详情"""
    provider = provider_store.get_provider(provider_name)
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")

    return provider


@router.post("/")
async def create_provider(provider_data: dict):
    """创建Provider配置"""
    name = provider_data.get("name")
    if not name:
        raise HTTPException(status_code=400, detail="Name is required")

    # 检查是否已存在
    if provider_store.get_provider(name):
        raise HTTPException(status_code=400, detail="Provider already exists")

    # 保存
    provider_store.save_provider(name, provider_data)

    # 加载到pack_manager
    pack = ProviderPack.from_dict(provider_data)
    pack_manager.add_pack(pack)

    return {"message": "Provider created", "name": name}


@router.put("/{provider_name}")
async def update_provider(provider_name: str, provider_data: dict):
    """更新Provider配置"""
    existing = provider_store.get_provider(provider_name)
    if not existing:
        raise HTTPException(status_code=404, detail="Provider not found")

    # 如果api_key为空或被遮盖，保留原有api_key
    api_key = provider_data.get("api_key", "")
    if not api_key or api_key == "***":
        provider_data["api_key"] = existing.get("api_key", "")

    # 更新
    provider_data["name"] = provider_name
    provider_store.save_provider(provider_name, provider_data)

    # 更新pack_manager
    pack = ProviderPack.from_dict(provider_data)
    pack_manager.add_pack(pack)

    return {"message": "Provider updated", "name": provider_name}


@router.delete("/{provider_name}")
async def delete_provider(provider_name: str):
    """删除Provider配置"""
    if not provider_store.delete_provider(provider_name):
        raise HTTPException(status_code=404, detail="Provider not found")

    # 从pack_manager移除
    pack_manager.remove_pack(provider_name)

    return {"message": "Provider deleted", "name": provider_name}


@router.get("/{provider_name}/models")
async def list_provider_models(provider_name: str):
    """获取Provider支持的模型列表"""
    provider = provider_store.get_provider(provider_name)
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")

    return provider.get("models", [])


@router.post("/{provider_name}/test")
async def test_provider(provider_name: str):
    """测试Provider连接"""
    provider = provider_store.get_provider(provider_name)
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")

    try:
        pack = ProviderPack.from_dict(provider)
        return {
            "message": "Provider configuration is valid",
            "name": provider_name,
            "models": [m.id for m in pack.models],
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid configuration: {str(e)}")


@router.post("/{provider_name}/test-connect")
async def test_provider_connection(provider_name: str):
    """真实测试Provider API连通性"""
    provider = provider_store.get_provider(provider_name)
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")

    try:
        pack = ProviderPack.from_dict(provider)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid configuration: {str(e)}")

    headers = {"Content-Type": "application/json"}
    if pack.auth_header == "api-key":
        headers["api-key"] = pack.api_key
    else:
        headers["Authorization"] = f"Bearer {pack.api_key}"

    import time
    start = time.time()
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(
                f"{pack.base_url}/chat/completions",
                headers=headers,
                json={
                    "model": pack.default_model,
                    "messages": [{"role": "user", "content": "Hi"}],
                    "max_tokens": 5,
                    pack.max_tokens_param: 5,
                    "stream": False,
                },
            )
            latency = round((time.time() - start) * 1000)
            if resp.status_code == 200:
                data = resp.json()
                return {
                    "success": True,
                    "latency_ms": latency,
                    "model": pack.default_model,
                    "provider": provider_name,
                    "message": "连通性测试成功",
                    "usage": data.get("usage", {}),
                }
            else:
                return {
                    "success": False,
                    "latency_ms": latency,
                    "status_code": resp.status_code,
                    "error": resp.text[:500],
                }
    except Exception as e:
        return {
            "success": False,
            "latency_ms": round((time.time() - start) * 1000),
            "error": str(e)[:500],
        }


@router.post("/{provider_name}/detect-models")
async def detect_models(provider_name: str):
    """从Provider API获取可用模型列表"""
    provider = provider_store.get_provider(provider_name)
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")

    try:
        pack = ProviderPack.from_dict(provider)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid configuration: {str(e)}")

    headers = {"Content-Type": "application/json"}
    if pack.auth_header == "api-key":
        headers["api-key"] = pack.api_key
    else:
        headers["Authorization"] = f"Bearer {pack.api_key}"

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(
                f"{pack.base_url}/models",
                headers=headers,
            )
            if resp.status_code == 200:
                data = resp.json()
                models = []
                for m in data.get("data", []):
                    models.append({
                        "id": m.get("id", ""),
                        "name": m.get("id", ""),
                        "owned_by": m.get("owned_by", ""),
                    })
                return {
                    "success": True,
                    "total": len(models),
                    "models": models,
                }
            else:
                return {
                    "success": False,
                    "status_code": resp.status_code,
                    "error": resp.text[:500],
                }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)[:500],
        }
