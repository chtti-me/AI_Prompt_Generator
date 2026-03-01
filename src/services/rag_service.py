"""
RAG (Retrieval-Augmented Generation) 知識庫服務
"""

import logging
from typing import List, Dict, Optional
from pathlib import Path
from config import config

logger = logging.getLogger(__name__)

# 嘗試匯入 ChromaDB，如果失敗則標記為不可用
CHROMADB_AVAILABLE = False
try:
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except Exception as e:
    logger.warning(f"ChromaDB 無法匯入（可能與 Python 3.14 不相容）: {e}")
    logger.warning("RAG 功能將被禁用，但應用程式仍可正常運行")

# 嘗試匯入 SentenceTransformer
SENTENCE_TRANSFORMER_AVAILABLE = False
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMER_AVAILABLE = True
except Exception as e:
    logger.warning(f"SentenceTransformer 無法匯入: {e}")


class RAGService:
    """RAG 知識庫服務"""

    def __init__(self):
        """初始化 RAG 服務"""
        self.available = False
        self.client = None
        self.collection = None
        self.embedding_model = None

        # 檢查 ChromaDB 是否可用
        if not CHROMADB_AVAILABLE:
            logger.error("ChromaDB 不可用，RAG 服務無法初始化")
            logger.error("建議：使用 Python 3.12 或 3.13 以獲得完整的 RAG 功能支援")
            return

        try:
            # 初始化 ChromaDB
            self.client = chromadb.Client(Settings(
                persist_directory=config.CHROMA_PERSIST_DIRECTORY,
                anonymized_telemetry=False
            ))

            # 取得或建立 collection
            self.collection = self.client.get_or_create_collection(
                name=config.CHROMA_COLLECTION_NAME,
                metadata={"description": "Prompt templates library"}
            )

            # 初始化嵌入模型
            if config.EMBEDDING_PROVIDER == 'sentence-transformers' and SENTENCE_TRANSFORMER_AVAILABLE:
                self.embedding_model = SentenceTransformer(config.SENTENCE_TRANSFORMER_MODEL)
                logger.info(f"已載入 Sentence Transformer: {config.SENTENCE_TRANSFORMER_MODEL}")
            else:
                self.embedding_model = None
                logger.warning("嵌入模型不可用")

            self.available = True
            logger.info("RAG 服務已初始化")

        except Exception as e:
            logger.error(f"RAG 服務初始化失敗: {e}")
            logger.error("RAG 功能將被禁用，但應用程式仍可正常運行")
            self.available = False

    def add_document(self, doc_id: str, content: str, metadata: Dict = None) -> bool:
        """
        新增文件到知識庫

        Args:
            doc_id: 文件唯一 ID
            content: 文件內容
            metadata: 文件元資料

        Returns:
            是否成功
        """
        if not self.available:
            logger.error("RAG 服務不可用，無法新增文件")
            return False

        try:
            # 分段處理
            chunks = self._chunk_text(content)

            # 生成嵌入
            embeddings = self._get_embeddings(chunks)

            # 建立 chunk IDs
            chunk_ids = [f"{doc_id}_chunk_{i}" for i in range(len(chunks))]

            # 準備 metadata
            metadatas = []
            for i in range(len(chunks)):
                chunk_metadata = {
                    'doc_id': doc_id,
                    'chunk_index': i,
                    'total_chunks': len(chunks)
                }
                if metadata:
                    chunk_metadata.update(metadata)
                metadatas.append(chunk_metadata)

            # 新增到 ChromaDB
            self.collection.add(
                ids=chunk_ids,
                embeddings=embeddings,
                documents=chunks,
                metadatas=metadatas
            )

            logger.info(f"文件已新增: {doc_id} ({len(chunks)} chunks)")
            return True

        except Exception as e:
            logger.error(f"新增文件失敗: {e}")
            return False

    def search(self, query: str, top_k: int = None) -> List[Dict]:
        """
        語義搜尋

        Args:
            query: 查詢文本
            top_k: 返回前 K 個結果

        Returns:
            搜尋結果列表
        """
        if not self.available:
            logger.error("RAG 服務不可用，無法執行搜尋")
            return []

        if top_k is None:
            top_k = config.RAG_TOP_K

        try:
            # 生成查詢嵌入
            query_embedding = self._get_embeddings([query])[0]

            # 搜尋
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k
            )

            # 格式化結果
            formatted_results = []
            if results['documents']:
                for i in range(len(results['documents'][0])):
                    formatted_results.append({
                        'id': results['ids'][0][i],
                        'content': results['documents'][0][i],
                        'metadata': results['metadatas'][0][i] if results['metadatas'] else {},
                        'distance': results['distances'][0][i] if results['distances'] else 0
                    })

            return formatted_results

        except Exception as e:
            logger.error(f"搜尋失敗: {e}")
            return []

    def delete_document(self, doc_id: str) -> bool:
        """
        刪除文件

        Args:
            doc_id: 文件 ID

        Returns:
            是否成功
        """
        if not self.available:
            logger.error("RAG 服務不可用，無法刪除文件")
            return False

        try:
            # 查找所有相關的 chunks
            results = self.collection.get(
                where={"doc_id": doc_id}
            )

            if results['ids']:
                self.collection.delete(ids=results['ids'])
                logger.info(f"文件已刪除: {doc_id}")
                return True
            else:
                logger.warning(f"找不到文件: {doc_id}")
                return False

        except Exception as e:
            logger.error(f"刪除文件失敗: {e}")
            return False

    def get_all_documents(self) -> List[Dict]:
        """取得所有文件列表"""
        if not self.available:
            logger.error("RAG 服務不可用，無法取得文件列表")
            return []

        try:
            results = self.collection.get()

            # 按 doc_id 分組
            docs = {}
            for i, doc_id in enumerate(results['ids']):
                metadata = results['metadatas'][i] if results['metadatas'] else {}
                original_doc_id = metadata.get('doc_id', doc_id)

                if original_doc_id not in docs:
                    docs[original_doc_id] = {
                        'id': original_doc_id,
                        'chunks': 0,
                        'metadata': metadata
                    }
                docs[original_doc_id]['chunks'] += 1

            return list(docs.values())

        except Exception as e:
            logger.error(f"取得文件列表失敗: {e}")
            return []

    def _chunk_text(self, text: str) -> List[str]:
        """
        將文本分段

        Args:
            text: 原始文本

        Returns:
            分段後的文本列表
        """
        chunk_size = config.RAG_CHUNK_SIZE
        chunk_overlap = config.RAG_CHUNK_OVERLAP

        chunks = []
        start = 0
        text_length = len(text)

        while start < text_length:
            end = start + chunk_size
            chunk = text[start:end]
            chunks.append(chunk)
            start = end - chunk_overlap

        return chunks

    def _get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        取得文本嵌入向量

        Args:
            texts: 文本列表

        Returns:
            嵌入向量列表
        """
        if self.embedding_model:
            # 使用 Sentence Transformer
            embeddings = self.embedding_model.encode(texts, show_progress_bar=False)
            return embeddings.tolist()
        else:
            # 如果沒有模型，返回空向量（不應發生）
            logger.error("沒有可用的嵌入模型")
            return [[0.0] * 384 for _ in texts]  # 預設維度

    def get_stats(self) -> Dict:
        """取得統計資訊"""
        if not self.available:
            return {
                'total_chunks': 0,
                'available': False,
                'error': 'RAG 服務不可用'
            }

        try:
            count = self.collection.count()
            return {
                'total_chunks': count,
                'collection_name': config.CHROMA_COLLECTION_NAME,
                'available': True
            }
        except Exception as e:
            logger.error(f"取得統計失敗: {e}")
            return {
                'total_chunks': 0,
                'available': False,
                'error': str(e)
            }
