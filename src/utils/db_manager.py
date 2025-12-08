"""
資料庫管理工具
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base
from contextlib import contextmanager
import logging

logger = logging.getLogger(__name__)

Base = declarative_base()


class DatabaseManager:
    """資料庫管理器"""

    def __init__(self, database_url):
        """
        初始化資料庫管理器

        Args:
            database_url: 資料庫連接字串
        """
        self.engine = create_engine(
            database_url,
            echo=False,  # 設為 True 可查看 SQL 語句
            pool_pre_ping=True,  # 自動檢測連接有效性
            connect_args={'check_same_thread': False} if 'sqlite' in database_url else {}
        )

        # 建立 session factory
        session_factory = sessionmaker(bind=self.engine)
        self.Session = scoped_session(session_factory)

        logger.info(f"資料庫已連接: {database_url}")

    def create_tables(self):
        """建立所有資料表"""
        from src.models.prompt import Base as PromptBase
        from src.models.rag_document import Base as RAGDocumentBase
        from src.models.generation_history import Base as HistoryBase
        from src.models.user_config import Base as ConfigBase

        # 合併所有模型的 metadata
        bases = [PromptBase, RAGDocumentBase, HistoryBase, ConfigBase]
        for base in bases:
            base.metadata.create_all(self.engine)

        logger.info("資料表建立完成")

    def drop_tables(self):
        """刪除所有資料表（危險操作！）"""
        Base.metadata.drop_all(self.engine)
        logger.warning("所有資料表已刪除")

    @contextmanager
    def session_scope(self):
        """
        提供事務性的 session context manager

        使用方式:
            with db.session_scope() as session:
                session.add(obj)
                # 自動 commit，發生錯誤時自動 rollback
        """
        session = self.Session()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"資料庫操作失敗: {e}")
            raise
        finally:
            session.close()

    def get_session(self):
        """取得新的 session（需要手動管理）"""
        return self.Session()

    def close(self):
        """關閉資料庫連接"""
        self.Session.remove()
        self.engine.dispose()
        logger.info("資料庫連接已關閉")


# 全域資料庫實例（將在 app.py 中初始化）
db_manager = None


def init_db(database_url):
    """初始化資料庫"""
    global db_manager
    db_manager = DatabaseManager(database_url)
    db_manager.create_tables()
    return db_manager


def get_db():
    """取得資料庫管理器實例"""
    return db_manager
