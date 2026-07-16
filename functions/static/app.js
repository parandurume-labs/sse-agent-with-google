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

// Module C Elements
const elBtnGenerateReport = document.getElementById('btn-generate-report');
const elEventName = document.getElementById('event-name');
const elPhotoFilename = document.getElementById('photo-filename');
const elRawNotes = document.getElementById('raw-notes');
const elDraftStatus = document.getElementById('draft-status');
const elPreviewBox = document.getElementById('preview-box');
const elDraftMeta = document.getElementById('draft-meta');
const elDraftPath = document.getElementById('draft-path');

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

// -------------------------------------------------------------
// Module B: RAG Wiki Chatbot logic
// -------------------------------------------------------------
const elChatHistory = document.getElementById('chat-history');
const elChatInput = document.getElementById('chat-input');
const elBtnChatSend = document.getElementById('btn-chat-send');

function appendChatMessage(sender, text, role = 'assistant') {
    const msgDiv = document.createElement('div');
    msgDiv.className = `chat-message ${role}`;
    
    const senderDiv = document.createElement('div');
    senderDiv.className = 'message-sender';
    senderDiv.textContent = sender;
    
    const textDiv = document.createElement('div');
    textDiv.className = 'message-text';
    
    // Simple markdown formatting (bold, code, lists, and linebreaks)
    let formattedText = text
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/`(.*?)`/g, '<code>$1</code>')
        .replace(/\n/g, '<br>');
    textDiv.innerHTML = formattedText;
    
    msgDiv.appendChild(senderDiv);
    msgDiv.appendChild(textDiv);
    elChatHistory.appendChild(msgDiv);
    elChatHistory.scrollTop = elChatHistory.scrollHeight;
}

let elTypingIndicator = null;
function showTypingIndicator() {
    elTypingIndicator = document.createElement('div');
    elTypingIndicator.className = 'chat-message assistant typing';
    elTypingIndicator.innerHTML = `
        <div class="message-sender">🤖 Wiki Bot</div>
        <div class="message-text"><span class="typing-dots"><span>.</span><span>.</span><span>.</span></span></div>
    `;
    elChatHistory.appendChild(elTypingIndicator);
    elChatHistory.scrollTop = elChatHistory.scrollHeight;
}

function removeTypingIndicator() {
    if (elTypingIndicator) {
        elTypingIndicator.remove();
        elTypingIndicator = null;
    }
}

async function handleChatSend() {
    const question = elChatInput.value.trim();
    if (!question) return;

    elChatInput.value = '';
    appendChatMessage('👤 나', question, 'user');
    showTypingIndicator();
    
    elChatInput.disabled = true;
    elBtnChatSend.disabled = true;

    try {
        const res = await fetch(`${API_BASE}/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ question })
        });
        
        removeTypingIndicator();

        if (!res.ok) throw new Error("서버 응답 에러");
        const data = await res.json();
        appendChatMessage('🤖 Wiki Bot', data.answer, 'assistant');
    } catch (err) {
        removeTypingIndicator();
        appendChatMessage('🤖 Wiki Bot', `오류가 발생했습니다: ${err.message}`, 'assistant');
    } finally {
        elChatInput.disabled = false;
        elBtnChatSend.disabled = false;
        elChatInput.focus();
    }
}

elBtnChatSend.addEventListener('click', handleChatSend);
elChatInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
        handleChatSend();
    }
});

// Trigger Module C: Event Report Draft Generation
async function handleGenerateReport() {
    const eventName = elEventName.value.trim();
    const rawNotes = elRawNotes.value.trim();
    const photoFilename = elPhotoFilename.value;

    if (!eventName || !rawNotes) {
        alert("행사명과 현장 메모를 입력해 주세요!");
        return;
    }

    appendConsoleLog(`[Console] Module C 기사 초안 생성 기동... 행사명: ${eventName}`, "system");
    
    // Update UI State to Generating
    elBtnGenerateReport.disabled = true;
    elBtnGenerateReport.innerHTML = '<span class="btn-icon">⏳</span> 생성 중 (Generating...)';
    elDraftStatus.textContent = "생성 중";
    elDraftStatus.className = "draft-status-badge generating";
    elPreviewBox.innerHTML = '<div class="loading">Gemini 1.5 Pro가 현장 분석 및 기사 초안을 작성 중입니다...<br>이 작업은 약 5~15초 소요될 수 있습니다.</div>';
    elDraftMeta.style.display = 'none';

    try {
        const payload = {
            event_name: eventName,
            raw_notes: rawNotes,
            photo_filename: photoFilename || null
        };

        const res = await fetch(`/api/report`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });

        if (!res.ok) {
            const errorData = await res.json();
            throw new Error(errorData.detail || "서버 오류 발생");
        }

        const data = await res.json();
        
        // Parse simple markdown for preview box
        elPreviewBox.innerHTML = parseSimpleMarkdown(data.content);
        
        // Update draft meta
        elDraftPath.textContent = data.file_path;
        elDraftMeta.style.display = 'flex';
        
        // Update badges
        elDraftStatus.textContent = "작성 완료";
        elDraftStatus.className = "draft-status-badge success";
        appendConsoleLog(`[Server] 기사 초안 작성 완료! 저장 위치: ${data.file_name}`, "system");

    } catch (err) {
        appendConsoleLog(`[Error] 기사 생성 실패: ${err.message}`, "error");
        elPreviewBox.innerHTML = `<div class="log-line error" style="text-align: center; padding: 2rem 0;">기사 초안 생성에 실패했습니다.<br>사유: ${err.message}</div>`;
        elDraftStatus.textContent = "실패";
        elDraftStatus.className = "draft-status-badge";
    } finally {
        elBtnGenerateReport.disabled = false;
        elBtnGenerateReport.innerHTML = '<span class="btn-icon">📝</span> 기사 초안 생성 (Generate Draft)';
    }
}

// Lightweight parser to render beautiful MD in the Glassmorphism card
function parseSimpleMarkdown(markdown) {
    if (!markdown) return '';
    let html = markdown;
    
    // Escape HTML first to prevent injection
    html = html
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;");
    
    // Replace headers
    html = html.replace(/^#\s+(.+)$/gm, '<h1>$1</h1>');
    html = html.replace(/^###\s+(.+)$/gm, '<h3>$1</h3>');
    html = html.replace(/^##\s+(.+)$/gm, '<h2>$1</h2>');
    
    // Replace blockquotes (which got escaped to &gt;)
    html = html.replace(/^&gt;\s+(.+)$/gm, '<blockquote>$1</blockquote>');
    
    // Replace bold text
    html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
    
    // Replace italic text
    html = html.replace(/\*(.+?)\*/g, '<em>$1</em>');
    
    // Replace horizontal rules
    html = html.replace(/^---$/gm, '<hr style="border: none; border-top: 1px solid rgba(255,255,255,0.1); margin: 1rem 0;">');
    
    // Replace carriage returns with line breaks (excluding headers/quotes/lists)
    html = html.replace(/\n/g, '<br>');
    
    return html;
}

// Listeners
elBtnLaunch.addEventListener('click', handleLaunch);
elBtnPause.addEventListener('click', handlePause);
elBtnStop.addEventListener('click', handleStop);
elBtnGenerateReport.addEventListener('click', handleGenerateReport);

// Event loops (Auto updates)
updateStatus();
fetchResults();
fetchLogs();

setInterval(updateStatus, 1500);
setInterval(fetchLogs, 1000);
setInterval(fetchResults, 3000);
