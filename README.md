# RAG 챗봇 프로젝트

온라인 교육 플랫폼의 고객센터에서는 사용자가 이전 대화를 이어서 질문하거나, 여러 상담을 동시에 진행하는 상황이 자주 발생합니다.

이 프로젝트는 이러한 실제 서비스 환경을 가정하여 **대화 맥락을 이해하는 RAG 챗봇**과 **ChatGPT와 같은 멀티 세션 관리 기능**을 구현한 풀스택 프로젝트입니다.

단순히 LLM을 연결하는 데 그치지 않고, 사용자 경험과 운영 환경까지 고려하여 서비스를 설계했습니다.

**🔗 배포 링크: https://chatbot-project-gamma-nine.vercel.app**
**🔗 GitHub: https://github.com/LiebeChaejun/chatbot-project**

> 백엔드는 Render 무료 인스턴스에서 실행되고 있어, 15분 이상 요청이 없으면 슬립 상태가 됩니다. 첫 접속 시 응답까지 30~50초 정도 걸릴 수 있으니 잠시 기다려주세요.

## 🔍 사용 시나리오 (바로 체험해보기)

### 시나리오 1. 첫 대화 시작 및 제목 자동 생성

1. 접속하면 사이드바가 닫힌 랜딩 화면이 보입니다.
2. 입력창에 `"수강 신청한 강의를 환불하고 싶어요. 환불 정책이 어떻게 되나요?"`를 입력하고 전송합니다.
3. 답변이 도착한 후, 헤더의 제목이 입력한 질문 앞부분으로 자동 설정된 것을 확인합니다.

### 시나리오 2. 대화 맥락 유지 및 질문 재구성 확인

1. 시나리오 1에 이어서, `"그거 전액 다 받으려면 조건이 어떻게 되나요?"`처럼 이전 질문을 지칭어("그거")로 참조하는 질문을 보냅니다.
2. "그거"가 환불을 가리킨다는 걸 챗봇이 이해하고, 환불 조건에 대한 답변을 이어가는지 확인합니다. (질문 재구성 에이전트가 모호한 질문을 독립적인 검색 쿼리로 바꿔주는 부분입니다.)

### 시나리오 3. 일상 대화와 서비스 질문의 자연스러운 구분

1. 새 대화를 시작해 `"안녕", "밥 먹었어?", "고마워"`처럼 가벼운 인사와 잡담을 순서대로 건네봅니다.
2. 매뉴얼 검색 없이도 자연스럽게 응대하면서, 가끔 강의나 학습 관련 대화로 부드럽게 화제를 이어가는지 확인합니다.
3. 챗봇이 유도한 대로 `"어떤 강의가 있어?"`라고 실제로 물어봅니다.
4. 이번엔 매뉴얼에 등록된 실제 강의 목록(파이썬, 웹 개발, 데이터 분석, LLM 활용 등)을 근거로 답하는지 확인합니다.

### 시나리오 4. 여러 대화 관리 및 전환

1. 사이드바를 열고 "+ 새 대화"로 대화를 하나 더 만듭니다.
2. `"모바일 앱에서 오프라인으로 강의를 볼 수 있나요?"`처럼 다른 주제로 질문합니다.
3. 사이드바에서 이전 대화(환불 관련)로 다시 돌아가, 대화 내용이 그대로 유지되어 있는지 확인합니다.

### 시나리오 5. 대화 제목 수동 편집

1. 아무 대화나 선택한 상태에서, 헤더의 편집 아이콘(✏️)을 클릭합니다.
2. 제목을 원하는 텍스트로 수정하고 Enter를 눌러 저장합니다.
3. 사이드바 목록에도 변경된 제목이 즉시 반영되는지 확인합니다.

### 시나리오 6. 매뉴얼에 없는 질문 처리 (할루시네이션 방지 확인)

