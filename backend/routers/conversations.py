from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel
from typing import Any
from db.conversations import (
    create_conversation,
    list_conversations,
    update_conversation_title,
    is_owner,
)
from dependencies import get_app_state

router = APIRouter(prefix="/conversations", tags=["conversations"])


@router.post("")
async def create_new_conversation(
    x_owner_id: str = Header(...),
    app_state: dict[str, Any] = Depends(get_app_state),
):
    import uuid
    thread_id = str(uuid.uuid4())
    conversation = await create_conversation(
        app_state["conversations_db_path"], thread_id, x_owner_id
    )
    return conversation


@router.get("")
async def get_conversations(
    x_owner_id: str = Header(...),
    app_state: dict[str, Any] = Depends(get_app_state),
):
    conversations = await list_conversations(
        app_state["conversations_db_path"], x_owner_id
    )
    return {"conversations": conversations}


class UpdateTitleRequest(BaseModel):
    title: str


@router.patch("/{thread_id}")
async def rename_conversation(
    thread_id: str,
    req: UpdateTitleRequest,
    x_owner_id: str = Header(...),
    app_state: dict[str, Any] = Depends(get_app_state),
):
    if not req.title.strip():
        raise HTTPException(status_code=400, detail="제목은 비어있을 수 없습니다.")

    if not await is_owner(app_state["conversations_db_path"], thread_id, x_owner_id):
        raise HTTPException(status_code=404, detail="대화를 찾을 수 없습니다.")

    await update_conversation_title(
        app_state["conversations_db_path"], thread_id, req.title.strip()
    )
    return {"thread_id": thread_id, "title": req.title.strip()}


@router.get("/{thread_id}/messages")
async def get_conversation_messages(
    thread_id: str,
    x_owner_id: str = Header(...),
    app_state: dict[str, Any] = Depends(get_app_state),
):
    if not await is_owner(app_state["conversations_db_path"], thread_id, x_owner_id):
        raise HTTPException(status_code=404, detail="대화를 찾을 수 없습니다.")

    agent = app_state["agent"]
    config = {"configurable": {"thread_id": thread_id}}

    state = await agent.aget_state(config)
    raw_messages = state.values.get("messages", []) if state.values else []

    messages = []
    for msg in raw_messages:
        role = "user" if msg.type == "human" else "assistant"
        messages.append({"role": role, "content": msg.content})

    if not messages:
        raise HTTPException(status_code=404, detail="대화를 찾을 수 없습니다.")

    return {"thread_id": thread_id, "messages": messages}