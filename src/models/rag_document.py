"""
RAG 文件資料模型
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class RAGDocument(Base):
    """RAG 文件資料表"""

    __tablename__ = 'rag_documents'

    id = Column(Integer, primary_key=True, autoincrement=True)
    filename = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    vector_id = Column(String(100), index=True)  # ChromaDB/FAISS 的文件 ID
    uploaded_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    file_size = Column(Integer)  # bytes
    chunk_count = Column(Integer, default=0)  # 分段數量
    file_type = Column(String(20))  # txt, md, pdf, docx

    def to_dict(self):
        """轉換為字典"""
        return {
            'id': self.id,
            'filename': self.filename,
            'content_preview': self.content[:200] + '...' if len(self.content) > 200 else self.content,
            'vector_id': self.vector_id,
            'uploaded_at': self.uploaded_at.isoformat() if self.uploaded_at else None,
            'file_size': self.file_size,
            'chunk_count': self.chunk_count,
            'file_type': self.file_type
        }

    def __repr__(self):
        return f"<RAGDocument(id={self.id}, filename='{self.filename}', type='{self.file_type}')>"
