import os
from dotenv import load_dotenv

# --- .env 절대경로로 로드 ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"), override=True)

from contextlib import asynccontextmanager
from fastapi import FastAPI
from pydantic import BaseModel
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from fastapi.middleware.cors import CORSMiddleware

from graph.agent import workflow



DB_PATH = os.path.join(BASE_DIR, "history_single_agent.sqlite")

# 앱 전역에서 재사용할 agent 객체(lifespan에서 채워짐)
app_state ={}

@asynccontextmanager
async def lifespan(app: FastAPI):
  # 서버 시작 시: DB 커넥션 열고 그래프 compile
  async with AsyncSqliteSaver.from_conn_string("history_single_agent.sqlite") as memory:
    app_state["agent"] = workflow.compile(checkpointer=memory)
    yield
  # 서버 종료 시: async with 블록을 벗어나며 커넥션 자동 종료

app = FastAPI(lifespan=lifespan)

app.add_middleware(
  CORSMiddleware,
  allow_origins=["http://localhost:5173"],
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"]
)

class ChatRequest(BaseModel):
  message: str
  thread_id: str

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/chat")
async def chat(req: ChatRequest):
  agent = app_state["agent"]
  config = {"configurable": {"thread_id": req.thread_id}}

  initial_state = {"messages": [HumanMessage(content=req.message)]}
  final_state = await agent.ainvoke(initial_state, config=config)

  return {"response": final_state["messages"][-1].content}