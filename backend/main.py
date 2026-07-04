import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"), override=True)

from langchain_core.messages import HumanMessage
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from graph.agent import workflow
from db.conversations import init_conversations_db, touch_conversation, create_conversation
from routers.conversations import router as conversations_router

CHECKPOINT_DB_PATH = os.path.join(BASE_DIR, "history_single_agent.sqlite")
CONVERSATIONS_DB_PATH = os.path.join(BASE_DIR, "conversations.sqlite")

app_state = {}


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
async def chat(req: ChatRequest):
    try:
        agent = app_state["agent"]
        config = {"configurable": {"thread_id": req.thread_id}}
        initial_state = {"messages": [HumanMessage(content=req.message)]}
        final_state = await agent.ainvoke(initial_state, config=config)

        # 대화 목록의 updated_at 갱신 (최근 대화가 위로 올라오도록)
        await touch_conversation(app_state["conversations_db_path"], req.thread_id)

        return {"response": final_state["messages"][-1].content}
    except Exception as e:
        return {"error": str(e)}