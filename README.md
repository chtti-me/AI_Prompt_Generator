# CH5｜AI Prompt 互動提示詞生成系統

<div align="center">

![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.0+-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

**智能提示詞生成平台 - 結合 AI 與 RAG 技術的完整解決方案**

[📊 完整課程簡報](slides/CH5_Overview.html) | [🎥 YouTube 頻道](https://www.youtube.com/@Liang-yt02) | [📘 Facebook](https://www.facebook.com/iddmail)

</div>

---

## 📋 本章節 Part 說明

| Part | 主題 | 說明 |
|------|------|------|
| [Part 1](slides/Part1_系統介紹與快速開始.html) | 系統介紹與快速開始 | 體驗提示詞生成平台，了解系統四大核心功能 |
| [Part 2](slides/Part2_專案架構與服務設計.html) | 專案架構與服務設計 | 深入了解 Flask 應用架構、分層設計與核心服務模組 |
| [Part 3](slides/Part3_互動式提示詞生成器.html) | 互動式提示詞生成器 | 問卷設計邏輯、模板系統與 AI 智能生成實作 |
| [Part 4](slides/Part4_RAG知識庫功能.html) | RAG 知識庫功能 | 文件上傳、向量嵌入、語義搜尋與知識增強生成 |
| [Part 5](slides/Part5_Google_Sheets整合.html) | Google Sheets 整合 | Service Account 設定、Apps Script 與團隊協作 |
| [Part 6](slides/Part6_疑難排解與效能優化.html) | 疑難排解與效能優化 | 常見問題解決方案與系統效能調校 |
| [Part 7](slides/Part7_進階擴展與客製化.html) | 進階擴展與客製化 | 自訂模板、整合新 AI 服務與 UI 客製化 |

---

## ✨ 功能特色

### 🎯 核心功能

- **互動式問卷生成器**：透過填寫問卷自動生成專業級提示詞
- **模板生成系統**：內建五種專案類型模板，快速產出標準化提示詞
- **AI 智能生成**：整合 OpenAI GPT 與 Google Gemini，客製化生成內容
- **提示詞優化**：AI 分析並提供改進建議

### 📚 RAG 知識庫

- **多格式支援**：支援 TXT、Markdown、PDF、Word 文件上傳
- **語義搜尋**：基於 Sentence Transformers 的向量搜尋
- **知識增強生成**：結合知識庫範本提升 AI 生成品質

### ☁️ 雲端整合

- **Google Sheets 同步**：自動同步提示詞到雲端試算表
- **團隊協作**：支援評分、評論、分類管理
- **Apps Script 自動化**：自訂選單與定時同步

---

## 🚀 專案下載方式

### 方法一：Git Clone（推薦）

```bash
git clone https://github.com/ChatGPT3a01/CH5_AI_Prompt_Generator.git
cd CH5_AI_Prompt_Generator
```

### 方法二：下載 ZIP

1. 點擊本頁面右上角的 **Code** 按鈕
2. 選擇 **Download ZIP**
3. 解壓縮到您想要的目錄

---

## 📦 安裝方式 (Installation)

### 系統需求

- Python 3.12 或更高版本
- pip 套件管理器
- 網路連線（首次啟動需下載 AI 模型）

### Windows 使用者

```bash
# 1. 進入專案目錄
cd CH5_AI_Prompt_Generator

# 2. 執行自動安裝腳本
start_windows.bat
```

腳本會自動完成以下步驟：
- 建立虛擬環境
- 安裝所有依賴套件
- 複製環境變數範本
- 啟動 Flask 應用

### macOS / Linux 使用者

```bash
# 1. 進入專案目錄
cd CH5_AI_Prompt_Generator

# 2. 給予執行權限並執行
chmod +x start.sh
./start.sh
```

### 手動安裝

```bash
# 1. 建立虛擬環境
python -m venv venv

# 2. 啟動虛擬環境
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 3. 安裝依賴
pip install -r requirements.txt

# 4. 複製環境變數範本
cp .env.example .env

# 5. 啟動應用
python app.py
```

### 配置 API Key

編輯 `.env` 檔案，填入您的 API Key：

```env
# 使用 Google Gemini（推薦，免費額度較多）
GOOGLE_AI_API_KEY=AIzaSy-your-key-here
AI_PROVIDER=gemini
DEFAULT_AI_PROVIDER=gemini

# 或使用 OpenAI
OPENAI_API_KEY=sk-proj-your-key-here
AI_PROVIDER=openai
```

> 💡 **提示**：沒有 API Key 也可以使用系統，只是無法使用 AI 智能生成功能，模板生成功能完全可用。

---

## 🌐 佈署流程 (Deployment)

### 本地開發

```bash
# 啟動開發伺服器
python app.py

# 訪問
http://localhost:5001
```

### 使用 Docker

```bash
# 建構映像
docker build -t ai-prompt-generator .

# 執行容器
docker run -p 5001:5001 --env-file .env ai-prompt-generator
```

### 佈署到雲端平台

#### Google Cloud Run

```bash
# 建構並推送映像
gcloud builds submit --tag gcr.io/PROJECT_ID/ai-prompt-generator

# 部署
gcloud run deploy ai-prompt-generator \
  --image gcr.io/PROJECT_ID/ai-prompt-generator \
  --platform managed \
  --allow-unauthenticated
```

#### Heroku

```bash
heroku create your-app-name
heroku config:set GOOGLE_AI_API_KEY=your-key
git push heroku main
```

---

## 📖 教學補充

### 技術架構

```
CH5_AI_Prompt_Generator/
├── app.py                 # Flask 應用入口
├── config.py              # 配置管理
├── src/
│   ├── services/
│   │   ├── ai_service.py      # AI API 統一接口
│   │   ├── rag_service.py     # RAG 知識庫服務
│   │   └── prompt_builder.py  # 模板生成引擎
│   ├── models/            # 資料模型
│   └── utils/             # 工具模組
├── templates/             # Jinja2 模板
├── static/                # 靜態資源
├── data/                  # 資料儲存
└── gas/                   # Google Apps Script
```

### 核心技術原理

#### 1. 模板生成系統
- 樹狀模板結構：專案類型 → 功能模組 → 詳細程度
- 變數替換與條件邏輯
- 支援多語言模板

#### 2. AI 服務整合
- 統一抽象層支援 OpenAI 和 Gemini
- 智能生成與優化功能
- 錯誤處理與重試機制

#### 3. RAG 技術流程
```
文件上傳 → 文本分段 → 向量嵌入 → 儲存至 ChromaDB
    ↓
查詢輸入 → 向量化 → 相似度搜尋 → 返回相關片段
    ↓
增強生成 → 將檢索結果加入 AI prompt → 生成客製化內容
```

#### 4. 向量搜尋原理
- 使用 Sentence Transformers 模型進行文本嵌入
- 384 維向量表示（paraphrase-multilingual-MiniLM-L12-v2）
- 餘弦相似度計算語義相關性

### API 端點說明

| 端點 | 方法 | 說明 |
|------|------|------|
| `/` | GET | 首頁 - 互動式建置教學 |
| `/generator` | GET | 提示詞生成器頁面 |
| `/library` | GET | RAG 知識庫頁面 |
| `/api/generate` | POST | 生成提示詞 |
| `/api/optimize` | POST | 優化提示詞 |
| `/api/rag/search` | POST | RAG 語義搜尋 |
| `/api/rag/upload` | POST | 上傳文件到知識庫 |
| `/api/status` | GET | 取得系統狀態 |

### 常見問題

**Q: 首次啟動為什麼很慢？**
A: 系統需要下載 Sentence Transformers 模型（約 470MB），首次下載完成後會快取在本地。

**Q: 可以離線使用嗎？**
A: 模板生成功能可以離線使用，但 AI 智能生成需要網路連線呼叫 API。

**Q: 支援哪些文件格式？**
A: 支援 TXT、Markdown、PDF、DOCX 四種格式上傳到知識庫。

---

## 📁 專案結構

```
CH5_AI_Prompt_Generator/
├── app.py                 # Flask 主應用
├── config.py              # 配置管理
├── requirements.txt       # Python 依賴
├── start_windows.bat      # Windows 啟動腳本
├── start.sh               # Linux/macOS 啟動腳本
├── .env.example           # 環境變數範本
├── src/
│   ├── services/          # 服務層
│   ├── models/            # 資料模型
│   └── utils/             # 工具函數
├── templates/             # HTML 模板
├── static/                # CSS/JS 靜態檔案
├── data/                  # 資料庫與向量儲存
├── gas/                   # Google Apps Script
└── slides/                # 課程簡報
```

---

## 🤝 社群連結

- 📘 **Facebook**：[https://www.facebook.com/iddmail](https://www.facebook.com/iddmail)
- 🎥 **YouTube**：[https://www.youtube.com/@Liang-yt02](https://www.youtube.com/@Liang-yt02)

---

## 📄 授權

本專案採用 MIT 授權條款。

---

<div align="center">

© 2026 自己架設 AI - 零基礎到大師 | Made with 曾慶良(阿亮老師) ❤️

</div>
