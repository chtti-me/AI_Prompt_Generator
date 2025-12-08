"""
AI Prompt Generator Platform - 配置管理模組
載入環境變數並提供應用配置
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# 載入 .env 檔案
load_dotenv()

# 基礎路徑
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
UPLOAD_DIR = DATA_DIR / "uploads"
VECTOR_STORE_DIR = DATA_DIR / "vector_store"
LOGS_DIR = BASE_DIR / "logs"

# 確保目錄存在
DATA_DIR.mkdir(exist_ok=True)
UPLOAD_DIR.mkdir(exist_ok=True)
VECTOR_STORE_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)


class Config:
    """應用配置類"""

    # Flask 配置
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', 5001))

    # AI 服務配置
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4')
    OPENAI_EMBEDDING_MODEL = os.getenv('OPENAI_EMBEDDING_MODEL', 'text-embedding-3-small')

    GOOGLE_AI_API_KEY = os.getenv('GOOGLE_AI_API_KEY')
    GEMINI_MODEL = os.getenv('GEMINI_MODEL', 'gemini-2.5-flash')
    GEMINI_PRO_MODEL = os.getenv('GEMINI_PRO_MODEL', 'gemini-2.5-pro')

    AI_PROVIDER = os.getenv('AI_PROVIDER', 'both')  # openai, gemini, both
    DEFAULT_AI_PROVIDER = os.getenv('DEFAULT_AI_PROVIDER', 'gemini')

    # RAG 配置
    VECTOR_DB_TYPE = os.getenv('VECTOR_DB_TYPE', 'chromadb')
    CHROMA_PERSIST_DIRECTORY = str(VECTOR_STORE_DIR)
    CHROMA_COLLECTION_NAME = os.getenv('CHROMA_COLLECTION_NAME', 'prompt_library')

    EMBEDDING_PROVIDER = os.getenv('EMBEDDING_PROVIDER', 'sentence-transformers')
    SENTENCE_TRANSFORMER_MODEL = os.getenv(
        'SENTENCE_TRANSFORMER_MODEL',
        'paraphrase-multilingual-MiniLM-L12-v2'
    )

    RAG_TOP_K = int(os.getenv('RAG_TOP_K', 5))
    RAG_SIMILARITY_THRESHOLD = float(os.getenv('RAG_SIMILARITY_THRESHOLD', 0.7))
    RAG_CHUNK_SIZE = int(os.getenv('RAG_CHUNK_SIZE', 500))
    RAG_CHUNK_OVERLAP = int(os.getenv('RAG_CHUNK_OVERLAP', 50))

    # Google Sheets 配置
    GOOGLE_SHEETS_ENABLED = os.getenv('GOOGLE_SHEETS_ENABLED', 'false').lower() == 'true'
    GOOGLE_SERVICE_ACCOUNT_FILE = os.getenv('GOOGLE_SERVICE_ACCOUNT_FILE')
    PROMPTS_SHEET_ID = os.getenv('PROMPTS_SHEET_ID')
    HISTORY_SHEET_ID = os.getenv('HISTORY_SHEET_ID')
    AUTO_SYNC_TO_SHEETS = os.getenv('AUTO_SYNC_TO_SHEETS', 'false').lower() == 'true'
    SYNC_INTERVAL_MINUTES = int(os.getenv('SYNC_INTERVAL_MINUTES', 30))

    # 資料庫配置
    DATABASE_URL = os.getenv('DATABASE_URL', f'sqlite:///{DATA_DIR}/prompts.db')

    # 檔案上傳配置
    UPLOAD_FOLDER = str(UPLOAD_DIR)
    ALLOWED_EXTENSIONS = set(os.getenv('ALLOWED_EXTENSIONS', 'txt,md,pdf,docx').split(','))
    MAX_FILE_SIZE_MB = int(os.getenv('MAX_FILE_SIZE_MB', 10))
    MAX_CONTENT_LENGTH = MAX_FILE_SIZE_MB * 1024 * 1024  # 轉換為 bytes

    # 功能開關
    ENABLE_RAG = os.getenv('ENABLE_RAG', 'true').lower() == 'true'
    ENABLE_AI_OPTIMIZATION = os.getenv('ENABLE_AI_OPTIMIZATION', 'true').lower() == 'true'
    ENABLE_ANALYTICS = os.getenv('ENABLE_ANALYTICS', 'true').lower() == 'true'
    ENABLE_EXPORT = os.getenv('ENABLE_EXPORT', 'true').lower() == 'true'

    # 日誌配置
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = str(LOGS_DIR / 'app.log')

    # 安全配置
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*')
    RATE_LIMIT_PER_MINUTE = int(os.getenv('RATE_LIMIT_PER_MINUTE', 60))
    SESSION_TIMEOUT_MINUTES = int(os.getenv('SESSION_TIMEOUT_MINUTES', 60))

    @classmethod
    def validate(cls):
        """驗證配置是否有效"""
        errors = []

        # 檢查 AI 服務配置
        if cls.AI_PROVIDER in ['openai', 'both'] and not cls.OPENAI_API_KEY:
            errors.append("OpenAI API Key 未設定")

        if cls.AI_PROVIDER in ['gemini', 'both'] and not cls.GOOGLE_AI_API_KEY:
            errors.append("Google AI API Key 未設定")

        if cls.AI_PROVIDER not in ['openai', 'gemini', 'both']:
            errors.append(f"無效的 AI_PROVIDER: {cls.AI_PROVIDER}")

        # 檢查 Google Sheets 配置
        if cls.GOOGLE_SHEETS_ENABLED:
            if not cls.GOOGLE_SERVICE_ACCOUNT_FILE:
                errors.append("Google Sheets 已啟用但未設定 Service Account 檔案")
            if not cls.PROMPTS_SHEET_ID:
                errors.append("Google Sheets 已啟用但未設定 Sheet ID")

        return errors

    @classmethod
    def get_ai_status(cls):
        """取得 AI 服務狀態"""
        return {
            'openai_available': bool(cls.OPENAI_API_KEY),
            'gemini_available': bool(cls.GOOGLE_AI_API_KEY),
            'provider': cls.AI_PROVIDER,
            'default_provider': cls.DEFAULT_AI_PROVIDER
        }


# 建立配置實例
config = Config()

# 驗證配置
config_errors = config.validate()
if config_errors:
    print("⚠️ 配置警告:")
    for error in config_errors:
        print(f"  - {error}")
    print("\n請檢查 .env 檔案配置")