1. `"배송비는 얼마인가요?"`처럼 매뉴얼(온라인 강의 서비스)에는 없지만 서비스 관련으로 보이는 질문을 보냅니다.
2. 검색 결과가 없을 때 임의로 답을 지어내지 않고, "아는 바가 없습니다"류의 정직한 답변을 하는지 확인합니다.

### 시나리오 7. 사용자 간 대화 격리 확인

1. 일반 브라우저 창에서 대화를 몇 개 만든 상태를 유지합니다.
2. 시크릿/프라이빗 모드로 같은 URL에 접속합니다.
3. 사이드바가 완전히 빈 상태(대화 없음)로 시작되는지 확인해, 로그인 없이도 서로 다른 사용자의 대화가 격리되어 있음을 확인합니다.

---

## 주요 기능

- **멀티 에이전트 RAG 파이프라인**: 질문의 의도(매뉴얼 검색 필요 여부)를 먼저 분류하고, 이전 대화 맥락에 의존하는 모호한 질문("그거 조건이 뭐야?")은 독립적인 검색 쿼리로 재구성한 뒤 답변
- **자연스러운 일상 대화 처리**: 인사나 잡담은 매뉴얼 검색 없이 응대하되, 매번 기계적으로 반복하지 않고 자연스러운 흐름으로 학습 관련 대화를 유도
- **할루시네이션 방지**: 매뉴얼에 없는 서비스 관련 질문에는 추측 답변 대신 정직하게 모른다고 응답
- **대화 맥락 유지**: LangGraph checkpointer로 같은 대화(thread) 내에서 이전 질문/답변을 기억
- **멀티 세션 대화 관리**: 여러 개의 대화를 독립적으로 생성·조회·전환 가능 (ChatGPT 스타일 사이드바)
- **대화 제목 자동 생성 및 수동 편집**: 첫 메시지로 제목을 자동 부여하고, 헤더에서 인라인으로 직접 수정 가능
- **사용자별 대화 격리**: 로그인 없이도 브라우저별 식별자(owner_id)로 대화가 서로 섞이지 않도록 격리 — 배포 후 여러 사람이 동시에 사용 가능
- **접이식 사이드바 UI**: 랜딩 화면은 새 대화 시작에 집중, 필요할 때만 사이드바를 열어 이전 대화 탐색
- **컨테이너 기반 배포**: Docker로 패키징하여 로컬-배포 환경 간 의존성 불일치 문제 방지

## 기술 스택

### Backend

- **FastAPI** — REST API 서버
- **LangGraph** — 멀티 에이전트 워크플로우 및 상태(checkpointer) 관리
- **LangChain** — RAG 파이프라인 구성 (문서 로드, 텍스트 분할, 프롬프트 체인)
- **OpenAI GPT-4o-mini** — 의도 분류(temperature=0), 질문 재구성(temperature=0), 답변 생성(temperature=0.7)
- **OpenAI text-embedding-3-small** — 문서 임베딩 (API 기반, 로컬 모델 미사용)
- **FAISS** — 벡터 검색 기반 문서 검색
- **AsyncSqliteSaver** — 대화 상태(메시지 이력) 영속화
- **aiosqlite** — 대화 메타데이터(제목, 소유자, 생성/수정일) 별도 관리

### Frontend

- **React + TypeScript** — 컴포넌트 기반 UI
- **Vite** — 빌드 도구
- **Tailwind CSS** — 스타일링

### Infra / Deployment

- **Docker** — 백엔드 컨테이너화
- **Render** — 백엔드 배포 (Docker 기반 Web Service)
- **Vercel** — 프론트엔드 배포

## 프로젝트 구조

