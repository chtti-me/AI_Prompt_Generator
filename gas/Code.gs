/**
 * AI Prompt Generator Platform - Google Apps Script
 * 自動化 Google Sheets 與平台整合
 */

// ============================================================================
// 配置
// ============================================================================

const CONFIG = {
  API_BASE_URL: 'http://localhost:5001/api',  // 修改為您的伺服器位址
  SHEET_NAMES: {
    PROMPTS: 'Prompts_Library',
    HISTORY: 'Generated_History',
    ANALYTICS: 'Analytics'
  }
};

// ============================================================================
// 選單建立
// ============================================================================

function onOpen() {
  const ui = SpreadsheetApp.getUi();
  ui.createMenu('🤖 AI Prompt')
    .addItem('📊 同步提示詞', 'syncPromptsFromPlatform')
    .addItem('🔄 刷新統計', 'refreshAnalytics')
    .addSeparator()
    .addItem('⚙️ 設定 API', 'showApiSettings')
    .addToUi();
}

// ============================================================================
// 主要功能
// ============================================================================

/**
 * 從平台同步提示詞到 Google Sheets
 */
function syncPromptsFromPlatform() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const promptsSheet = getOrCreateSheet(ss, CONFIG.SHEET_NAMES.PROMPTS);

  try {
    // 呼叫 API 取得提示詞列表
    const url = `${CONFIG.API_BASE_URL}/prompts`;
    const response = UrlFetchApp.fetch(url, {
      method: 'get',
      headers: {
        'Content-Type': 'application/json'
      },
      muteHttpExceptions: true
    });

    if (response.getResponseCode() === 200) {
      const data = JSON.parse(response.getContentText());

      // 清空現有資料（保留標題）
      if (promptsSheet.getLastRow() > 1) {
        promptsSheet.getRange(2, 1, promptsSheet.getLastRow() - 1, promptsSheet.getLastColumn()).clear();
      }

      // 寫入新資料
      if (data.prompts && data.prompts.length > 0) {
        const values = data.prompts.map(prompt => [
          prompt.id,
          prompt.title,
          prompt.category || '',
          prompt.tags || '',
          prompt.content.substring(0, 500) + '...',  // 預覽
          prompt.created_at,
          prompt.usage_count || 0,
          prompt.rating || 0
        ]);

        promptsSheet.getRange(2, 1, values.length, values[0].length).setValues(values);

        SpreadsheetApp.getUi().alert(`成功同步 ${data.prompts.length} 個提示詞！`);
      } else {
        SpreadsheetApp.getUi().alert('沒有可同步的提示詞');
      }
    } else {
      throw new Error(`API 錯誤: ${response.getResponseCode()}`);
    }

  } catch (error) {
    Logger.log('同步失敗: ' + error);
    SpreadsheetApp.getUi().alert('同步失敗: ' + error.message);
  }
}

/**
 * 刷新統計資料
 */
function refreshAnalytics() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const analyticsSheet = getOrCreateSheet(ss, CONFIG.SHEET_NAMES.ANALYTICS);
  const promptsSheet = ss.getSheetByName(CONFIG.SHEET_NAMES.PROMPTS);

  if (!promptsSheet) {
    SpreadsheetApp.getUi().alert('請先同步提示詞！');
    return;
  }

  try {
    // 取得資料
    const data = promptsSheet.getDataRange().getValues();
    const headers = data[0];
    const rows = data.slice(1);

    if (rows.length === 0) {
      SpreadsheetApp.getUi().alert('沒有資料可分析');
      return;
    }

    // 計算統計
    const totalPrompts = rows.length;
    const categoryIndex = headers.indexOf('分類');
    const usageIndex = headers.indexOf('使用次數');
    const ratingIndex = headers.indexOf('評分');

    // 分類統計
    const categoryStats = {};
    let totalUsage = 0;
    let totalRating = 0;
    let ratedCount = 0;

    rows.forEach(row => {
      const category = row[categoryIndex] || '未分類';
      categoryStats[category] = (categoryStats[category] || 0) + 1;

      totalUsage += row[usageIndex] || 0;

      if (row[ratingIndex] > 0) {
        totalRating += row[ratingIndex];
        ratedCount++;
      }
    });

    const avgRating = ratedCount > 0 ? (totalRating / ratedCount).toFixed(2) : 0;

    // 寫入統計
    analyticsSheet.clear();
    analyticsSheet.appendRow(['統計項目', '數值']);
    analyticsSheet.appendRow(['總提示詞數', totalPrompts]);
    analyticsSheet.appendRow(['總使用次數', totalUsage]);
    analyticsSheet.appendRow(['平均評分', avgRating]);
    analyticsSheet.appendRow(['']);
    analyticsSheet.appendRow(['分類', '數量']);

    Object.keys(categoryStats).forEach(category => {
      analyticsSheet.appendRow([category, categoryStats[category]]);
    });

    // 格式化
    analyticsSheet.getRange(1, 1, 1, 2).setFontWeight('bold').setBackground('#4285f4').setFontColor('#ffffff');

    SpreadsheetApp.getUi().alert('統計已更新！');

  } catch (error) {
    Logger.log('刷新統計失敗: ' + error);
    SpreadsheetApp.getUi().alert('刷新統計失敗: ' + error.message);
  }
}

