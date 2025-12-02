import sys
from pathlib import Path
from loguru import logger

# 1. 确定日志保存的路径: backend/logs/
# current_file: backend/core/logger.py
# .parent: backend/core
# .parent.parent: backend
BASE_DIR = Path(__file__).resolve().parent.parent
LOG_DIR = BASE_DIR / "logs"

# 自动创建 logs 文件夹（如果不存在）
LOG_DIR.mkdir(parents=True, exist_ok=True)

log_file_path = LOG_DIR / "app.log"

# 2. 移除默认的 handler（避免重复打印）
logger.remove()

# 3. 添加控制台输出 (开发环境用)
logger.add(
    sys.stderr,
    level="DEBUG", # 开发时设为 DEBUG，上线可改为 INFO
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
)

# 4. 添加文件输出 (生产环境用)
logger.add(
    log_file_path,
    rotation="10 MB",  # 每个文件超过 10MB 就自动分割，比如 app.log.1, app.log.2
    retention="10 days", # 只保留最近 10 天的日志
    compression="zip", # 旧日志自动压缩，节省空间
    level="INFO",      # 文件里只存 INFO 及以上级别，减少垃圾信息
    encoding="utf-8"
)

__all__ = ["logger"]