```
chatbot-project/
├── backend/
│   ├── main.py                    # FastAPI 앱 진입점, lifespan, /chat 엔드포인트
│   ├── dependencies.py            # 앱 전역 상태(app_state) 및 의존성 주입
│   ├── Dockerfile                 # 백엔드 컨테이너 이미지 정의
│   ├── graph/
│   │   └── agent.py               # LangGraph 멀티 에이전트 그래프 정의
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
    │   │   ├── ChatHeader.tsx      # 사이드바 토글 + 제목 인라인 편집
    │   │   ├── ChatWindow.tsx      # 메시지 목록 + 빈 상태(랜딩) 화면
    │   │   ├── MessageBubble.tsx
    │   │   ├── ChatInput.tsx
    │   │   ├── ErrorBanner.tsx     # 닫기 가능한 에러 배너
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
    │   │   ├── owner.ts            # 브라우저별 owner_id 생성/조회
    │   │   └── errorMessage.ts
    │   ├── constants/
    │   │   └── index.ts
    │   └── App.tsx
    └── package.json
```

## 아키텍처 개요

### 멀티 에이전트 그래프 구조

```
                 ┌─────────────┐
question ──────▶│ route (의도 │──(일상 대화)──▶ general_answer ──▶ END
                 │   분류)      │
                 └─────────────┘
                        │
                     (매뉴얼 관련)
                        ▼
                  rephrase (질문 재구성) ──▶ retriever (검색) ──▶ answer (답변 생성) ──▶ END
```

- **route**: 질문이 매뉴얼 검색이 필요한지(`manual`), 일상 대화인지(`general`) 분류. Few-shot 예시를 활용해 "밥 먹었어?" 같은 일상 대화가 서비스 질문으로 오분류되지 않도록 조정
- **rephrase**: 이전 대화 맥락에 의존하는 모호한 질문을 독립적인 검색 쿼리로 재구성
- **retriever**: 재구성된 쿼리로 FAISS 벡터 검색 (상위 3개 문서, OpenAI 임베딩 기반)
- **answer**: 검색된 컨텍스트를 바탕으로 매뉴얼 기반 답변 생성
- **general_answer**: 매뉴얼 검색 없이 대화 맥락으로 자연스럽게 응대하되, 서비스 관련 질문에는 추측 답변을 하지 않고 학습 관련 대화로 자연스럽게 유도

### 대화 데이터가 두 곳에 나뉘어 저장됩니다

| 저장소                                                       | 담당 내용                                                          |
| ------------------------------------------------------------ | ------------------------------------------------------------------ |
| `history_single_agent.sqlite` (LangGraph `AsyncSqliteSaver`) | 각 `thread_id`의 실제 메시지 이력 (체크포인트)                     |
| `conversations.sqlite` (자체 관리)                           | `thread_id`별 제목, 소유자(owner_id), 생성일, 수정일 등 메타데이터 |

### 사용자별 대화 격리 (로그인 없이)

로그인 시스템 없이도, 브라우저마다 `localStorage`에 고유한 `owner_id`(UUID)를 발급해 모든 API 요청에 `X-Owner-Id` 헤더로 실어 보냅니다. 백엔드는 이 값으로 대화 목록을 필터링하고, 다른 사용자의 `thread_id`로 접근을 시도하면 404로 차단합니다.

### 주요 API

| 메서드  | 경로                                  | 설명                                              |
| ------- | ------------------------------------- | ------------------------------------------------- |
| `POST`  | `/conversations`                      | 새 대화 생성 (thread_id 발급, 요청자 소유로 등록) |
| `GET`   | `/conversations`                      | 요청자 소유의 대화 목록 조회 (최근 수정순)        |
| `PATCH` | `/conversations/{thread_id}`          | 대화 제목 수정 (소유자만 가능)                    |
| `GET`   | `/conversations/{thread_id}/messages` | 특정 대화의 과거 메시지 조회 (소유자만 가능)      |
| `POST`  | `/chat`                               | 메시지 전송 및 답변 생성 (소유자만 가능)          |

모든 대화 관련 요청은 `X-Owner-Id` 헤더가 필수입니다.

## 실행 방법

### Backend (Docker)

```bash
cd backend
cp .env.example .env   # OPENAI_API_KEY 설정

docker build -t chatbot-backend .
docker run -p 8000:8000 --env-file .env chatbot-backend
```

