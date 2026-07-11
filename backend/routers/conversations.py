from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from db.conversations import (
  create_conversation,
  list_conversations,
  update_conversation_title
)
from dependencies import get_app_state

router = APIRouter(prefix="/conversations", tags=["conversations"])

@router.post("")
async def create_new_conversation():
  app_state = get_app_state()
  import uuid
  thread_id = str(uuid.uuid4())
  conversation = await create_conversation(
    app_state["conversations_db_path"], thread_id
  )

  return conversation

@router.get("")
async def get_conversations():
  app_state = get_app_state()
  conversations = await list_conversations(app_state["conversations_db_path"])
  return {"conversations": conversations}

class UpdateTitleRequest(BaseModel):
    title: str

@router.patch("/{thread_id}")
async def rename_conversation(thread_id: str, req: UpdateTitleRequest):
    if not req.title.strip():
        raise HTTPException(status_code=400, detail="제목은 비어있을 수 없습니다.")

    app_state = get_app_state()
    await update_conversation_title(
        app_state["conversations_db_path"], thread_id, req.title.strip()
    )
    return {"thread_id": thread_id, "title": req.title.strip()}

@router.get("/{thread_id}/messages")
async def get_conversation_messages(thread_id: str):
  app_state = get_app_state()
  agent = app_state["agent"]
  config = {"configurable": {"thread_id": thread_id}}

  state = await agent.aget_state(config)
  raw_messages = state.values.get("messages", []) if state.values else []

  # LangChain 메시지 객체를 프론트가 쓰기 쉬운 JSON 형탤 변환
  messages = []
  for msg in raw_messages:
    role = "user" if msg.type == "human" else "assistant"
    messages.append({"role": role, "content": msg.content})

  if not messages:
    raise HTTPException(status_code=404, detail="대화를 찾을 수 없습니다.")
  
  return {"thread_id": thread_id, "messages": messages}