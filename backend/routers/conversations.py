from fastapi import APIRouter, HTTPException
from db.conversations import (
  create_conversation,
  list_conversations,
)

router = APIRouter(prefix="/conversations", tags=["conversations"])

def get_app_state():
  # main.py의 app_state를 참조하기 위한 지연 import (순환 참조 방지)
  from main import app_state
  return app_state

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