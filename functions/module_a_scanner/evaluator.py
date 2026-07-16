"""
Module A: Evaluator Agent using Google Gemini
"""
import os
import json
import logging
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
    logger.warning("GEMINI_API_KEY not found in environment. Evaluations will be simulated.")

class GrantEvaluator:
    def __init__(self, rules_path):
        self.rules_path = rules_path
        self.rules_text = self._load_rules()
        
        # Use Gemini 1.5 Flash for fast textual analysis
        if GEMINI_API_KEY:
            self.model = genai.GenerativeModel('gemini-1.5-flash')
        else:
            self.model = None

    def _load_rules(self):
        try:
            with open(self.rules_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Failed to load rules from {self.rules_path}: {e}")
            return "기본 규칙: 사회적기업에 적합한 사업을 찾습니다."

    def evaluate(self, grant_data):
        """
        Calls Gemini to evaluate the grant against the agent's rules.
        Expected to return a dict with 'score' (1-10) and 'reason'.
        """
        if not self.model:
            # Fallback mock evaluation if no API key
            logger.info(f"Simulating evaluation for: {grant_data['title']}")
            score = 9 if "사회적" in grant_data['title'] or "소셜" in grant_data['title'] else 3
            return {
                "score": score,
                "reason": "시뮬레이션된 평가 결과입니다. (API 키 미등록)"
            }

        prompt = f"""
다음은 우리 조직의 지원사업 타겟팅 필터링 룰입니다:
{self.rules_text}

---
새로운 지원사업 공고가 수집되었습니다:
- 공고명: {grant_data['title']}
- 요약내용: {grant_data['content_summary']}

위 규칙을 바탕으로 이 공고가 우리 조직에 얼마나 적합한지 평가해 주세요.
반드시 아래의 JSON 형식으로만 응답해 주세요. (마크다운 백틱 없이 순수 JSON만 출력)

{{
    "score": [1에서 10 사이의 정수 점수],
    "reason": "[적합도 점수를 부여한 이유에 대한 3줄 요약]"
}}
"""
        try:
            response = self.model.generate_content(prompt)
            # Clean up potential markdown formatting from the response
            raw_text = response.text.strip().replace('```json', '').replace('```', '')
            result = json.loads(raw_text)
            return result
        except Exception as e:
            logger.error(f"Gemini API error during evaluation: {e}")
            return {"score": 1, "reason": "AI 평가 중 오류가 발생했습니다."}
