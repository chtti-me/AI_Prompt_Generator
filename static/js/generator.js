/**
 * 提示詞生成器頁面邏輯
 */

let currentGeneratedContent = '';

// 頁面載入
document.addEventListener('DOMContentLoaded', function() {
    initGeneratorPage();
});

function initGeneratorPage() {
    const form = document.getElementById('generator-form');
    const useAICheckbox = document.getElementById('use-ai');
    const aiProviderSection = document.getElementById('ai-provider-section');
    const copyBtn = document.getElementById('copy-btn');
    const downloadBtn = document.getElementById('download-btn');
    const optimizeBtn = document.getElementById('optimize-btn');

    // 監聽 AI 選項變化
    if (useAICheckbox) {
        useAICheckbox.addEventListener('change', function() {
            aiProviderSection.style.display = this.checked ? 'block' : 'none';
        });
    }

    // 表單提交
    if (form) {
        form.addEventListener('submit', handleGenerate);
    }

    // 複製按鈕
    if (copyBtn) {
        copyBtn.addEventListener('click', function() {
            copyToClipboard(currentGeneratedContent);
        });
    }

    // 下載按鈕
    if (downloadBtn) {
        downloadBtn.addEventListener('click', function() {
            const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, -5);
            const filename = `prompt_${timestamp}.md`;
            downloadAsFile(currentGeneratedContent, filename);
        });
    }

    // 優化按鈕
    if (optimizeBtn) {
        optimizeBtn.addEventListener('click', handleOptimize);
    }
}

async function handleGenerate(e) {
    e.preventDefault();

    // 取得表單資料
    const formData = getFormData();

    // 顯示載入中
    showLoading(true);

    try {
        const result = await apiRequest('/generate', 'POST', formData);

        if (result.success) {
            currentGeneratedContent = result.content;
            displayResult(result.content);
            showNotification('提示詞生成成功！', 'success');

            // 啟用按鈕
            enableButtons();
        } else {
            throw new Error(result.error || '生成失敗');
        }
    } catch (error) {
        showNotification(`生成失敗: ${error.message}`, 'danger');
    } finally {
        showLoading(false);
    }
}

async function handleOptimize() {
    if (!currentGeneratedContent) {
        showNotification('沒有可優化的內容', 'warning');
        return;
    }

    showLoading(true);

    try {
        const provider = document.getElementById('ai-provider').value;
        const result = await apiRequest('/optimize', 'POST', {
            prompt: currentGeneratedContent,
            provider: provider
        });

        if (result.success) {
            currentGeneratedContent = result.optimized;
            displayResult(result.optimized);

            // 顯示優化建議
            if (result.suggestions && result.suggestions.length > 0) {
                displaySuggestions(result.suggestions);
            }

            showNotification('提示詞已優化！', 'success');
        } else {
            throw new Error(result.error || '優化失敗');
        }
    } catch (error) {
        showNotification(`優化失敗: ${error.message}`, 'danger');
    } finally {
        showLoading(false);
    }
}

function getFormData() {
    // 取得已選擇的功能
    const features = [];
    document.querySelectorAll('#features-checkboxes input:checked').forEach(checkbox => {
        features.push(checkbox.value);
    });

    return {
        project_type: document.getElementById('project-type').value,
        features: features,
        detail_level: document.getElementById('detail-level').value,
        language: document.getElementById('language').value,
        target_platform: document.getElementById('target-platform').value,
        additional_requirements: document.getElementById('additional-requirements').value,
        use_ai: document.getElementById('use-ai').checked,
        ai_provider: document.getElementById('ai-provider').value
    };
}

function displayResult(content) {
    const initialMessage = document.getElementById('initial-message');
    const resultContainer = document.getElementById('result-container');
    const resultPreview = document.getElementById('result-preview');
    const resultRaw = document.getElementById('result-raw');

    // 隱藏初始訊息
    if (initialMessage) {
        initialMessage.style.display = 'none';
    }

    // 顯示結果
    if (resultContainer) {
        resultContainer.style.display = 'block';
    }

    // 渲染 Markdown
    if (resultPreview) {
        resultPreview.innerHTML = renderMarkdown(content);
    }

    // 儲存原始內容
    if (resultRaw) {
        resultRaw.value = content;
    }
}

function displaySuggestions(suggestions) {
    const suggestionsContainer = document.getElementById('optimization-suggestions');
    const suggestionsList = document.getElementById('suggestions-list');

    if (!suggestionsContainer || !suggestionsList) return;

    // 清空並填充建議
    suggestionsList.innerHTML = '';
    suggestions.forEach(suggestion => {
        const li = document.createElement('li');
        li.textContent = suggestion;
        suggestionsList.appendChild(li);
    });

    suggestionsContainer.style.display = 'block';
}

function showLoading(show) {
    const spinner = document.getElementById('loading-spinner');
    const generateBtn = document.getElementById('generate-btn');

    if (spinner) {
        spinner.style.display = show ? 'block' : 'none';
    }

    if (generateBtn) {
        generateBtn.disabled = show;
        if (show) {
            generateBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 生成中...';
        } else {
            generateBtn.innerHTML = '<i class="fas fa-magic"></i> 生成提示詞';
        }
    }
}

function enableButtons() {
    document.getElementById('copy-btn').disabled = false;
    document.getElementById('download-btn').disabled = false;
    document.getElementById('optimize-btn').disabled = false;
}
