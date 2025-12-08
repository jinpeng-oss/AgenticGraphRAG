from fastapi import APIRouter
from datetime import datetime
import os

# 导入服务模块 (使用模块导入方式避免 None 问题)
import app.services.neo4j_service as neo4j_svc
import app.services.qdrant_service as qdrant_svc
from app.services.llm_factory import llm_factory
from app.services.embedding_factory import embedding_factory
from app.api.schemas import SystemHealthResponse, ComponentStatus, ModelConfigInfo

router = APIRouter()

@router.get("/health", response_model=SystemHealthResponse)
async def get_system_health():
    """
    全系统健康检查 (Database + Services)
    """
    components = []
    has_error = False

    # 1. 检查 Neo4j
    neo4j_status = neo4j_svc.neo4j_manager.check_health()
    components.append(ComponentStatus(
        name="Neo4j Graph DB",
        status=neo4j_status.get("status", "down"),
        details=neo4j_status
    ))
    if neo4j_status.get("status") == "down": has_error = True

    # 2. 检查 Qdrant
    qdrant_status = qdrant_svc.qdrant_manager.check_health()
    components.append(ComponentStatus(
        name="Qdrant Vector DB",
        status=qdrant_status.get("status", "down"),
        details=qdrant_status
    ))
    if qdrant_status.get("status") == "down": has_error = True

    return SystemHealthResponse(
        timestamp=datetime.now().isoformat(),
        overall_status="unhealthy" if has_error else "healthy",
        components=components
    )

@router.get("/models")
async def get_model_configs():
    """
    获取当前加载的模型配置信息 (脱敏)
    """
    configs = []
    
    # 获取环境变量中的配置 (只读，不泄露 Key)
    # LLM Fast
    configs.append(ModelConfigInfo(
        model_type="LLM (Fast)",
        model_name=os.getenv("MODEL_FAST", "unknown"),
        provider=os.getenv("LLM_BASE_URL", "default"),
        parameters={"temperature": 0.0} # 假设值，或者去 factory 里读
    ))
    
    # LLM Smart
    configs.append(ModelConfigInfo(
        model_type="LLM (Smart)",
        model_name=os.getenv("MODEL_SMART", "unknown"),
        provider=os.getenv("LLM_BASE_URL", "default"),
        parameters={"temperature": 0.7}
    ))
    
    # Embedding
    # 获取 Embedding 维度 (需要实例化一下或者存个 config)
    emb_model = embedding_factory.get_embedding()
    # 尝试获取模型名 (不同厂商属性不同，这里是一个通用尝试)
    model_name = getattr(emb_model, "model", "unknown") 
    
    configs.append(ModelConfigInfo(
        model_type="Embedding",
        model_name=model_name,
        provider="HuggingFace/Local",
        parameters={"dimension": "Dynamic (checked on init)"}
    ))

    return {"models": configs}