"""Persona API"""

import uuid
from datetime import datetime
from typing import List

from fastapi import APIRouter, HTTPException

from ..llm.manager import provider_manager
from ..models.persona import (
    PersonaCreate,
    PersonaDetail,
    PersonaGenerateRequest,
    PersonaGroup,
    PersonaGroupCreate,
    PersonaGroupUpdate,
    PersonaOptimizeRequest,
    PersonaResponse,
    PersonaSummary,
    PersonaTemplate,
    PersonaUpdate,
)
from ..prompts.optimizer import PersonaOptimizer
from ..storage.config_store import persona_group_store, persona_store

router = APIRouter(prefix="/api/v1/personas", tags=["personas"])

# ========== 分组管理 API (must come before /{persona_id}) ==========

@router.get("/groups", response_model=List[PersonaGroup])
async def list_persona_groups():
    groups = []
    for g in persona_group_store.list_groups():
        groups.append(PersonaGroup(
            id=g.get("id", ""), name=g.get("name", ""),
            description=g.get("description", ""),
            persona_ids=g.get("persona_ids", []),
            created_at=g.get("created_at", ""),
        ))
    return groups


@router.post("/groups", response_model=PersonaGroup)
async def create_persona_group(group_data: PersonaGroupCreate):
    group_id = group_data.name.strip().replace(" ", "_").replace("/", "_").lower()
    data = group_data.dict()
    data["id"] = group_id
    data["created_at"] = datetime.now().isoformat()
    persona_group_store.save_group(group_id, data)
    return PersonaGroup(
        id=group_id, name=data["name"], description=data["description"],
        persona_ids=data["persona_ids"], created_at=data["created_at"],
    )