/**
 * 顯示 API 設定對話框
 */
function showApiSettings() {
  const html = HtmlService.createHtmlOutput(`
    <style>
      body { font-family: Arial, sans-serif; padding: 20px; }
      .form-group { margin-bottom: 15px; }
      label { display: block; margin-bottom: 5px; font-weight: bold; }
      input { width: 100%; padding: 8px; box-sizing: border-box; }
      button { background: #4285f4; color: white; border: none; padding: 10px 20px; cursor: pointer; }
      button:hover { background: #357ae8; }
    </style>
    <div class="form-group">
      <label>API 基礎 URL:</label>
      <input type="text" id="api-url" value="${CONFIG.API_BASE_URL}" />
    </div>
    <button onclick="saveSettings()">儲存設定</button>
    <script>
      function saveSettings() {
        const apiUrl = document.getElementById('api-url').value;
        google.script.run
          .withSuccessHandler(() => {
            alert('設定已儲存！');
            google.script.host.close();
          })
          .withFailureHandler((error) => {
            alert('儲存失敗: ' + error);
          })
          .saveApiUrl(apiUrl);
      }
    </script>
  `).setWidth(400).setHeight(200);

  SpreadsheetApp.getUi().showModalDialog(html, 'API 設定');
}

/**
 * 儲存 API URL
 */
function saveApiUrl(url) {
  const scriptProperties = PropertiesService.getScriptProperties();
  scriptProperties.setProperty('API_BASE_URL', url);
  CONFIG.API_BASE_URL = url;
}

// ============================================================================
// 工具函數
// ============================================================================

/**
 * 取得或建立工作表
 */
function getOrCreateSheet(ss, sheetName) {
  let sheet = ss.getSheetByName(sheetName);

  if (!sheet) {
    sheet = ss.insertSheet(sheetName);

    // 根據工作表類型設定標題
    if (sheetName === CONFIG.SHEET_NAMES.PROMPTS) {
      sheet.appendRow(['ID', '標題', '分類', '標籤', '內容預覽', '建立時間', '使用次數', '評分']);
      sheet.getRange(1, 1, 1, 8).setFontWeight('bold').setBackground('#4285f4').setFontColor('#ffffff');
    } else if (sheetName === CONFIG.SHEET_NAMES.HISTORY) {
      sheet.appendRow(['ID', '使用者輸入', 'AI 模型', '建立時間', '已匯出']);
      sheet.getRange(1, 1, 1, 5).setFontWeight('bold').setBackground('#34a853').setFontColor('#ffffff');
    } else if (sheetName === CONFIG.SHEET_NAMES.ANALYTICS) {
      sheet.appendRow(['統計項目', '數值']);
      sheet.getRange(1, 1, 1, 2).setFontWeight('bold').setBackground('#fbbc04').setFontColor('#ffffff');
    }

    // 自動調整欄寬
    sheet.autoResizeColumns(1, sheet.getLastColumn());
  }

  return sheet;
}

/**
 * 初始化工作表
 */
function initializeSheets() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();

  getOrCreateSheet(ss, CONFIG.SHEET_NAMES.PROMPTS);
  getOrCreateSheet(ss, CONFIG.SHEET_NAMES.HISTORY);
  getOrCreateSheet(ss, CONFIG.SHEET_NAMES.ANALYTICS);

  SpreadsheetApp.getUi().alert('工作表初始化完成！');
}

// ============================================================================
// 定時觸發器（可選）
// ============================================================================

/**
 * 建立每小時同步的觸發器
 */
function createHourlyTrigger() {
  // 刪除現有觸發器
  const triggers = ScriptApp.getProjectTriggers();
  triggers.forEach(trigger => {
    if (trigger.getHandlerFunction() === 'syncPromptsFromPlatform') {
      ScriptApp.deleteTrigger(trigger);
    }
  });

  // 建立新觸發器
  ScriptApp.newTrigger('syncPromptsFromPlatform')
    .timeBased()
    .everyHours(1)
    .create();

  SpreadsheetApp.getUi().alert('已設定每小時自動同步！');
}

/**
 * 刪除所有觸發器
 */
function deleteAllTriggers() {
  const triggers = ScriptApp.getProjectTriggers();
  triggers.forEach(trigger => ScriptApp.deleteTrigger(trigger));
  SpreadsheetApp.getUi().alert('所有觸發器已刪除！');
}
