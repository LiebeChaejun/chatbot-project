import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"), override=True)

from langchain_core.messages import HumanMessage
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from graph.agent import workflow
from db.conversations import init_conversations_db, touch_conversation, update_conversation_title, is_owner
from routers.conversations import router as conversations_router
from dependencies import app_state

CHECKPOINT_DB_PATH = os.path.join(BASE_DIR, "history_single_agent.sqlite")
CONVERSATIONS_DB_PATH = os.path.join(BASE_DIR, "conversations.sqlite")

TITLE_MAX_LENGTH = 20


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_conversations_db(CONVERSATIONS_DB_PATH)
    app_state["conversations_db_path"] = CONVERSATIONS_DB_PATH

    async with AsyncSqliteSaver.from_conn_string(CHECKPOINT_DB_PATH) as memory:
        app_state["agent"] = workflow.compile(checkpointer=memory)
        yield


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(conversations_router)


from pydantic import BaseModel

class ChatRequest(BaseModel):
    message: str
    thread_id: str


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/chat")
async def chat(req: ChatRequest, x_owner_id: str = Header(...)):
    try:
        # --- 소유자 검증: 이 thread_id가 요청자의 것이 맞는지 먼저 확인 ---
        if not await is_owner(app_state["conversations_db_path"], req.thread_id, x_owner_id):
            raise HTTPException(status_code=404, detail="대화를 찾을 수 없습니다.")

        agent = app_state["agent"]
        config = {"configurable": {"thread_id": req.thread_id}}

        existing_state = await agent.aget_state(config)
        is_first_message = not existing_state.values.get("messages")

        initial_state = {"messages": [HumanMessage(content=req.message)]}
        final_state = await agent.ainvoke(initial_state, config=config)

        if is_first_message:
            title = req.message[:TITLE_MAX_LENGTH]
            if len(req.message) > TITLE_MAX_LENGTH:
                title += "..."
            await update_conversation_title(
                app_state["conversations_db_path"], req.thread_id, title
            )
        else:
            await touch_conversation(app_state["conversations_db_path"], req.thread_id)

        return {"response": final_state["messages"][-1].content}
    except HTTPException:
        raise   # 소유자 검증 실패는 그대로 404로 전달 (아래 except Exception에 안 걸리게)
    except Exception as e:
        return {"error": str(e)}