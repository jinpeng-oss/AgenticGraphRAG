from qdrant_client import QdrantClient
from qdrant_client.http import models
from app.core.config import settings
from app.core.logger import logger

class QdrantManager:
    _client: QdrantClient = None

    def __init__(self):
        self.url = settings.QDRANT_URL
        self.api_key = settings.QDRANT_API_KEY
        self._connect()

    def _connect(self):
        try:
            if self.api_key:
                self._client = QdrantClient(url=self.url, api_key=self.api_key)
            else:
                self._client = QdrantClient(path=self.url) if not self.url.startswith("http") else QdrantClient(url=self.url)
            
            logger.success(f"✅ Qdrant 客户端初始化成功: {self.url}")
        except Exception as e:
            logger.error(f"❌ Qdrant 初始化失败: {e}")
            raise e

    def get_client(self) -> QdrantClient:
        """获取原生客户端，方便给 LangChain 使用"""
        return self._client

    def create_collection_if_not_exists(self, collection_name: str, vector_size: int = 4096):
        """
        创建一个集合 (类似 SQL 的 Table)
        vector_size: 向量维度
        """
        if not self._client.collection_exists(collection_name):
            self._client.create_collection(
                collection_name=collection_name,
                vectors_config=models.VectorParams(
                    size=vector_size, 
                    distance=models.Distance.COSINE
                )
            )
            logger.info(f"已创建新集合: {collection_name}")
        else:
            logger.info(f"集合已存在: {collection_name}")

    def search(self, collection_name: str, query_vector: list, limit: int = 5):
        """基础搜索封装"""
        return self._client.search(
            collection_name=collection_name,
            query_vector=query_vector,
            limit=limit
        )

# --- 单例导出 ---
try:
    qdrant_manager = QdrantManager()
except Exception:
    qdrant_manager = None

# --- 测试代码 ---
if __name__ == "__main__":
    # 使用 python -m app.services.qdrant_service 运行
    if qdrant_manager:
        # 测试创建一个集合
        test_col = "test_collection"
        qdrant_manager.create_collection_if_not_exists(test_col, vector_size=4)
        print("测试完成，查看 logs 目录下的日志以确认详情。")