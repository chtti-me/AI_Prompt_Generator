"""資料模型模組"""
from .prompt import Prompt
from .rag_document import RAGDocument
from .generation_history import GenerationHistory
from .user_config import UserConfig

__all__ = ['Prompt', 'RAGDocument', 'GenerationHistory', 'UserConfig']
