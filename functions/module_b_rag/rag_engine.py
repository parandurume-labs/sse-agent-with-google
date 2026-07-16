"""
Module B: RAG Engine using Google Gemini
"""
import os
import logging
import google.generativeai as genai
from dotenv import load_dotenv
from drive_client import DriveClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
else:
    logger.warning("GEMINI_API_KEY not found in environment. RAG answers will be simulated.")

class RAGEngine:
    def __init__(self):
        self.drive_client = DriveClient()
        if GEMINI_API_KEY:
            self.model = genai.GenerativeModel('gemini-1.5-flash')
        else:
            self.model = None

    def query(self, question: str) -> str:
        """
        Retrieves relevant context from Google Drive markdown files 
        and answers the user's question using Gemini.
        """
        # 1. Fetch documents
        docs = self.drive_client.fetch_wiki_files()
        
        if not docs:
            return "사내 지식 베이스(02_Knowledge_Wiki)에 등록된 문서가 없거나 접근할 수 없습니다."

        # 2. Build the context
        context_parts = []
        for filename, content in docs.items():
            context_parts.append(f"=== 문서 파일: {filename} ===\n{content}\n")
        
        context_text = "\n".join(context_parts)

        # 3. If no Gemini API key, return a simulated response based on simple keyword match
        if not self.model:
            logger.info("Simulating RAG response (No Gemini API Key)")
            return self._simulate_response(question, docs)

        # 4. Construct prompt
        prompt = f"""
당신은 사회연대경제(SSE) 조직을 위한 AI 비서 및 사내 지식 위키 챗봇입니다.
아래에 제공되는 사내 지식 베이스 문서들을 바탕으로 사용자의 질문에 친절하고 정확하게 답해 주세요.

[중요 지침]
- 반드시 아래 제공된 문서 내용만을 바탕으로 답변해야 하며, 지식 베이스에 없는 임의의 사실을 지어내지 마세요.
- 답변을 구성할 때 반드시 정보의 출처(예: '사내_운영_규정.md' 파일에 따르면...)를 명확히 밝혀주세요.
- 만약 제공된 문서에서 사용자의 질문에 대한 답을 찾을 수 없는 경우, "제공된 사내 문서 내에서는 해당 내용을 찾을 수 없습니다. 추가 문서가 필요하시면 등록해 주세요."라고 답해 주세요.

---
[사내 지식 베이스 문서]
{context_text}

---
[사용자 질문]
{question}
"""

        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            logger.error(f"Gemini API error during RAG: {e}")
            return "Gemini API 호출 중 오류가 발생했습니다. 잠시 후 다시 시도해 주세요."

    def _simulate_response(self, question: str, docs: dict) -> str:
        """Simulates RAG engine responses in case of missing API credentials."""
        question_lower = question.lower()
        
        # Simple rule-based mock matching
        if "정기총회" in question_lower or "서명" in question_lower or "양식" in question_lower:
            doc_name = "사내_운영_규정.md"
            if doc_name in docs:
                return (
                    f"**[시뮬레이션 답변]** (API 키가 등록되지 않아 로컬 규칙 기반으로 답변합니다.)\n\n"
                    f"`{doc_name}` 문서에 따르면, 정기총회 의사록 및 서명 양식은 제5조(총회의 소집) 및 "
                    f"제6조(총회의 의결 및 서명 날인)에 규정되어 있습니다. "
                    f"실제 양식 파일은 사내 서식 보관 폴더를 참조해 주시기 바랍니다."
                )
        
        elif "정산" in question_lower or "집행" in question_lower or "지원금" in question_lower:
            doc_name = "지원금_집행_및_정산_매뉴얼.md"
            if doc_name in docs:
                return (
                    f"**[시뮬레이션 답변]** (API 키가 등록되지 않아 로컬 규칙 기반으로 답변합니다.)\n\n"
                    f"`{doc_name}` 문서의 가이드에 따르면, 모든 지원금 집행은 법인카드 사용을 원칙으로 하며 "
                    f"영수증 및 지출결의서를 5영업일 이내에 제출하셔야 정상 정산 처리됩니다."
                )

        # General default response
        best_match_doc = None
        for doc_name, content in docs.items():
            # Check if any words from question exist in the document
            words = [w for w in question.split() if len(w) > 1]
            if any(w in content for w in words):
                best_match_doc = doc_name
                break
                
        if best_match_doc:
            return (
                f"**[시뮬레이션 답변]** (API 키가 등록되지 않아 로컬 문서 매칭으로 답변합니다.)\n\n"
                f"질문하신 내용과 관련하여 `{best_match_doc}` 파일에 언급된 부분이 있는 것으로 추정됩니다. "
                f"Gemini API 키가 등록되면 인공지능이 문맥을 이해하고 보다 명확한 요약 답변을 제공해 드립니다."
            )
            
        return "제공된 사내 문서 내에서는 질문하신 내용과 관련된 문서를 매칭할 수 없습니다."

if __name__ == "__main__":
    engine = RAGEngine()
    test_q = "정기총회 서명 양식은 어디에 있지?"
    print(f"Question: {test_q}")
    print(f"Answer:\n{engine.query(test_q)}")
