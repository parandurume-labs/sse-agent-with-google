# 🤝 사회연대경제(SSE) AI 에이전트 서비스

> **Google Workspace + GCP + Gemini API 기반의 사회연대경제 조직을 위한 자율 행정 업무 에이전트 시스템**

본 프로젝트는 자원과 인력이 부족한 사회연대경제(SSE) 조직들이 행정 업무의 부담을 덜고, 조직 내에 흩어진 지식을 자산화하여 지속 가능한 성장 기반을 마련할 수 있도록 돕는 에이전트 기반 솔루션입니다.

---

## 🖥️ 실시간 제어 대시보드 (Glassmorphic Web Dashboard)

스마트 행정 제어를 위해 **FastAPI & HTML5 SPA** 기반의 대시보드를 탑재하였습니다. 개발자 및 운영진은 실시간 스캔을 구동 및 중지하고, 실시간 로그 스트리밍과 매칭 점수를 직접 확인할 수 있습니다.

![Dashboard Mockup](https://images.unsplash.com/photo-1551288049-bebda4e38f71?auto=format&fit=crop&w=1200&q=80)

---

## 🛠️ 핵심 기능 (Core Features)

### 1. 실시간 지원사업 자동 스캐너 & 필터 (Module A)
* **실시간 웹 스크래핑 (BeautifulSoup4)**: 기업마당(Bizinfo) 공고 리스트 테이블을 실시간 크롤링하여 공고명, 공고 ID(`pblancId`), 상세 링크, **신청 기한(마감일)**, 소관 부처 등을 완벽하게 추출합니다.
* **AI 적합도 평가 (Gemini 1.5 Flash)**: 수집된 정보를 바탕으로 조직의 타겟팅 룰(`Agent_Grant_Searcher.md`)에 근거하여 AI 적합도 점수 ($S \in [1, 10]$) 및 평가 사유를 실시간 산출합니다.
* **구글 캘린더 자동 동기화**: 매칭 점수가 8점 이상($S \ge 8$)인 공고는 구글 캘린더(Google Calendar)에 마감일 기준 종일 일정으로 자동 동기화되며, 3일 전 자동 이메일 리마인더가 세팅됩니다.
* **구글 스프레드시트 연동 및 제어 (Spreadsheet DB)**: Google Apps Script(`apps_script.js`) 기반의 시트 메뉴 제어 패널을 통해 대시보드 스캔 명령을 내리고, 결과를 `T_Grant_Master` 데이터베이스 시트에 즉시 동기화(Deduplicated Sync)합니다.

### 2. Google Drive 기반 지식 RAG 위키 (Module B)
* **지식 베이스**: Obsidian 스타일의 마크다운(`.md`) 파일 기반 사내 지식 베이스 구축
* **긴 컨텍스트 RAG**: Gemini의 긴 컨텍스트 창(Context Window)을 활용하여 사내 규정, 정관, 총회 의사록 기반의 정확한 RAG 챗봇 구동

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
├── SSE_Agent_Workspace/                # Google Drive 동기화 작업 공간
│   ├── 01_Agent_Profiles/              # 에이전트별 동작 규칙 (마크다운)
│   │   ├── Agent_Grant_Searcher.md     # 지원사업 타겟팅 필터링 룰
│   │   └── Agent_Reporter.md           # 보고서 작성 톤앤매너 및 포스팅 규칙
│   ├── 02_Knowledge_Wiki/              # RAG 지식 베이스용 마크다운 파일 보관함
│   ├── 03_Task_Queue/                  # 에이전트가 실행할 작업 요청함
│   ├── 04_AppSheet_Media/              # 현장 미디어 저장소
│   └── 05_Output_Drafts/               # 에이전트가 생성한 출력물 초안 보관함
└── functions/                          # 백엔드 엔진 & 제어 대시보드 소스코드
    ├── dashboard_app.py                # FastAPI 대시보드 웹 어플리케이션
    ├── static/                         # 대시보드 정적 웹 리소스 (HTML/CSS/JS SPA)
    ├── apps_script.js                  # Google Sheets 연동 메뉴 Apps Script 소스
    ├── credentials.json                # Google API 사용자 인증 클라이언트 보안 키
    └── module_a_scanner/               # 지원사업 스캔 코어 패키지
        ├── main.py                     # 스캐너 실행 오케스트레이터 및 GCP 진입점
        ├── scraper.py                  # 비즈인포 실시간 BeautifulSoup 웹 크롤러
        ├── evaluator.py                # Gemini 1.5 기반 공고 적합도 평가 엔진
        └── calendar_sync.py            # 구글 캘린더 자동 등록 모듈
```

---

## 🚀 로컬 대시보드 실행 가이드 (Quick Start)

본 프로젝트는 가상 개발 환경(venv)과 FastAPI를 사용해 간편하게 즉시 구동할 수 있습니다.

### 1. 가상환경 세팅 및 의존성 설치
```powershell
# functions 폴더로 이동하여 가상환경 생성 및 실행
cd functions
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 필요한 라이브러리 및 크롤링 의존성 패키지 설치
pip install -r requirements.txt
```

### 2. API 인증 정보 구성
1. `functions/.env` 파일을 생성하고 `GEMINI_API_KEY`를 설정합니다.
   ```env
   GEMINI_API_KEY="your_actual_gemini_api_key"
   ```
2. Google Cloud Console에서 발급받은 `credentials.json` 파일을 `functions/` 디렉토리에 배치합니다.

### 3. 로컬 웹 제어 콘솔 실행
대시보드를 로컬 포트 `8000`에서 실행합니다:
```powershell
uvicorn dashboard_app:app --host 127.0.0.1 --port 8000 --reload
```
브라우저에서 `http://127.0.0.1:8000`으로 접속하여 **우아한 글래스모피즘 어드민 패널**과 **즉시실행** 기능을 경험해 보세요!

---

## 🛡️ 기술 스택 (Tech Stack)

| 구분 | 기술 스택 |
|---|---|
| **Language** | Python 3.11+, JavaScript (ES6) |
| **Backend** | FastAPI (Uvicorn), Google Apps Script |
| **Scraping** | BeautifulSoup4, Requests |
| **AI Engine** | Google AI Studio (Gemini 1.5 Pro / Flash) |
| **Database/Storage** | Google Drive, Google Sheets, Google Calendar |
| **Frontend UI** | HTML5 / Vanilla CSS Glassmorphism 어드민 패널 |
| **Development Orchestrator** | Antigravity (gstack) |
