/* -------------------------------------------------------------
   SSE AI Agent Dashboard: Client Logic Controller (app.js)
------------------------------------------------------------- */

// Elements
const elSchedulerBadge = document.getElementById('scheduler-badge');
const elProcessBadge = document.getElementById('process-badge');
const elBtnLaunch = document.getElementById('btn-launch');
const elBtnPause = document.getElementById('btn-pause');
const elBtnStop = document.getElementById('btn-stop');
const elPauseIcon = document.getElementById('pause-icon');
const elPauseText = document.getElementById('pause-text');
const elConsoleLogs = document.getElementById('console-logs');
const elResultsContainer = document.getElementById('results-container');
const elLogPulse = document.getElementById('log-pulse');

// API Base URLs
const API_BASE = '/api';

// Utility: Create log lines in the console box
function appendConsoleLog(text, type = 'info') {
    const div = document.createElement('div');
    div.className = `log-line ${type}`;
    div.textContent = text;
    elConsoleLogs.appendChild(div);
    elConsoleLogs.scrollTop = elConsoleLogs.scrollHeight;
}

// Fetch and update system status
async function updateStatus() {
    try {
        const res = await fetch(`${API_BASE}/status`);
        if (!res.ok) throw new Error("Status API request failed.");
        const data = await res.json();

        // Update scheduler badge & text
        if (data.scheduler_active) {
            elSchedulerBadge.className = 'badge badge-active';
            elSchedulerBadge.textContent = '활성화됨';
            elPauseIcon.textContent = '⏸️';
            elPauseText.textContent = '일시정지 (Pause)';
        } else {
            elSchedulerBadge.className = 'badge badge-paused';
            elSchedulerBadge.textContent = '일시정지';
            elPauseIcon.textContent = '▶️';
            elPauseText.textContent = '스케줄 재개 (Resume)';
        }

        // Update scanner process state
        if (data.scanner_running) {
            elProcessBadge.className = 'badge badge-scanning';
            elProcessBadge.textContent = '스캔 중 (Scanning)';
            elBtnLaunch.disabled = true;
            elBtnStop.disabled = false;
            elLogPulse.className = 'pulse-indicator scanning';
        } else {
            elProcessBadge.className = 'badge badge-idle';
            elProcessBadge.textContent = '대기중 (Idle)';
            elBtnLaunch.disabled = false;
            elBtnStop.disabled = true;
            elLogPulse.className = 'pulse-indicator';
        }

    } catch (err) {
        console.error("Error fetching system status:", err);
    }
}

// Fetch real-time logs from backend and render inside the console
let lastLogLength = 0;
async function fetchLogs() {
    try {
        const res = await fetch(`${API_BASE}/logs`);
        if (!res.ok) throw new Error("Logs API failed.");
        const data = await res.json();
        const logs = data.logs;

        if (logs.length > lastLogLength) {
            // Append only new logs
            const newLogs = logs.slice(lastLogLength);
            newLogs.forEach(line => {
                let type = 'info';
                if (line.includes('ERROR') || line.includes('Failed')) type = 'error';
                else if (line.includes('WARNING') || line.includes('not found')) type = 'warning';
                else if (line.includes('[Dashboard]') || line.includes('===')) type = 'system';
                
                appendConsoleLog(line, type);
            });
            lastLogLength = logs.length;
        } else if (logs.length < lastLogLength) {
            // Logs cleared or restarted
            elConsoleLogs.innerHTML = '';
            lastLogLength = 0;
        }
    } catch (err) {
        console.error("Error fetching logs:", err);
    }
}

// Fetch results history (the scanned grants)
async function fetchResults() {
    try {
        const res = await fetch(`${API_BASE}/results`);
        if (!res.ok) throw new Error("Results API failed.");
        const data = await res.json();
        const results = data.results;

        if (results.length === 0) {
            elResultsContainer.innerHTML = '<div class="loading">등록된 지원사업 매칭 결과가 없습니다.</div>';
            return;
        }

        elResultsContainer.innerHTML = '';
        results.forEach(grant => {
            const card = document.createElement('div');
            card.className = 'result-card';
            
            const isHigh = grant.score >= 8;
            const scoreClass = isHigh ? 'score-high' : 'score-low';
            
            card.innerHTML = `
                <div class="score-badge ${scoreClass}">${grant.score}</div>
                <div class="card-info">
                    <div class="card-title-row">
                        <h4 class="card-title">${grant.title}</h4>
                        <span class="card-date">마감일: ${grant.due_date}</span>
                    </div>
                    <p class="card-desc">${grant.reason}</p>
                    <div class="card-tags">
                        <span class="tag">적합도 스코어: ${grant.score}/10</span>
                        <span class="tag" style="color: ${isHigh ? 'var(--emerald)' : 'var(--crimson)'}">${grant.status}</span>
                        ${grant.url ? `
                            <a href="${grant.url}" target="_blank" class="tag" style="margin-left: auto; color: var(--cyan-glow); border: 1px solid rgba(0, 242, 254, 0.25); background: rgba(0, 242, 254, 0.05); text-decoration: none; font-weight: 500; display: flex; align-items: center; gap: 0.2rem; transition: all 0.2s;">
                                🔗 원문 보기
                            </a>
                        ` : ''}
                    </div>
                </div>
            `;
            elResultsContainer.appendChild(card);
        });

    } catch (err) {
        console.error("Error fetching results:", err);
    }
}

// Trigger "Launch"
async function handleLaunch() {
    appendConsoleLog("[Console] 즉시 실행 명령어(Launch) 전송...", "system");
    try {
        const res = await fetch(`${API_BASE}/launch`, { method: 'POST' });
        const data = await res.json();
        appendConsoleLog(`[Server] ${data.message || data.detail}`, "system");
        updateStatus();
    } catch (err) {
        appendConsoleLog(`[Error] 실행 요청 실패: ${err.message}`, "error");
    }
}

// Trigger "Pause / Resume"
async function handlePause() {
    appendConsoleLog("[Console] 자동 스케줄 상태 변경 요청...", "system");
    try {
        const res = await fetch(`${API_BASE}/pause`, { method: 'POST' });
        const data = await res.json();
        appendConsoleLog(`[Server] ${data.message}`, "system");
        updateStatus();
    } catch (err) {
        appendConsoleLog(`[Error] 상태 변경 요청 실패: ${err.message}`, "error");
    }
}

// Trigger "Stop"
async function handleStop() {
    appendConsoleLog("[Console] 강제 중단 명령어(Stop) 전송...", "warning");
    try {
        const res = await fetch(`${API_BASE}/stop`, { method: 'POST' });
        const data = await res.json();
        appendConsoleLog(`[Server] ${data.message || data.detail}`, "warning");
        updateStatus();
    } catch (err) {
        appendConsoleLog(`[Error] 중단 요청 실패: ${err.message}`, "error");
    }
}

// Listeners
elBtnLaunch.addEventListener('click', handleLaunch);
elBtnPause.addEventListener('click', handlePause);
elBtnStop.addEventListener('click', handleStop);

// Event loops (Auto updates)
updateStatus();
fetchResults();
fetchLogs();

setInterval(updateStatus, 1500);
setInterval(fetchLogs, 1000);
setInterval(fetchResults, 3000);
