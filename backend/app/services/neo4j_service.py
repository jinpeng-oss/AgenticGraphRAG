from neo4j import GraphDatabase, Driver
from app.core.config import settings
from app.core.logger import logger

class Neo4jManager:
    _driver: Driver = None

    def __init__(self):
        """初始化连接，但保持单例逻辑"""
        self.uri = settings.NEO4J_URI
        self.user = settings.NEO4J_USERNAME
        self.password = settings.NEO4J_PASSWORD
        self._connect()

    def _connect(self):
        """内部连接方法"""
        try:
            self._driver = GraphDatabase.driver(
                self.uri, 
                auth=(self.user, self.password)
            )
            # 验证连接是否真正通了 (verify_connectivity 会抛异常如果连不上)
            self._driver.verify_connectivity()
            logger.success(f"✅ Neo4j 连接成功: {self.uri}")
        except Exception as e:
            logger.error(f"❌ Neo4j 连接失败: {e}")
            raise e

    def close(self):
        """关闭连接"""
        if self._driver:
            self._driver.close()
            logger.info("Neo4j 连接已关闭")

    def execute_query(self, query: str, parameters: dict = None):
        """
        执行 Cypher 查询的通用方法
        :param query: Cypher 语句
        :param parameters: 参数字典
        :return: 查询结果列表
        """
        if not self._driver:
            logger.error("驱动未初始化，尝试重新连接...")
            self._connect()
            
        try:
            result = self._driver.execute_query(
                query, 
                parameters_=parameters,
                database_="neo4j"
            )
            return result.records
        except Exception as e:
            logger.exception(f"查询执行出错: {query}")
            raise e

try:
    neo4j_manager = Neo4jManager()
except Exception:
    neo4j_manager = None 

if __name__ == "__main__":
    if neo4j_manager:
        logger.info("开始测试查询...")
        cql = "MERGE (t:TestNode {message: 'Hello World'}) RETURN t.message AS msg"
        records = neo4j_manager.execute_query(cql)
        print(f"查询结果: {records[0]['msg']}")
        neo4j_manager.close()