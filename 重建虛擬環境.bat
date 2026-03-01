@echo off
chcp 65001 >nul
echo ========================================
echo 使用 Python 3.12 重建虛擬環境
echo ========================================
echo.

echo 步驟 1: 刪除舊的虛擬環境...
if exist venv (
    rmdir /s /q venv
    echo 舊虛擬環境已刪除
) else (
    echo 沒有找到舊虛擬環境
)
echo.

echo 步驟 2: 使用 Python 3.12 建立新虛擬環境...
py -3.12 -m venv venv
if %errorlevel% neq 0 (
    echo 錯誤：無法建立虛擬環境
    pause
    exit /b 1
)
echo 虛擬環境已建立
echo.

echo 步驟 3: 啟動虛擬環境並安裝套件...
call venv\Scripts\activate.bat
python --version
echo.

echo 步驟 4: 升級 pip...
python -m pip install --upgrade pip
echo.

echo 步驟 5: 安裝基本套件（Flask 等）...
pip install Flask==3.0.0 Flask-CORS==4.0.0 Flask-SocketIO==5.3.5
echo.

echo 步驟 6: 安裝其他必要套件...
pip install openai google-generativeai httpx python-dotenv requests validators SQLAlchemy
echo.

echo 步驟 7: 安裝 RAG 相關套件...
pip install chromadb==0.4.22 sentence-transformers python-docx PyPDF2 markdown beautifulsoup4
echo.

echo 步驟 8: 安裝 Google Sheets 相關套件...
pip install gspread google-auth-oauthlib
echo.

echo ========================================
echo 完成！虛擬環境已重建
echo ========================================
echo.
echo 現在可以執行：python app.py
echo.
pause
