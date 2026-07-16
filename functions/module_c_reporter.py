"""
Module C: Event Reporter Agent using Google Gemini Multimodal API
"""
import os
import datetime
import logging
from PIL import Image
import google.generativeai as genai
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
else:
    logger.warning("GEMINI_API_KEY not found in environment. Report generation will be simulated.")

class EventReporter:
    def __init__(self, workspace_path=None, rules_path=None):
        if workspace_path:
            self.workspace_path = workspace_path
        else:
            self.workspace_path = os.getenv(
                "WORKSPACE_PATH", 
                os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "SSE_Agent_Workspace"))
            )
        
        if rules_path:
            self.rules_path = rules_path
        else:
            self.rules_path = os.path.join(self.workspace_path, "01_Agent_Profiles", "Agent_Reporter.md")
            
        self.rules_text = self._load_rules()
        
        # Use Gemini 1.5 Pro for rich multimodal analysis as specified in the architecture
        if GEMINI_API_KEY:
            try:
                self.model = genai.GenerativeModel('gemini-1.5-pro')
                logger.info("Using Gemini 1.5 Pro for Multimodal Event Reporting.")
            except Exception as e:
                logger.warning(f"Failed to load gemini-1.5-pro, falling back to gemini-1.5-flash: {e}")
                self.model = genai.GenerativeModel('gemini-1.5-flash')
        else:
            self.model = None

    def _load_rules(self):
        try:
            if os.path.exists(self.rules_path):
                with open(self.rules_path, 'r', encoding='utf-8') as f:
                    return f.read()
            else:
                logger.warning(f"Rules file not found at {self.rules_path}. Using fallback guidelines.")
                return "기본 규칙: 따뜻하고 신뢰감 있는 문체로 사회연대경제 활동 보고서를 작성합니다."
        except Exception as e:
            logger.error(f"Failed to load rules from {self.rules_path}: {e}")
            return "기본 규칙: 따뜻하고 신뢰감 있는 문체로 사회연대경제 활동 보고서를 작성합니다."

    def generate_report(self, event_name, raw_notes, photo_filename=None):
        """
        Generates a markdown report draft based on a photo and raw notes.
        Saves the resulting draft to the 05_Output_Drafts folder.
        """
        # 1. Resolve photo path and load image if provided
        img = None
        photo_path = None
        if photo_filename:
            # Check both relative to workspace and absolute paths
            possible_paths = [
                os.path.join(self.workspace_path, "04_AppSheet_Media", photo_filename),
                photo_filename
            ]
            for path in possible_paths:
                if os.path.exists(path):
                    photo_path = path
                    break
            
            if photo_path:
                try:
                    img = Image.open(photo_path)
                    logger.info(f"Successfully loaded photo from {photo_path}")
                except Exception as e:
                    logger.error(f"Failed to load photo from {photo_path}: {e}")
            else:
                logger.warning(f"Photo '{photo_filename}' not found in AppSheet Media folder. Proceeding text-only.")

        # 2. Simulate if no Gemini API Key is available
        if not self.model:
            logger.info("Simulation mode: Generating mock draft.")
            draft_content = self._generate_simulation_draft(event_name, raw_notes, photo_filename)
        else:
            # 3. Call Gemini Multimodal Model
            prompt = f"""
역할: 사회연대경제(SSE) 전문 기자 및 홍보 에이전트

다음 지침과 규칙을 바탕으로 현장 사진과 메모를 분석하여 고품질 블로그 기사 초안을 작성해 주세요.

[콘텐츠 작성 가이드라인]
{self.rules_text}

---
[현장 정보]
- 행사명: {event_name}
- 현장 메모/키워드: {raw_notes}
- 작성일: {datetime.date.today().strftime('%Y년 %m월 %d일')}

[요구사항]
1. 위 가이드라인에 정의된 '블로그/뉴스 기사 구조 표준 템플릿'에 맞춰 정확히 본문을 작성해 주세요.
2. 만약 제공된 사진이 있다면, 사진 분석을 통해 현장의 생생한 모습(어떤 활동을 하고 있는지, 참여자들의 표정, 현장 분위기 등)을 묘사하여 [📸 오늘의 현장 스케치] 부분에 자연스럽게 삽입해 주세요. (사진이 없거나 분석이 어려우면 메모를 기반으로 생생하게 묘사해 주세요)
3. 템플릿 중 `[현재 일자]` 부분은 실제 오늘 일자({datetime.date.today().strftime('%Y-%m-%d')})로 교체해 주세요.
4. 마크다운 형식으로 작성해 주세요.
"""
            try:
                # Pass both the prompt and the PIL Image to the multimodal model
                inputs = [prompt]
                if img:
                    inputs.append(img)
                
                response = self.model.generate_content(inputs)
                draft_content = response.text
            except Exception as e:
                logger.error(f"Gemini API error during report generation: {e}")
                draft_content = self._generate_simulation_draft(event_name, f"{raw_notes} (API 오류 발생: {e})", photo_filename)

        # 4. Save the generated draft to 05_Output_Drafts folder
        safe_event_name = "".join(x for x in event_name if x.isalnum() or x in "._- ")
        output_filename = f"[초안]_{safe_event_name}.md"
        output_path = os.path.join(self.workspace_path, "05_Output_Drafts", output_filename)
        
        try:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(draft_content)
            logger.info(f"Report draft successfully saved to {output_path}")
            return {
                "success": True,
                "file_path": output_path,
                "file_name": output_filename,
                "content": draft_content
            }
        except Exception as e:
            logger.error(f"Failed to save draft to {output_path}: {e}")
            return {
                "success": False,
                "error": str(e),
                "content": draft_content
            }

    def _generate_simulation_draft(self, event_name, raw_notes, photo_filename):
        photo_section = f"![현장 사진](../04_AppSheet_Media/{photo_filename})\n*(사진 파일: {photo_filename})*" if photo_filename else "*(등록된 현장 사진이 없습니다)*"
        
        return f"""# 🌟 [따뜻한 동행] {event_name} 현장에서 피어난 사회적 가치

> **지역사회 주민들과 함께 협동과 연대의 온기를 나눈 뜻깊은 시간이었습니다.**

### 📸 오늘의 현장 스케치
{photo_section}
- **활동 일시**: {datetime.date.today().strftime('%Y년 %m월 %d일')}
- **장소**: 성동구 협동조합 소통 공간
- **함께해 주신 분들**: 지역 활동가, 주민 참여자 및 사회적경제 관계자

### 🤝 함께 나누는 이야기 (활동 상세)
이번에 진행된 **'{event_name}'** 행사는 사회적 가치를 직접 체감하고 지역 공동체의 결속을 다질 수 있도록 기획되었습니다. 

현장에서 공유된 메모에 따르면, "{raw_notes}"라는 소중한 발걸음들이 하나로 모여 행사의 깊이를 더했습니다. 참가자들은 시종일관 밝은 미소로 의견을 나누었으며, 서로의 손을 맞잡고 따뜻한 연대의 이야기를 나누었습니다. 특히 다양한 세대가 한자리에 모여 사회적 협동의 의미를 되짚어보는 과정은 그 자체로 커다란 감동을 선사했습니다.

### 🌱 더 나은 내일을 위한 발걸음 (사회적 가치)
우리가 만들어가는 사회연대경제는 거창한 구호에 머무르지 않고, 오늘과 같은 일상의 실천 속에서 그 싹을 틔웁니다. 한 사람 한 사람의 참여가 어우러져 만들어낸 긍정적인 파급력은 우리 공동체를 더욱 든든하게 지탱하는 버팀목이 될 것입니다. 앞으로도 지속 가능한 발전과 따뜻한 포용 사회를 향해 멈추지 않고 나아가겠습니다.

---
**작성일**: {datetime.date.today().strftime('%Y-%m-%d')} | **작성자**: 사회연대경제 자율 에이전트 (시뮬레이션 모드)
"""
