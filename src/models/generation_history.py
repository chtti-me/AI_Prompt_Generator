"""
生成歷史資料模型
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class GenerationHistory(Base):
    """生成歷史資料表"""

    __tablename__ = 'generation_history'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_input = Column(Text, nullable=False)  # 使用者的原始輸入
    ai_model = Column(String(50), nullable=False)  # 使用的 AI 模型
    generated_content = Column(Text, nullable=False)  # 生成的提示詞內容
    config = Column(JSON)  # 生成時的配置參數
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    exported = Column(Boolean, default=False)  # 是否已匯出
    prompt_id = Column(Integer)  # 關聯的提示詞 ID（如果已儲存）
    synced_to_sheets = Column(Boolean, default=False)  # 是否已同步到 Google Sheets

    def to_dict(self):
        """轉換為字典"""
        return {
            'id': self.id,
            'user_input': self.user_input,
            'ai_model': self.ai_model,
            'generated_content': self.generated_content,
            'config': self.config,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'exported': self.exported,
            'prompt_id': self.prompt_id,
            'synced_to_sheets': self.synced_to_sheets
        }

    def __repr__(self):
        return f"<GenerationHistory(id={self.id}, model='{self.ai_model}', created='{self.created_at}')>"
