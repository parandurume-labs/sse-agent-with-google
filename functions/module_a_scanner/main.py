"""
Module A: Main Orchestrator (Grant Scanner & Calendar Registration)
"""
import os
import logging
from scraper import GrantScraper
from evaluator import GrantEvaluator
from calendar_sync import CalendarSync

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Resolve workspace path relative to this script or via env var
WORKSPACE_PATH = os.getenv(
    "WORKSPACE_PATH", 
    os.path.abspath(os.path.join(os.path.dirname(__file__), "../..", "SSE_Agent_Workspace"))
)
RULES_FILE = os.path.join(WORKSPACE_PATH, "01_Agent_Profiles", "Agent_Grant_Searcher.md")

def run_module_a(request=None):
    """
    Entry point for Google Cloud Functions.
    (Can also be run locally directly).
    """
    logger.info("=== Starting Module A: Grant Scanner Sprint ===")
    
    # 1. Initialize components
    scraper = GrantScraper()
    evaluator = GrantEvaluator(rules_path=RULES_FILE)
    cal_sync = CalendarSync()

    # 2. Fetch new grants (e.g., from Bizinfo)
    grants = scraper.fetch_grants(max_items=3)
    if not grants:
        logger.info("No new grants found today.")
        return "OK"

    # 3. Evaluate each grant and process if S >= 8
    processed_count = 0
    for grant in grants:
        logger.info(f"Evaluating: {grant['title']}")
        evaluation = evaluator.evaluate(grant)
        
        score = evaluation.get('score', 0)
        reason = evaluation.get('reason', '사유 없음')
        
        logger.info(f"Score: {score} | Reason: {reason}")
        
        if score >= 8:
            logger.info(f"HIGH SUITABILITY (S={score})! Adding to Calendar...")
            success = cal_sync.add_grant_deadline(grant, evaluation)
            if success:
                processed_count += 1
                # Note: In a full architecture, we'd also log this to Google Sheets (T_Grant_Master) here.
        else:
            logger.info(f"Skipping calendar registration (Score {score} < 8)")

    logger.info(f"=== Module A Completed. Added {processed_count} grants to calendar. ===")
    return f"Processed {len(grants)} grants. Added {processed_count} to calendar."

if __name__ == "__main__":
    # Local execution for testing
    run_module_a()
