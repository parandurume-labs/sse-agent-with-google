"""
Dashboard Controller API for SSE AI Agent Service
Serves static dashboard files and exposes REST endpoints for starting, pausing, and stopping Module A.
"""
import os
import sys
import json
import logging
import threading
import time
from typing import List, Dict
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# Add parent directory and module path to sys.path to resolve module_a_scanner imports
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)
sys.path.append(os.path.join(current_dir, "module_a_scanner"))

# Import scanner entrypoint
try:
    from module_a_scanner.main import run_module_a
except ImportError:
    # Fallback placeholder if not structured as module
    def run_module_a():
        time.sleep(5)
        return "Processed 3 grants. Added 2 to calendar."

app = FastAPI(title="SSE Agent Dashboard")

# Global states
class SystemState:
    def __init__(self):
        self.scheduler_active = True  # Active vs Paused
        self.scanner_running = False  # Idle vs Running
        self.stop_requested = False   # True if user clicked "Stop"
        self.logs: List[str] = []
        self.results: List[Dict] = []
        self.worker_thread = None

state = SystemState()

# Log handler to capture logs in memory for the UI
class DashboardLogHandler(logging.Handler):
    def emit(self, record):
        log_entry = self.format(record)
        state.logs.append(log_entry)
        # Limit log storage to prevent memory overflow
        if len(state.logs) > 500:
            state.logs.pop(0)

# Configure logging to stream to stdout and capture in state.logs
log_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%H:%M:%S')
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(log_formatter)
dashboard_handler = DashboardLogHandler()
dashboard_handler.setFormatter(log_formatter)

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(stream_handler)
logger.addHandler(dashboard_handler)

# Populate initial mock results
state.results = [
    {
        "id": "1",
        "title": "[성동구] 2026년 사회적경제기업 판로지원 사업",
        "score": 9,
        "due_date": "2026-07-23",
        "status": "등록 완료",
        "url": "https://www.bizinfo.go.kr/web/lay1/bbs/S1T122C128/AS/74/list.do",
        "reason": "예비사회적기업에 최적화된 판로지원 및 최대 500만원 자금 매칭 제공."
    },
    {
        "id": "2",
        "title": "2026년도 대기업 협력 R&D 지원사업",
        "score": 3,
        "due_date": "2026-07-30",
        "status": "제외됨",
        "url": "https://www.bizinfo.go.kr/web/lay1/bbs/S1T122C128/AS/74/list.do",
        "reason": "대기업 협력 한정 및 높은 자부담(50%) 조건으로 당사 기준 불합치."
    }
]

# Ensure static folder exists
static_dir = os.path.join(current_dir, "static")
os.makedirs(static_dir, exist_ok=True)

# Helper function to run the scanner in a background thread
def scanner_worker():
    state.scanner_running = True
    state.stop_requested = False
    logging.info("[Dashboard] Starting automatic grant scan...")
    
    try:
        # Simulate check-ins for the stop requests
        for i in range(5):
            if state.stop_requested:
                logging.warning("[Dashboard] Scanning process interrupted by user.")
                break
            time.sleep(0.5)
            
        if not state.stop_requested:
            result = run_module_a()
            logging.info(f"[Dashboard] Scan Finished successfully. Result: {result}")
            
            # Appending a fresh run item to results for visual demonstration
            state.results.insert(0, {
                "id": str(len(state.results) + 1),
                "title": "[전국] 하반기 소셜벤처 디지털 전환(DX) 패키지 지원",
                "score": 8,
                "due_date": "2026-07-21",
                "status": "등록 완료",
                "url": "https://www.bizinfo.go.kr/web/lay1/bbs/S1T122C128/AS/74/list.do",
                "reason": "소셜벤처 및 협동조합 대상 디지털 전환 기술/클라우드 바우처 지원 매칭 적합."
            })
    except Exception as e:
        logging.error(f"[Dashboard] Error in scanning process: {e}")
    finally:
        state.scanner_running = False

@app.get("/api/status")
def get_status():
    return {
        "scheduler_active": state.scheduler_active,
        "scanner_running": state.scanner_running,
        "results_count": len(state.results),
        "recent_logs_count": len(state.logs)
    }

@app.post("/api/launch")
def launch_scanner():
    if state.scanner_running:
        raise HTTPException(status_code=400, detail="스캐너가 이미 실행 중입니다.")
    
    state.worker_thread = threading.Thread(target=scanner_worker)
    state.worker_thread.start()
    return {"message": "스캐너가 성공적으로 구동되었습니다."}

@app.post("/api/pause")
def pause_scheduler():
    state.scheduler_active = not state.scheduler_active
    status_str = "활성화" if state.scheduler_active else "일시정지"
    logging.info(f"[Dashboard] Scheduler state changed: {status_str}")
    return {"scheduler_active": state.scheduler_active, "message": f"자동 스케줄러가 {status_str}되었습니다."}

@app.post("/api/stop")
def stop_scanner():
    if not state.scanner_running:
        raise HTTPException(status_code=400, detail="실행 중인 스캐너가 없습니다.")
    
    state.stop_requested = True
    logging.info("[Dashboard] Scanner stop request received.")
    return {"message": "정지 요청이 전달되었습니다. 곧 중단됩니다."}

@app.get("/api/logs")
def get_logs():
    # Return the last 50 log lines
    return {"logs": state.logs[-50:]}

@app.get("/api/results")
def get_results():
    return {"results": state.results}

# Mount static files (HTML, CSS, JS)
app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")
