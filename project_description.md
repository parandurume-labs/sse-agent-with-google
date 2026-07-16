# 프로젝트 소개 (Project Description)

## 1. 기본 정보 (Overview)
- **프로젝트명**: 사회연대경제(SSE) 조직을 위한 자율 행정 AI 에이전트 (SSE AI Agent Service)
- **참가 트랙**: Track 3. Google AI for Social Good

## 2. 해결하고자 하는 문제 (Problem Statement)
사회연대경제(SSE) 조직, 비영리 단체, 소셜 벤처 등은 세상을 긍정적으로 바꾸는 중요한 역할을 하지만, 항상 **인력과 자원의 부족**에 시달립니다. 활동가들은 본연의 소셜 임팩트 창출 업무보다 각종 지원사업 탐색, 행사 결과 보고서 작성, 파편화된 사내 규정 및 회의록 확인 등 **반복적인 행정 업무**에 많은 시간을 뺏기고 있습니다.

## 3. 솔루션 소개 (Solution)
**"Google Workspace + GCP + Gemini 기반의 자율 행정 업무 에이전트 시스템"**

활동가들의 기존 업무 환경(Google Workspace)을 벗어나지 않고, 노코드 앱(AppSheet)과 사내 드라이브(Google Drive)에 에이전트를 결합하여 행정 부담을 최소화하고 지식을 자산화합니다. 

### 핵심 기능 (Core Features)
1. **지원사업 자동 스캐너 (Grant Scanner)**
   - **기능**: 공공 포털의 지원사업 공고를 자동 수집하고, 사내 에이전트 룰에 맞춰 적합도를 평가합니다.
   - **효과**: 적합도가 높은 공고는 자동으로 Google Calendar에 일정을 등록하고 마감 3일 전 Google Chat/이메일 리마인더를 발송하여 기회를 놓치지 않게 돕습니다.
2. **사내 규정 및 지식 RAG 챗봇 (Knowledge Wiki)**
   - **기능**: Google Drive 내의 마크다운(`.md`) 기반 사내 문서를 Gemini의 긴 컨텍스트(Context Window)를 활용해 분석합니다.
   - **효과**: 활동가가 "정기총회 서명 양식 어딨어?"라고 물으면 즉시 문서를 참조해 신뢰할 수 있는 출처와 함께 답변을 제공합니다.
3. **현장 멀티모달 자동 보고서 (Field Report Publisher)**
   - **기능**: 현장 활동가가 AppSheet로 사진과 간단한 메모만 올리면, Gemini 1.5 Pro의 멀티모달 분석을 통해 공식 블로그/보고서 톤앤매너에 맞춘 완성형 초안을 생성합니다.
   - **효과**: 행사 후 보고서 작성 시간을 획기적으로 단축하고, 승인 시 웹사이트에 자동 퍼블리싱까지 지원합니다.

## 4. 기대 효과 및 심사 기준 부합성 (Impact & Creativity)
- 🌍 **Impact (사회적 영향력)**: 영세한 사회적 경제 조직들이 행정 업무 대신 본연의 소셜 미션(사회적 문제 해결)에 온전히 집중할 수 있는 환경을 제공합니다. 
- ✨ **Creativity (창의성)**: 별도의 무거운 웹/앱 플랫폼을 새로 구축하는 대신, 조직원들에게 이미 익숙한 Google Workspace(Drive, Chat, Calendar)와 AppSheet를 그대로 활용하는 'Agentic Workflow' 접근을 통해 실질적인 도입 장벽을 낮췄습니다.
- 🛠️ **Technical (기술적 완성도)**: GCP(Cloud Functions, Scheduler) 서버리스 아키텍처 위에서 Gemini 1.5 Pro의 멀티모달 추론과 긴 컨텍스트 분석 능력을 유기적으로 파이프라인화하여 완전 자동화를 구현했습니다.

## 5. 기술 스택 (Tech Stack)
- **AI Engine**: Google AI Studio (Gemini 1.5 Pro / Flash)
- **Backend**: Google Cloud Functions, Google Cloud Scheduler
- **Workspace/DB**: Google Drive, Google Sheets, Google Calendar, Google Chat
- **Frontend**: AppSheet (No-Code Mobile App)
- **Orchestration**: Google Antigravity
