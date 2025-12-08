/**
 * AI Prompt Generator Platform - 主要 JavaScript
 */

// API 基礎 URL
const API_BASE = '/api';

// 通用 API 請求函數
async function apiRequest(endpoint, method = 'GET', data = null) {
    const options = {
        method,
        headers: {
            'Content-Type': 'application/json'
        }
    };

    if (data) {
        options.body = JSON.stringify(data);
    }

    try {
        const response = await fetch(`${API_BASE}${endpoint}`, options);
        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.error || '請求失敗');
        }

        return result;
    } catch (error) {
        console.error('API 請求錯誤:', error);
        throw error;
    }
}

// 顯示通知
function showNotification(message, type = 'info') {
    // 簡單的通知實作（可以替換為更好的 UI 庫）
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed top-0 end-0 m-3`;
    alertDiv.style.zIndex = '9999';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;

    document.body.appendChild(alertDiv);

    setTimeout(() => {
        alertDiv.remove();
    }, 5000);
}

// 複製到剪貼板
async function copyToClipboard(text) {
    try {
        await navigator.clipboard.writeText(text);
        showNotification('已複製到剪貼板！', 'success');
        return true;
    } catch (error) {
        console.error('複製失敗:', error);
        showNotification('複製失敗', 'danger');
        return false;
    }
}

// 下載文本為檔案
function downloadAsFile(content, filename, type = 'text/markdown') {
    const blob = new Blob([content], { type });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);

    showNotification(`檔案已下載: ${filename}`, 'success');
}

// 格式化日期時間
function formatDateTime(isoString) {
    const date = new Date(isoString);
    return date.toLocaleString('zh-TW');
}

// Markdown 渲染（使用 marked.js）
function renderMarkdown(markdown) {
    if (typeof marked !== 'undefined') {
        return marked.parse(markdown);
    }
    // Fallback: 簡單的換行處理
    return markdown.replace(/\n/g, '<br>');
}

// 全域錯誤處理
window.addEventListener('error', function(e) {
    console.error('全域錯誤:', e.error);
});

// 頁面載入完成
document.addEventListener('DOMContentLoaded', function() {
    console.log('AI Prompt Generator Platform 已載入');
});
