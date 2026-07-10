# RAG 챗봇 프로젝트

LangGraph 기반 RAG(Retrieval-Augmented Generation) 챗봇에, 멀티 세션 대화 관리 기능을 더한 풀스택 프로젝트입니다. 사내 매뉴얼 문서를 검색해 답변하는 온라인 교육 플랫폼 고객센터 챗봇을 가정하고 만들었습니다.

## 주요 기능

- **RAG 기반 질의응답**: 사내 매뉴얼 문서(FAQ)를 벡터 검색 후, 검색된 컨텍스트를 바탕으로 답변 생성
- **대화 맥락 유지**: LangGraph checkpointer로 같은 대화(thread) 내에서 이전 질문/답변을 기억
- **멀티 세션 대화 관리**: 여러 개의 대화를 독립적으로 생성·조회·전환 가능 (ChatGPT 스타일 사이드바)
- **대화 제목 자동 생성**: 각 대화의 첫 메시지를 기준으로 제목 자동 부여, 이후 수동 수정 가능
- **접이식 사이드바 UI**: 랜딩 화면은 새 대화 시작에 집중, 필요할 때만 사이드바를 열어 이전 대화 탐색

## 기술 스택

### Backend

- **FastAPI** — REST API 서버
- **LangGraph** — 에이전트 워크플로우 및 상태(checkpointer) 관리
- **LangChain** — RAG 파이프라인 구성 (문서 로드, 텍스트 분할, 프롬프트 체인)
- **OpenAI GPT-4o-mini** — 답변 생성 LLM
- **FAISS + BAAI/bge-m3** — 벡터 검색 기반 문서 검색
- **AsyncSqliteSaver** — 대화 상태(메시지 이력) 영속화
- **aiosqlite** — 대화 메타데이터(제목, 생성/수정일) 별도 관리

### Frontend

- **React + TypeScript** — 컴포넌트 기반 UI
- **Vite** — 빌드 도구
- **Tailwind CSS** — 스타일링

## 프로젝트 구조

```
chatbot-project/
├── backend/
│   ├── main.py                    # FastAPI 앱 진입점, lifespan, /chat 엔드포인트
│   ├── graph/
│   │   └── agent.py               # LangGraph 그래프 정의 (RAG 노드, 벡터스토어 초기화)
│   ├── routers/
│   │   └── conversations.py       # 대화 목록/생성/제목수정 API
│   ├── db/
│   │   └── conversations.py       # 대화 메타데이터 SQLite 접근 계층
│   ├── utils/
│   │   └── text_splitter.py       # Q&A 단락 기준 최적 chunk_size 계산
│   ├── data/
│   │   └── manual.txt             # RAG 검색 대상 매뉴얼 문서
│   └── requirements.txt
│
└── frontend/
    ├── src/
    │   ├── components/
    │   │   ├── Sidebar.tsx         # 접이식 대화 목록 패널
    │   │   ├── ChatHeader.tsx      # 사이드바 토글 + 현재 대화 제목
    │   │   ├── ChatWindow.tsx      # 메시지 목록 + 빈 상태(랜딩) 화면
    │   │   ├── MessageBubble.tsx
    │   │   ├── ChatInput.tsx
    │   │   ├── ErrorBanner.tsx
    │   │   └── Button.tsx
    │   ├── hooks/
    │   │   ├── useChat.ts          # 특정 대화의 메시지 송수신
    │   │   └── useConversations.ts # 대화 목록 조회/생성/제목수정
    │   ├── types/
    │   │   ├── chat.ts
    │   │   ├── api.ts
    │   │   └── conversation.ts
    │   ├── utils/
    │   │   ├── conversation.ts     # 백엔드 응답(snake_case) → 프론트 타입(camelCase) 변환
    │   │   └── errorMessage.ts
    │   ├── constants/
    │   │   └── index.ts
    │   └── App.tsx
    └── package.json
```

## 아키텍처 개요

### 대화 데이터가 두 곳에 나뉘어 저장됩니다

| 저장소                                                       | 담당 내용                                        |
| ------------------------------------------------------------ | ------------------------------------------------ |
| `history_single_agent.sqlite` (LangGraph `AsyncSqliteSaver`) | 각 `thread_id`의 실제 메시지 이력 (체크포인트)   |
| `conversations.sqlite` (자체 관리)                           | `thread_id`별 제목, 생성일, 수정일 등 메타데이터 |

LangGraph의 checkpointer는 메시지 이력은 저장하지만 "이 대화의 제목이 뭔지" 같은 메타데이터는 다루지 않기 때문에, 별도 SQLite DB를 두어 확장했습니다.

### 주요 API

| 메서드  | 경로                                  | 설명                              |
| ------- | ------------------------------------- | --------------------------------- |
| `POST`  | `/conversations`                      | 새 대화 생성 (thread_id 발급)     |
| `GET`   | `/conversations`                      | 전체 대화 목록 조회 (최근 수정순) |
| `PATCH` | `/conversations/{thread_id}`          | 대화 제목 수정                    |
| `GET`   | `/conversations/{thread_id}/messages` | 특정 대화의 과거 메시지 조회      |
| `POST`  | `/chat`                               | 메시지 전송 및 답변 생성          |

### 프론트엔드 상태 흐름

- `App.tsx`가 `selectedThreadId`(현재 보고 있는 대화)와 `isSidebarOpen`(사이드바 열림 여부)을 최상위에서 관리합니다.
- `useConversations`(목록 관리)와 `useChat`(메시지 송수신)은 서로 독립적인 훅이며, `App.tsx`가 둘을 연결합니다.
- 랜딩 화면(`selectedThreadId === null`)에서 첫 메시지를 보내면, 그 시점에 `POST /conversations`로 대화를 생성한 뒤 `/chat`을 호출합니다.

## 실행 방법

### Backend

```bash
cd backend

conda create -n chatbot-agent python=3.11 -y
conda activate chatbot-agent
pip install -r requirements.txt

# .env 파일 생성 후 OPENAI_API_KEY 설정
cp .env.example .env

uvicorn main:app --reload
```

서버는 `http://localhost:8000`에서 실행됩니다. `/health`로 정상 기동 여부를 확인할 수 있습니다.

### Frontend

```bash
cd frontend

npm install

# .env 파일 생성
cp .env.example .env

npm run dev
```

`http://localhost:5173`에서 확인할 수 있습니다.

## 개발 중 다룬 주요 이슈 (회고)

- **FastAPI `lifespan`을 통한 리소스 관리**: `AsyncSqliteSaver` 커넥션과 LangGraph 컴파일을 요청마다 반복하지 않고, 서버 시작 시 한 번만 초기화하도록 설계
- **discriminated union으로 API 응답 타입 안전성 확보**: `/chat` 응답이 `{ response }` 또는 `{ error }` 중 하나만 오도록 타입으로 강제
- **snake_case ↔ camelCase 변환 계층 분리**: 백엔드(Python 관례)와 프론트엔드(TypeScript 관례) 사이의 네이밍 차이를 변환 유틸 함수로 명확히 분리
- **접이식 사이드바 구현**: 모달이 아닌, `width` 값만 토글하는 방식으로 채팅 화면을 막지 않으면서 대화 목록에 접근 가능하도록 구성
