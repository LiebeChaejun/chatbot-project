import os
from typing import Annotated, Literal
from pydantic import BaseModel, Field
from langchain_core.messages import BaseMessage, AIMessage, SystemMessage
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

# 분류/재구성처럼 "정확하고 일관된 판단"이 필요한 작업용(창의성 불필요)
classifier_llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# 실제 답변 생성처럼 "자연스러운 문장"이 필요한 작업용
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)

output_parser = StrOutputParser()

# --- [신규] 의도 분류 체인 ---
route_system_prompt = """당신은 사용자의 질문 의도를 분류하는 라우터입니다.

최신 사용자 질문(question)을 보고, 아래 두 가지 중 하나로만 분류하세요.

- "manual": 코드크래프터스 아카데미(온라인 교육 플랫폼)의 정책, 환불, 결제,
  수강, 강의 내용/커리큘럼, 배송, 계정, 기술 지원 등 서비스나 상품에 관한
  구체적인 질문. 매뉴얼에 실제로 그 답이 있는지 여부와 관계없이 이 범주에
  속하면 "manual"로 분류하세요.
- "general": 인사, 안부, 날씨, 식사 여부, 감사 인사, 잡담 등 특정 서비스나
  상품을 직접 묻지 않는 일상 대화. 대화 맥락(chat_history)에 강의나 서비스
  이야기가 있었더라도, 최신 질문 자체가 그 내용을 구체적으로 묻는 게
  아니라면 "general"로 분류하세요.

분류 예시:
- "환불 규정이 어떻게 되나요?" → manual
- "배송비는 얼마야?" → manual (매뉴얼에 답이 없어도 서비스 관련 질문이므로 manual)
- "어떤 강의를 들을 수 있나요?" → manual
- "안녕하세요" → general
- "밥 먹었어?" → general
- "오늘 날씨 어때?" → general
- "고마워" → general
- "잘 지내?" → general

규칙:
1. 최신 질문이 회사의 구체적인 서비스, 정책, 상품, 강의 내용을 직접
   묻고 있을 때만 "manual"로 분류하세요.
2. 안부, 감사, 잡담처럼 특정 대상을 묻지 않는 가벼운 대화는 이전 대화
   맥락과 관계없이 "general"로 분류하세요.
3. 반드시 "manual" 또는 "general" 중 하나의 단어만 출력하세요.
4. 설명, 문장부호, 다른 텍스트를 추가하지 마세요."""

route_prompt = ChatPromptTemplate.from_messages([
    ("system", route_system_prompt),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{question}")
])
route_chain = route_prompt | classifier_llm | output_parser

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
rephrase_chain = rephrase_prompt | classifier_llm | output_parser

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
general_system_prompt = """당신은 코드크래프터스 아카데미의 챗봇입니다.
인사, 안부 등 가벼운 대화에는 자연스럽고 친근하게 응답하세요.

다만 회사의 서비스, 정책, 상품, 가격 등에 관한 질문을 받으면 절대로 스스로 추측해서
답변하지 마세요. 대신 정확한 안내를 위해 다시 질문해 달라고 요청하세요.

가벼운 인사나 잡담에 응답할 때는 다음 순서를 따르세요:
1. 먼저 상대방의 말에 짧고 자연스럽게 반응하세요 (예: 안부를 물으면 안부로 화답, 잡담이면 공감 한마디).
2. 그 다음, 대화 흐름이 자연스럽다면 코드크래프터스 아카데미의 강의나 서비스로
   부드럽게 이어질 수 있는 말을 한 문장만 덧붙이세요. 질문을 덧붙일 경우
   반드시 질문은 하나만 하세요 (두 개 이상의 물음표를 한 답변에 넣지 마세요).

유도 문장의 예시(이 표현들을 그대로 반복하지 말고 참고만 하세요):
- "오늘은 어떤 걸 도와드릴까요?"
- "혹시 요즘 관심 있는 학습 주제가 있으신가요?"
- "학습하시다가 막히는 부분 있으면 언제든 물어보세요."
- "쉬시는 김에 새로운 강의도 한번 둘러보시는 건 어때요?"

규칙:
- 답변의 약 40% 정도는 유도 문장 없이, 순수하게 상대방 말에 반응만 하고 끝내세요.
  매번 화제를 돌리면 영업하는 것처럼 느껴져 부자연스럽습니다.
- 유도 문장을 붙일 때도 매번 같은 표현을 쓰지 말고 대화 맥락에 맞게 다양하게 표현하세요.
- 한 답변에 질문은 최대 1개까지만 포함하세요."""


async def general_answer_node(state: AgentState) -> dict:
    # 매뉴얼 검색 없이, 지금까지의 대화 맥락 전체를 그대로 LLM에 전달하되
    # 서비스 관련 질문에는 추측 답변을 하지 않도록 시스템 프롬프트로 가드
    messages_with_system = [SystemMessage(content=general_system_prompt)] + list(state.messages)
    response = await llm.ainvoke(messages_with_system)
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