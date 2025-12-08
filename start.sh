#!/bin/bash

# AI Prompt Generator Platform - 啟動腳本 (Linux/macOS)

echo "=========================================="
echo "  AI Prompt Generator Platform"
echo "=========================================="
echo ""

# 檢查 Python 版本
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python 版本: $python_version"

# 檢查虛擬環境
if [ ! -d "venv" ]; then
    echo ""
    echo "未找到虛擬環境，正在建立..."
    python3 -m venv venv
    echo "✓ 虛擬環境建立完成"
fi

# 啟動虛擬環境
echo ""
echo "啟動虛擬環境..."
source venv/bin/activate

# 檢查依賴
if [ ! -f "venv/lib/python*/site-packages/flask/__init__.py" ]; then
    echo ""
    echo "正在安裝依賴套件..."
    pip install -r requirements.txt
    echo "✓ 依賴安裝完成"
fi

# 檢查 .env 檔案
if [ ! -f ".env" ]; then
    echo ""
    echo "⚠️  未找到 .env 檔案"
    echo "正在複製 .env.example..."
    cp .env.example .env
    echo "✓ 請編輯 .env 檔案並填入您的 API Key"
    echo ""
    read -p "按 Enter 繼續啟動（或 Ctrl+C 取消）..."
fi

# 啟動應用
echo ""
echo "=========================================="
echo "正在啟動應用..."
echo "=========================================="
echo ""

python app.py
