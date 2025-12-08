from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from app.core.logger import logger
from app.api.endpoints import router as chat_router

# ✅ 引入初始化函数
from app.services.hybrid_search import init_hybrid_search

# 定义生命周期管理器
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 🟢 启动时执行：初始化服务
    logger.info("🔄 正在初始化核心服务...")
    init_hybrid_search()
    yield
    # 🔴 关闭时执行（可选）：清理资源
    logger.info("🛑 服务正在关闭...")

# 初始化 FastAPI (挂载 lifespan)
app = FastAPI(
    title="Agentic GraphRAG API",
    lifespan=lifespan, # 👈 关键点
    version="1.0.0"
)

# ... 后面的 CORS 和路由配置保持不变 ...
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router, prefix="/api/v1")

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)