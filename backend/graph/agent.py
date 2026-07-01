import os
from typing import Annotated
from pydantic import BaseModel, Field
from langchain_core.messages import BaseMessage, AIMessage
from langchain_openai import ChatOpenAI
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langgraph.graph import add_messages, StateGraph, END

from utils.text_splitter import get_optimal_chunk_size

# --- 파일 경로를 절대 경로로 수정 ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(BASE_DIR, "data", "manual.txt")

# --- RAG 기반 설정 ---
## text 데이터 분할 처리
file_path = "data/manual.txt"
loader = TextLoader(file_path=file_path, encoding="utf-8")
documents = loader.load()

optimal_chunk_size = get_optimal_chunk_size(file_path)
text_splitter = RecursiveCharacterTextSplitter(chunk_size=optimal_chunk_size, chunk_overlap=0)
docs = text_splitter.split_documents(documents)

embeddings = HuggingFaceEmbeddings(
  model_name="BAAI/bge-m3",
  encode_kwargs={'normalize_embeddings': True}
)
vectorstore = FAISS.from_documents(docs, embeddings)
retriever = vectorstore.as_retriever(search_kwargs={'k': 1})

## LCEL RAG 체인 구성
system_prompt = """당신은 친절한 온라인 교육 플랫폼 직원입니다. 주어진 컨텍스트
정보를 바탕으로 고객의 질문에 정중하게 답변해주세요.
주어진 컨텍스트 정보는 고객의 질문에 대한 답변입니다. 컨텍스트를 그대로 사용하여
답변하거나, 컨텍스트의 내용을 바탕으로 자연스럽게 답변을 재구성해주세요.
답변을 할 때는 '답변:'이라는 표현을 사용하지 말아야 하며, 컨텍스트에 질문에 대한
정보가 없다면, '죄송하지만 문의하신 내용에 대해서는 아는 바가 없습니다.'라고 답변해주세요."""

prompt = ChatPromptTemplate.from_messages([
  ("system", system_prompt),
  MessagesPlaceholder(variable_name="chat_history"),
  ("human", "컨텍스트:\n{context}\n\n질문:\n{question}")
])

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)

output_parser = StrOutputParser()

rag_chain = prompt | llm | output_parser

## 그래프 상태 정의
class AgentState(BaseModel):
  messages: Annotated[list[BaseMessage], add_messages] = Field(default_factory=list)

async def rag_node(state: AgentState):
  question = state.messages[-1].content
  chat_history = state.messages[:-1]

  retrieved_docs = await retriever.ainvoke(question)
  context_text = retrieved_docs[0].page_content

  response = await rag_chain.ainvoke({
    "context": context_text,
    "chat_history": chat_history,
    "question": question
  })

  return {"messages": [AIMessage(content=response)]}

# 그래프는 "정의"만 하고, compile은 main.py의 lifespan에서 checkpointer와 함께 수행
workflow = StateGraph(AgentState)
workflow.add_node("rag_node", rag_node)
workflow.set_entry_point("rag_node")
workflow.add_edge("rag_node", END)