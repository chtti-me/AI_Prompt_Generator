"""
輸入驗證工具
"""

import os
import re
from pathlib import Path
from typing import Tuple


def validate_file(file, allowed_extensions: set, max_size_mb: int = 10) -> Tuple[bool, str]:
    """
    驗證上傳的檔案

    Args:
        file: 上傳的檔案物件
        allowed_extensions: 允許的副檔名集合
        max_size_mb: 最大檔案大小（MB）

    Returns:
        (is_valid, error_message)
    """
    # 檢查檔案是否存在
    if not file or not file.filename:
        return False, "沒有選擇檔案"

    # 檢查副檔名
    filename = file.filename.lower()
    file_ext = filename.rsplit('.', 1)[1] if '.' in filename else ''

    if file_ext not in allowed_extensions:
        return False, f"不支援的檔案類型: {file_ext}。允許的類型: {', '.join(allowed_extensions)}"

    # 檢查檔案大小
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)  # 重置檔案指針

    max_size_bytes = max_size_mb * 1024 * 1024
    if file_size > max_size_bytes:
        return False, f"檔案太大: {file_size / (1024 * 1024):.2f}MB。最大允許: {max_size_mb}MB"

    if file_size == 0:
        return False, "檔案是空的"

    return True, ""


def validate_api_key(api_key: str, provider: str = 'openai') -> Tuple[bool, str]:
    """
    驗證 API Key 格式

    Args:
        api_key: API Key 字串
        provider: 'openai' 或 'gemini'

    Returns:
        (is_valid, error_message)
    """
    if not api_key:
        return False, "API Key 不能為空"

    if provider == 'openai':
        # OpenAI API Key 格式: sk-proj-... 或 sk-...
        if not (api_key.startswith('sk-proj-') or api_key.startswith('sk-')):
            return False, "無效的 OpenAI API Key 格式（應以 sk- 開頭）"
        if len(api_key) < 40:
            return False, "OpenAI API Key 太短"

    elif provider == 'gemini':
        # Google AI Studio API Key 格式: AIzaSy...
        if not api_key.startswith('AIzaSy'):
            return False, "無效的 Google AI API Key 格式（應以 AIzaSy 開頭）"
        if len(api_key) < 30:
            return False, "Google AI API Key 太短"

    else:
        return False, f"未知的 provider: {provider}"

    return True, ""


def validate_prompt_title(title: str) -> Tuple[bool, str]:
    """驗證提示詞標題"""
    if not title or not title.strip():
        return False, "標題不能為空"

    if len(title) > 200:
        return False, "標題太長（最多 200 字元）"

    return True, ""


def validate_prompt_content(content: str) -> Tuple[bool, str]:
    """驗證提示詞內容"""
    if not content or not content.strip():
        return False, "內容不能為空"

    if len(content) < 10:
        return False, "內容太短（至少 10 字元）"

    if len(content) > 100000:
        return False, "內容太長（最多 100,000 字元）"

    return True, ""


def validate_category(category: str) -> Tuple[bool, str]:
    """驗證分類"""
    allowed_categories = [
        'development', 'teaching', 'marketing', 'writing',
        'analysis', 'creative', 'business', 'other'
    ]

    if category and category not in allowed_categories:
        return False, f"無效的分類。允許的分類: {', '.join(allowed_categories)}"

    return True, ""


def sanitize_filename(filename: str) -> str:
    """
    清理檔案名稱，移除不安全的字元

    Args:
        filename: 原始檔名

    Returns:
        清理後的檔名
    """
    # 移除路徑分隔符號
    filename = os.path.basename(filename)

    # 移除不安全的字元
    filename = re.sub(r'[^\w\s\-\.]', '', filename)

    # 移除多餘的空格
    filename = re.sub(r'\s+', '_', filename)

    # 限制長度
    name, ext = os.path.splitext(filename)
    if len(name) > 100:
        name = name[:100]
    filename = name + ext

    return filename


def validate_sheet_id(sheet_id: str) -> Tuple[bool, str]:
    """驗證 Google Sheet ID 格式"""
    if not sheet_id:
        return False, "Sheet ID 不能為空"

    # Google Sheet ID 通常是 44 字元的字母數字組合
    if not re.match(r'^[a-zA-Z0-9_-]{20,}$', sheet_id):
        return False, "無效的 Google Sheet ID 格式"

    return True, ""
