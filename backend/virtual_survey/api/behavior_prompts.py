"""行为提示词API"""

from typing import List

from fastapi import APIRouter, HTTPException

from ..storage.config_store import behavior_prompt_store

router = APIRouter(prefix="/api/v1/behavior-prompts", tags=["behavior-prompts"])


@router.get("/")
async def list_behavior_prompts():
    """获取行为提示词列表"""
    prompts = behavior_prompt_store.list_prompts()
    return prompts


@router.get("/{prompt_id}")
async def get_behavior_prompt(prompt_id: str):
    """获取行为提示词详情"""
    prompt = behavior_prompt_store.get_prompt(prompt_id)
    if not prompt:
        raise HTTPException(status_code=404, detail="Behavior prompt not found")

    return prompt


@router.post("/")
async def create_behavior_prompt(prompt_data: dict):
    """创建行为提示词"""
    prompt_id = prompt_data.get("id")
    if not prompt_id:
        raise HTTPException(status_code=400, detail="ID is required")

    # 检查是否已存在
    if behavior_prompt_store.get_prompt(prompt_id):
        raise HTTPException(status_code=400, detail="Behavior prompt already exists")

    # 保存
    behavior_prompt_store.save_prompt(prompt_id, prompt_data)

    return {"message": "Behavior prompt created", "id": prompt_id}


@router.put("/{prompt_id}")
async def update_behavior_prompt(prompt_id: str, prompt_data: dict):
    """更新行为提示词"""
    prompt = behavior_prompt_store.get_prompt(prompt_id)
    if not prompt:
        raise HTTPException(status_code=404, detail="Behavior prompt not found")

    # 更新
    prompt_data["id"] = prompt_id
    behavior_prompt_store.save_prompt(prompt_id, prompt_data)

    return {"message": "Behavior prompt updated", "id": prompt_id}


@router.delete("/{prompt_id}")
async def delete_behavior_prompt(prompt_id: str):
    """删除行为提示词"""
    if not behavior_prompt_store.delete_prompt(prompt_id):
        raise HTTPException(status_code=404, detail="Behavior prompt not found")

    return {"message": "Behavior prompt deleted", "id": prompt_id}