서버는 `http://localhost:8000`에서 실행됩니다. `/health`로 정상 기동 여부를 확인할 수 있습니다.

### Backend (Docker 없이, 로컬 Python 환경)

```bash
cd backend

conda create -n chatbot-agent python=3.11 -y
conda activate chatbot-agent
pip install -r requirements.txt

cp .env.example .env
uvicorn main:app --reload
```

### Frontend

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

`http://localhost:5173`에서 확인할 수 있습니다.

## 배포

- **Frontend**: Vercel (Root Directory: `frontend`, 환경변수 `VITE_API_URL`로 백엔드 주소 지정)
- **Backend**: Render (Docker 기반 Web Service, Root Directory: `backend`)

배포 시 `main.py`의 CORS `allow_origins`에 프론트엔드 배포 도메인을 등록해야 합니다.

## 개발 중 다룬 주요 이슈 (회고)

- **FastAPI `lifespan`을 통한 리소스 관리**: `AsyncSqliteSaver` 커넥션과 LangGraph 컴파일을 요청마다 반복하지 않고, 서버 시작 시 한 번만 초기화하도록 설계
- **의존성 주입으로 순환참조 해결**: 라우터와 `main.py`가 서로를 import하던 구조를, `dependencies.py`를 통한 `Depends()` 패턴으로 정리
- **discriminated union으로 API 응답 타입 안전성 확보**: `/chat` 응답이 `{ response }` 또는 `{ error }` 중 하나만 오도록 타입으로 강제
- **snake_case ↔ camelCase 변환 계층 분리**: 백엔드(Python 관례)와 프론트엔드(TypeScript 관례) 사이의 네이밍 차이를 변환 유틸 함수로 명확히 분리
- **접이식 사이드바 구현**: 모달이 아닌, `width` 값만 토글하는 방식으로 채팅 화면을 막지 않으면서 대화 목록에 접근 가능하도록 구성
- **로그인 없는 사용자 격리**: 정식 인증 시스템 대신, 브라우저별 익명 식별자(owner_id)로 배포 환경에서의 데이터 격리 문제를 실용적으로 해결
- **의도 분류 기반 라우팅과 temperature 분리**: 분류·재구성처럼 일관성이 중요한 작업(temperature=0)과, 답변 생성처럼 자연스러움이 중요한 작업(temperature=0.7)에 서로 다른 LLM 인스턴스를 사용해, 같은 질문이 매번 다르게 분류되는 문제를 해결
- **Few-shot 예시를 통한 프롬프트 안정화**: 규칙을 말로 설명하는 것만으로는 "밥 먹었어?" 같은 일상 대화가 서비스 질문으로 오분류되는 문제가 반복되어, 구체적인 입출력 예시를 프롬프트에 포함시켜 분류 정확도를 개선
- **무료 티어 메모리 제약과 임베딩 전략 전환**: 로컬 HuggingFace 임베딩 모델(BAAI/bge-m3)이 Render 무료 인스턴스(512MB)의 메모리 한도를 초과해 배포가 반복적으로 실패하는 문제를 겪었습니다. Docker 컨테이너 로그와 메모리 지표를 근거로 원인을 OOM으로 특정한 뒤, 로컬 모델 대신 OpenAI 임베딩 API로 전환해 문제를 해결했습니다. 이 과정에서 Docker 이미지 용량과 서버 시작 속도도 함께 개선되었습니다.
- **Docker 도입으로 환경 불일치 문제 예방**: 로컬(conda)과 배포 환경 간 의존성 차이로 인한 실패를 사전에 방지하기 위해 처음부터 Dockerfile을 도입했습니다. 실제로 로컬에서는 우연히 설치되어 있던 `sentence-transformers` 패키지가 `requirements.txt`에 누락되어 있던 것을 컨테이너 빌드 과정에서 발견해 조기에 수정할 수 있었습니다.
