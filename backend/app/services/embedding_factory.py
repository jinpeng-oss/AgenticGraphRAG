# app/services/embedding_factory.py
from langchain_openai import OpenAIEmbeddings
from langchain_core.embeddings import Embeddings
from app.core.config import settings
from app.core.logger import logger


class EmbeddingFactory:
    """
    嵌入模型工厂类
    用于创建和管理各种嵌入模型实例
    """
    
    @staticmethod
    def get_embedding() -> Embeddings:
        """
        获取嵌入模型实例
        
        Returns:
            Embeddings 实例 (用于向量化文本)
            
        Examples:
            >>> embeddings = EmbeddingFactory.get_embedding()
            >>> vectors = embeddings.embed_documents(["文本1", "文本2"])
        """
        
        # 1. API Key 检查
        if not settings.EMBD_API_KEY:
            logger.error("❌ 未找到 EMBD_API_KEY，请检查环境变量或 .env 配置")
            raise ValueError("EMBD_API_KEY is missing")

        try:
            # 2. 创建嵌入模型实例
            embeddings = OpenAIEmbeddings(
                base_url=settings.EMBD_BASE_URL,
                api_key=settings.EMBD_API_KEY,
                model=settings.EMBD_MODEL_NAME,
                dimensions=settings.EMBD_DIMENSIONS,
            )

            logger.success(
                f"✅ Embedding 已初始化 | Model: {settings.EMBD_MODEL_NAME}"
            )
            return embeddings

        except Exception as e:
            logger.error(f"❌ Embedding 初始化失败: {str(e)}")
            raise


embedding_factory = EmbeddingFactory()


if __name__ == "__main__":
    logger.info("🤖 开始测试 Embedding Factory...")

    try:
        logger.info("1️⃣ 初始化嵌入模型...")
        embeddings = EmbeddingFactory.get_embedding()
        logger.success("✅ Embedding 初始化成功")

        logger.info("2️⃣ 测试单个文本嵌入...")
        vector = embeddings.embed_query("你好，这是一个测试")
        logger.success(f"✅ 向量维度: {len(vector)}")

        logger.info("3️⃣ 测试批量文本嵌入...")
        vectors = embeddings.embed_documents(["文本1", "文本2", "文本3"])
        logger.success(f"✅ 批量嵌入成功，数量: {len(vectors)}")

        logger.success("🎉 所有测试通过！")

    except Exception as e:
        logger.error(f"❌ 测试失败: {e}")