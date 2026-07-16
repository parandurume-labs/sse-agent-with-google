# 🤝 사회연대경제(SSE) AI 에이전트 서비스

> **Google Workspace + GCP + Gemini API 기반의 사회연대경제 조직을 위한 자율 행정 업무 에이전트 시스템**

본 프로젝트는 자원과 인력이 부족한 사회연대경제(SSE) 조직들이 행정 업무의 부담을 덜고, 조직 내에 흩어진 지식을 자산화하여 지속 가능한 성장 기반을 마련할 수 있도록 돕는 에이전트 기반 솔루션입니다.

---

## 🛠️ 핵심 기능 (Core Features)

### 1. 지원사업 자동 스캐너 (Module A)
* **자동 수집**: 매일 지정된 포털의 지원사업 공고 자동 스크래핑
* **AI 적합도 평가**: 에이전트 룰(`Agent_Grant_Searcher.md`) 기준 적합도 점수 ($S \in [1, 10]$) 평가
* **알림 및 연동**: $S \ge 8$ 점 이상인 공고 Google Calendar 자동 등록 및 마감 3일 전 이메일/Google Chat 리마인더 발송

### 2. Google Drive 기반 지식 위키 (Module B)
* **지식 베이스**: Obsidian 스타일의 마크다운(`.md`) 파일 기반 사내 지식 베이스 구축
* **긴 컨텍스트 RAG**: Gemini의 긴 컨텍스트 창(Context Window)을 활용하여 사내 규정, 총회 의사록 기반 RAG 챗봇 구동

### 3. 현장 사진 기반 자동 보고서 및 사이트 포스팅 (Module C)
* **미디어 전송**: AppSheet 모바일 앱으로 촬영한 현장 사진과 메모 전송
* **멀티모달 분석**: Gemini 1.5 Pro 멀티모달 분석을 통해 톤앤매너(`Agent_Reporter.md`)가 반영된 완성도 높은 블로그 초안 작성
* **자동 퍼블리싱**: 승인 시 아임웹, WordPress 등 웹사이트 API 연동 자동 퍼블리싱

---

## 📁 디렉토리 구조 (Directory Structure)

본 프로젝트는 Google Drive 및 로컬 에이전트 규칙 관리를 위해 아래와 같은 폴더 구조를 준수합니다.

```
.
├── README.md                           # 본 프로젝트 안내 파일
├── 00_architecture_spec.md             # Antigravity용 기술 명세 및 개발 로드맵
├── .agent/                             # Antigravity 에이전트 설정 및 실행 규칙
│   └── rules/
│       ├── system_prompt.md            # 기본 에이전트 페르소나 설정
│       └── developer_rules.md          # 코딩 표준 및 디버깅 가이드라인
└── SSE_Agent_Workspace/                # Google Drive 동기화 작업 공간
    ├── 01_Agent_Profiles/              # 에이전트별 동작 규칙 (마크다운)
    │   ├── Agent_Grant_Searcher.md     # 지원사업 타겟팅 필터링 룰
    │   └── Agent_Reporter.md           # 보고서 작성 톤앤매너 및 포스팅 규칙
    ├── 02_Knowledge_Wiki/              # RAG 지식 베이스용 마크다운 파일 보관함
    ├── 03_Task_Queue/                  # 에이전트가 실행할 작업 요청함
    ├── 04_AppSheet_Media/              # 현장 미디어 저장소
    └── 05_Output_Drafts/               # 에이전트가 생성한 출력물 초안 보관함
```

---

## 🚀 Antigravity(gstack)를 통한 빠른 시작 가이드

본 프로젝트는 Antigravity(gstack) 환경에 최적화되어 있습니다. 아래 단계를 통해 가상 개발자 팀을 활성화하고 구현을 진행하세요.

### 1. 환경 설정 및 초기화

```bash
# 1. gstack-antigravity 도구 확인 (또는 최신 공식 gstack 연동 사용)
# 2. 로컬 디렉토리에 본 저장소 클론 및 README.md 배치
# 3. Google AI Studio에서 GEMINI_API_KEY 발급 후 로컬 환경 변수 등록
export GEMINI_API_KEY="your_api_key_here"
```

### 2. 단계별 개발 스프린트 명령

Antigravity CLI 채팅창에서 아래와 같이 입력하여 순차적으로 에이전트 가상 엔지니어링을 구동합니다.

#### 🏃 스프린트 2 (지원사업 스캐너) 시작하기
> "README.md와 00_architecture_spec.md의 Module A 사양을 확인하고, 매일 아침 작동할 지원사업 스캐너 및 구글 캘린더 연동 파이썬 백엔드 코드를 작성해 줘."

#### 🏃 스프린트 3 (RAG 지식 위키) 시작하기
> "README.md와 00_architecture_spec.md의 Module B 사양을 참조하여, 구글 드라이브 내의 02_Knowledge_Wiki 폴더 내 md 파일들을 컨텍스트로 불러와 답변하는 API 엔드포인트를 구현해 줘."

#### 🏃 스프린트 4 (AppSheet 연동 멀티모달) 시작하기
> "README.md와 00_architecture_spec.md의 Module C 사양을 읽고, AppSheet 웹훅 이미지와 메모 텍스트를 처리해 Gemini 1.5 Pro로 블로그 초안을 생성하는 API 및 웹사이트 퍼블리싱 기능을 연동해 줘."

---

## 🛡️ 기술 스택 (Tech Stack)

| 구분 | 기술 스택 |
|---|---|
| **Language** | Python 3.11+ |
| **Backend** | Google Cloud Functions, Google Apps Script |
| **AI Engine** | Google AI Studio (Gemini 1.5 Pro / Flash) |
| **Database/Storage** | Google Drive, Google Sheets, Google Calendar |
| **Frontend / Entrypoint** | AppSheet (No-Code UI) |
| **Development Orchestrator** | Antigravity (gstack) |
