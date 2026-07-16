/**
 * Google Apps Script for T_Grant_Master Google Sheet
 * 
 * 이 스크립트를 구글 시트의 [확장 프로그램] -> [Apps Script]에 붙여넣어 사용하세요.
 * 시트가 열릴 때 상단에 [🤖 에이전트 제어] 메뉴가 추가되며, 시트를 컨트롤 타워 및 DB로 활용할 수 있습니다.
 */

// 1. 에이전트 백엔드 API URL 설정 (GCP Cloud Functions 또는 배포된 서버 주소)
const BACKEND_API_URL = "https://your-gcp-cloud-functions-url.a.run.app"; // 실제 배포 시 이 부분을 수정하세요.

/**
 * 시트가 열릴 때 자동으로 커스텀 메뉴를 추가합니다.
 */
function onOpen() {
  const ui = SpreadsheetApp.getUi();
  ui.createMenu('🤖 에이전트 제어')
      .addItem('⚡ 지원사업 스캔 즉시 실행 (Run)', 'runScanner')
      .addItem('🛑 스캔 강제 중단 (Stop)', 'stopScanner')
      .addSeparator()
      .addItem('🔄 최신 분석 결과 불러오기 (Sync)', 'fetchResultsToSheet')
      .addToUi();
}

/**
 * 1. 백엔드 스캐너 실행 트리거
 */
function runScanner() {
  const ui = SpreadsheetApp.getUi();
  const url = BACKEND_API_URL + "/api/launch";
  
  try {
    const options = {
      'method': 'post',
      'muteHttpExceptions': true
    };
    
    appendLogToConsole("구글 시트 제어로 에이전트 스캐너 실행 요청 송신...");
    const response = UrlFetchApp.fetch(url, options);
    const responseCode = response.getResponseCode();
    
    if (responseCode === 200) {
      ui.alert('성공', '지원사업 스캐너가 성공적으로 실행되었습니다. 분석에 수 분이 소요될 수 있습니다.', ui.ButtonSet.OK);
    } else {
      ui.alert('실패', '서버 응답 오류 (' + responseCode + '): ' + response.getContentText(), ui.ButtonSet.OK);
    }
  } catch (e) {
    ui.alert('에러', '백엔드 연결 실패: ' + e.toString() + '\n(로컬 환경 테스트 시에는 배포된 공개 URL이 필요합니다.)', ui.ButtonSet.OK);
  }
}

/**
 * 2. 백엔드 스캐너 정지 트리거
 */
function stopScanner() {
  const ui = SpreadsheetApp.getUi();
  const url = BACKEND_API_URL + "/api/stop";
  
  try {
    const options = {
      'method': 'post',
      'muteHttpExceptions': true
    };
    
    const response = UrlFetchApp.fetch(url, options);
    const responseCode = response.getResponseCode();
    
    if (responseCode === 200) {
      ui.alert('중단 성공', '스캐너 강제 중단 명령이 성공적으로 전달되었습니다.', ui.ButtonSet.OK);
    } else {
      ui.alert('실패', '서버 응답 오류: ' + response.getContentText(), ui.ButtonSet.OK);
    }
  } catch (e) {
    ui.alert('에러', '백엔드 연결 실패: ' + e.toString(), ui.ButtonSet.OK);
  }
}

/**
 * 3. 백엔드 API로부터 최신 매칭 결과를 받아 구글 시트(DB)에 동기화
 * (T_Grant_Master 스키마 준수)
 */
function fetchResultsToSheet() {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  const url = BACKEND_API_URL + "/api/results";
  
  try {
    // 헤더 행 설정 및 데이터 초기화 검증
    setupSheetHeaders(sheet);
    
    const response = UrlFetchApp.fetch(url);
    const data = JSON.parse(response.getContentText());
    const results = data.results || [];
    
    if (results.length === 0) {
      SpreadsheetApp.getUi().alert('알림', '가져올 새로운 분석 결과가 없습니다.', SpreadsheetApp.getUi().ButtonSet.OK);
      return;
    }
    
    // 기존 데이터 읽기 (중복 입력 방지용 PK 세트 구축)
    const lastRow = sheet.getLastRow();
    const existingIds = new Set();
    if (lastRow > 1) {
      const idRange = sheet.getRange(2, 1, lastRow - 1, 1).getValues();
      idRange.forEach(row => existingIds.add(row[0].toString()));
    }
    
    // 신규 데이터 필터링 후 역순으로 시트에 추가
    let addedCount = 0;
    for (let i = results.length - 1; i >= 0; i--) {
      const grant = results[i];
      if (!existingIds.has(grant.id.toString())) {
        sheet.appendRow([
          grant.id,
          grant.title,
          "https://www.bizinfo.go.kr", // 실제 공고 링크 매핑
          grant.due_date,
          grant.score,
          grant.reason,
          grant.score >= 8 ? "지원예정" : "포기" // 스코어 기반 상태 초기값 자동 매핑
        ]);
        addedCount++;
      }
    }
    
    SpreadsheetApp.getUi().alert('동기화 완료', addedCount + '개의 새로운 지원사업 매칭 데이터가 구글 시트 DB에 등록되었습니다.', SpreadsheetApp.getUi().ButtonSet.OK);
    
  } catch (e) {
    SpreadsheetApp.getUi().alert('에러', '데이터 동기화 실패: ' + e.toString(), SpreadsheetApp.getUi().ButtonSet.OK);
  }
}

/**
 * 시트 헤더 초기 구성 함수 (T_Grant_Master 스키마)
 */
function setupSheetHeaders(sheet) {
  if (sheet.getLastRow() === 0) {
    const headers = [
      "grant_id (PK)", 
      "title (공고명)", 
      "link (공고 URL)", 
      "due_date (마감일)", 
      "suitability_score (적합도 점수)", 
      "reason (추천 사유)", 
      "status (검토중 / 지원예정 / 포기)"
    ];
    sheet.appendRow(headers);
    
    // 헤더 스타일링 (볼드체, 배경색 추가)
    const headerRange = sheet.getRange(1, 1, 1, headers.length);
    headerRange.setFontWeight("bold");
    headerRange.setBackground("#f1f5f9");
    headerRange.setHorizontalAlignment("center");
  }
}

/**
 * 간단한 디버그용 콘솔 출력 로직
 */
function appendLogToConsole(message) {
  Logger.log(message);
}
