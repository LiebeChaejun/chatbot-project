import os
from typing import Annotated, Literal
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

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
file_path = os.path.join(BASE_DIR, "data", "manual.txt")

# --- RAG 기반 설정 ---
loader = TextLoader(file_path=file_path, encoding="utf-8")
documents = loader.load()

optimal_chunk_size = get_optimal_chunk_size(file_path)
text_splitter = RecursiveCharacterTextSplitter(chunk_size=optimal_chunk_size, chunk_overlap=0)
docs = text_splitter.split_documents(documents)

embeddings = HuggingFaceEmbeddings(
    model_name="BAAI/bge-m3",
    encode_kwargs={"normalize_embeddings": True}
)
vectorstore = FAISS.from_documents(docs, embeddings)
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
output_parser = StrOutputParser()

# --- [신규] 의도 분류 체인 ---
route_system_prompt = """당신은 사용자의 질문 의도를 분류하는 라우터입니다.

최신 사용자 질문(question)을 보고, 아래 두 가지 중 하나로만 분류하세요.

- "manual": 온라인 교육 플랫폼의 정책, 환불, 결제, 수강, 서비스 이용 등 매뉴얼을 검색해서 답해야 하는 질문
- "general": 인사, 안부, 잡담 등 매뉴얼 검색이 필요 없는 일상적인 대화

규칙:
1. 반드시 "manual" 또는 "general" 중 하나의 단어만 출력하세요.
2. 설명, 문장부호, 다른 텍스트를 추가하지 마세요."""

route_prompt = ChatPromptTemplate.from_messages([
    ("system", route_system_prompt),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{question}")
])
route_chain = route_prompt | llm | output_parser

# --- 질문 재구성 체인 ---
rephrase_system_prompt = """당신은 대화형 검색 시스템의 질의 재구성(query rewriting) 모듈입니다.

아래에 주어진 채팅 기록(chat_history)과 최신 사용자 질문(question)을 참고하여,
최신 사용자 질문을 채팅 기록 없이도 완전히 이해할 수 있는 독립적인 질문으로 재구성하세요.

규칙:
1. 최신 사용자 질문이 채팅 기록의 맥락에 의존하는 모호한 질문이라면,
   채팅 기록에서 지시 대상을 찾아 명시적으로 포함한 독립적인 질문으로 다시 작성하세요.
2. 최신 사용자 질문이 채팅 기록 없이도 이미 그 자체로 이해 가능한 독립적인 질문이라면,
   내용을 바꾸지 말고 그대로 반환하세요.
3. 질문에 답하지 마세요. 질문을 재구성하거나 그대로 반환하는 것 외의 다른 작업은 하지 마세요.
4. 결과는 재구성된 질문 하나만 출력하세요. 설명, 접두사, 따옴표 등을 추가하지 마세요."""

rephrase_prompt = ChatPromptTemplate.from_messages([
    ("system", rephrase_system_prompt),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{question}")
])
rephrase_chain = rephrase_prompt | llm | output_parser

# --- 답변 생성 체인 ---
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
rag_chain = prompt | llm | output_parser


# --- 그래프 상태 ---
class AgentState(BaseModel):
    messages: Annotated[list[BaseMessage], add_messages] = Field(default_factory=list)
    intent: str = ""
    rephrased_query: str = ""
    context: str = ""


# --- 노드 1: 의도 분류 ---
async def route_node(state: AgentState) -> dict:
    question = state.messages[-1].content
    chat_history = state.messages[:-1]

    result = await route_chain.ainvoke({
        "chat_history": chat_history,
        "question": question,
    })

    intent = result.strip().lower()
    if intent not in ("manual", "general"):
        intent = "manual"  # 분류가 애매하면 안전하게 매뉴얼 검색 경로로

    return {"intent": intent}


# --- 분기 함수: route_node의 결과를 보고 다음 노드를 결정 ---
def decide_next(state: AgentState) -> Literal["rephrase", "general_answer"]:
    return "rephrase" if state.intent == "manual" else "general_answer"


# --- 노드 2: 질문 재구성 ---
async def rephrase_node(state: AgentState) -> dict:
    latest_question = state.messages[-1].content
    chat_history = state.messages[:-1]

    if chat_history:
        query = await rephrase_chain.ainvoke({
            "chat_history": chat_history,
            "question": latest_question,
        })
    else:
        query = latest_question

    return {"rephrased_query": query}


# --- 노드 3: 문서 검색 ---
async def retriever_node(state: AgentState) -> dict:
    retrieved_docs = await retriever.ainvoke(state.rephrased_query)
    context_text = "\n\n---\n\n".join(doc.page_content for doc in retrieved_docs)
    return {"context": context_text}


# --- 노드 4: 매뉴얼 기반 답변 생성 ---
async def answer_node(state: AgentState) -> dict:
    question = state.messages[-1].content
    chat_history = state.messages[:-1]

    response = await rag_chain.ainvoke({
        "context": state.context,
        "chat_history": chat_history,
        "question": question,
    })
    return {"messages": [AIMessage(content=response)]}


# --- 노드 5: 일반 대화 답변 생성 ---
async def general_answer_node(state: AgentState) -> dict:
    # 매뉴얼 검색 없이, 지금까지의 대화 맥락 전체를 그대로 LLM에 전달
    response = await llm.ainvoke(state.messages)
    return {"messages": [AIMessage(content=response.content)]}


# --- 그래프 구성 ---
workflow = StateGraph(AgentState)
workflow.add_node("route", route_node)
workflow.add_node("rephrase", rephrase_node)
workflow.add_node("retriever", retriever_node)
workflow.add_node("answer", answer_node)
workflow.add_node("general_answer", general_answer_node)

workflow.set_entry_point("route")

# route_node 이후 분기: 매뉴얼 관련이면 rephrase로, 아니면 general_answer로
workflow.add_conditional_edges(
    "route",
    decide_next,
    {"rephrase": "rephrase", "general_answer": "general_answer"},
)

# 매뉴얼 경로: rephrase → retriever → answer, 여긴 분기가 없으니 그대로 add_edge
workflow.add_edge("rephrase", "retriever")
workflow.add_edge("retriever", "answer")
workflow.add_edge("answer", END)

# 일반 대화 경로: 바로 종료
workflow.add_edge("general_answer", END)