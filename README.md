# 챗봇 프로젝트

LangGraph 기반 RAG 챗봇 + FastAPI 백엔드 + React 프론트엔드로 구성된 대화형 챗봇입니다.

## 기술 스택

**Backend**

- FastAPI, LangGraph, LangChain
- OpenAI GPT-4o-mini
- FAISS + BAAI/bge-m3 임베딩
- AsyncSqliteSaver (대화 이력 checkpointer)

**Frontend**

- React, TypeScript, Vite
- Tailwind CSS

## 주요 기능

- Thread ID 기반 대화 세션 관리 (브라우저별 대화 맥락 유지)
- RAG 기반 질의응답 (사내 매뉴얼 문서 검색 후 답변 생성)
- SQLite 기반 대화 기록 영속성

## 실행 방법

### Backend

\`\`\`bash
cd backend
conda create -n chatbot-agent python=3.11 -y
conda activate chatbot-agent
pip install -r requirements.txt

# .env 파일 생성 후 OPENAI_API_KEY 설정

cp .env.example .env

uvicorn main:app --reload
\`\`\`

### Frontend

\`\`\`bash
cd frontend
npm install

# .env 파일 생성

cp .env.example .env

npm run dev
\`\`\`

## 프로젝트 구조

\`\`\`
chatbot-project/
├── backend/
│ ├── main.py # FastAPI 앱 진입점
│ ├── graph/agent.py # LangGraph 그래프 정의
│ ├── utils/ # 텍스트 분할 등 유틸
│ └── data/manual.txt # RAG 검색 대상 문서
└── frontend/
├── src/
│ ├── components/
│ ├── hooks/
│ ├── types/
│ └── utils/
└── ...
\`\`\`