@router.put("/groups/{group_id}", response_model=PersonaGroup)
async def update_persona_group(group_id: str, group_data: PersonaGroupUpdate):
    existing = persona_group_store.get_group(group_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Group not found")
    if group_data.name is not None:
        existing["name"] = group_data.name
    if group_data.description is not None:
        existing["description"] = group_data.description
    if group_data.persona_ids is not None:
        existing["persona_ids"] = group_data.persona_ids
    persona_group_store.save_group(group_id, existing)
    return PersonaGroup(
        id=group_id, name=existing["name"], description=existing.get("description", ""),
        persona_ids=existing.get("persona_ids", []), created_at=existing.get("created_at", ""),
    )


@router.delete("/groups/{group_id}")
async def delete_persona_group(group_id: str):
    if not persona_group_store.delete_group(group_id):
        raise HTTPException(status_code=404, detail="Group not found")
    return {"message": "Group deleted", "group_id": group_id}


@router.get("/groups/{group_id}/personas", response_model=List[PersonaSummary])
async def get_group_personas(group_id: str):
    group = persona_group_store.get_group(group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    personas = []
    for pid in group.get("persona_ids", []):
        persona = persona_store.get_custom(pid)
        if persona:
            personas.append(PersonaSummary(
                id=pid, name=persona.get("name", ""),
                age=persona.get("demographics", {}).get("age", 0),
                gender=persona.get("demographics", {}).get("gender", ""),
                occupation=persona.get("demographics", {}).get("occupation", ""),
                city=persona.get("demographics", {}).get("city", ""),
                groups=persona_group_store.get_groups_for_persona(pid),
            ))
    return personas


# ========== Persona CRUD ==========

@router.post("/", response_model=PersonaResponse)
async def create_persona(persona_data: PersonaCreate):
    persona_id = str(uuid.uuid4())
    data = persona_data.dict()
    data["id"] = persona_id
    data["version"] = "1.0"
    persona_store.save_custom(persona_id, data)
    return PersonaResponse(
        id=persona_id, name=persona_data.name, version="1.0",
    )


@router.get("/", response_model=List[PersonaSummary])
async def list_personas():
    personas = []
    for persona in persona_store.list_custom():
        pid = persona.get("id", "")
        personas.append(PersonaSummary(
            id=pid, name=persona.get("name", ""),
            age=persona.get("demographics", {}).get("age", 0),
            gender=persona.get("demographics", {}).get("gender", ""),
            occupation=persona.get("demographics", {}).get("occupation", ""),
            city=persona.get("demographics", {}).get("city", ""),
            groups=persona_group_store.get_groups_for_persona(pid),
        ))
    return personas


@router.get("/templates", response_model=List[PersonaTemplate])
async def list_persona_templates():
    templates = []
    for template in persona_store.list_templates():
        templates.append(PersonaTemplate(
            id=template.get("id", ""), name=template.get("name", ""),
            emoji=template.get("emoji", "👤"), description=template.get("description", ""),
            demographics=template.get("demographics", {}),
            psychographics=template.get("psychographics", {}),
            background=template.get("background", {}),
            initial_attitudes=template.get("initial_attitudes", {}),
        ))
    return templates


@router.get("/{persona_id}", response_model=PersonaDetail)
async def get_persona(persona_id: str):
    persona = persona_store.get_custom(persona_id)
    if not persona:
        persona = persona_store.get_template(persona_id)
    if not persona:
        raise HTTPException(status_code=404, detail="Persona not found")
    pid = persona.get("id", persona_id)
    return PersonaDetail(
        id=pid, name=persona.get("name", ""), version=persona.get("version", "1.0"),
        demographics=persona.get("demographics", {}),
        psychographics=persona.get("psychographics", {}),
        background=persona.get("background", {}),
        initial_attitudes=persona.get("initial_attitudes", {}),
        groups=persona_group_store.get_groups_for_persona(pid),
    )


@router.put("/{persona_id}", response_model=PersonaResponse)
async def update_persona(persona_id: str, persona_data: PersonaUpdate):
    persona = persona_store.get_custom(persona_id)
    if not persona:
        raise HTTPException(status_code=404, detail="Persona not found")
    if persona_data.name is not None:
        persona["name"] = persona_data.name
    if persona_data.demographics is not None:
        persona["demographics"] = persona_data.demographics.dict()
    if persona_data.psychographics is not None:
        persona["psychographics"] = persona_data.psychographics.dict()
    if persona_data.background is not None:
        persona["background"] = persona_data.background.dict()
    if persona_data.initial_attitudes is not None:
        persona["initial_attitudes"] = persona_data.initial_attitudes
    persona_store.save_custom(persona_id, persona)
    return PersonaResponse(
        id=persona_id, name=persona.get("name", ""), version=persona.get("version", "1.0"),
    )


@router.delete("/{persona_id}")
async def delete_persona(persona_id: str):
    if not persona_store.delete_custom(persona_id):
        raise HTTPException(status_code=404, detail="Persona not found")
    return {"message": "Persona deleted", "persona_id": persona_id}


@router.post("/{persona_id}/optimize", response_model=PersonaResponse)
async def optimize_persona(persona_id: str, request: PersonaOptimizeRequest):
    base_persona = None
    if request.persona_id:
        base_persona = persona_store.get_custom(request.persona_id)
    elif request.template_id:
        base_persona = persona_store.get_template(request.template_id)
    elif persona_id and persona_id != "optimize":
        base_persona = persona_store.get_custom(persona_id) or persona_store.get_template(persona_id)
    if not base_persona:
        base_persona = persona_store.get_template("elderly")

    provider = provider_manager.get(request.provider_pack)
    if not provider:
        raise HTTPException(status_code=400, detail=f"LLM provider '{request.provider_pack}' not configured")

    optimizer = PersonaOptimizer(provider, request.model)
    try:
        result = await optimizer.optimize(base_persona, request.target_description)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Optimization failed: {str(e)}")
    new_persona_id = str(uuid.uuid4())
    result["id"] = new_persona_id
    result["version"] = "1.0"
    persona_store.save_custom(new_persona_id, result)
    return PersonaResponse(id=new_persona_id, name=result.get("name", ""), version="1.0")


@router.post("/generate", response_model=List[PersonaResponse])
async def generate_personas(request: PersonaGenerateRequest):
    provider = provider_manager.get("OpenAI")
    if not provider:
        raise HTTPException(status_code=400, detail="LLM provider not configured")
    optimizer = PersonaOptimizer(provider, "gpt-4o-mini")
    try:
        results = await optimizer.generate(request.description, request.count)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")
    responses = []
    for result in results:
        persona_id = str(uuid.uuid4())
        result["id"] = persona_id
        result["version"] = "1.0"
        persona_store.save_custom(persona_id, result)
        responses.append(PersonaResponse(id=persona_id, name=result.get("name", ""), version="1.0"))
    return responses


@router.post("/from-template/{template_id}", response_model=PersonaResponse)
async def create_from_template(template_id: str):
    template = persona_store.get_template(template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    persona_id = str(uuid.uuid4())
    persona = template.copy()
    persona["id"] = persona_id
    persona["name"] = f"{template.get('name', '')} - 副本"
    persona["version"] = "1.0"
    persona_store.save_custom(persona_id, persona)
    return PersonaResponse(id=persona_id, name=persona["name"], version="1.0")
