from langchain_core.output_parsers import StrOutputParser
from typing import Dict, Any

from app.core.state import AgentState
from app.services.llm_factory import llm_factory
from app.prompts.generation import rag_generation_prompt
from app.core.logger import logger

# 初始化生成链
llm = llm_factory.get_llm(mode="smart")
chain = rag_generation_prompt | llm | StrOutputParser()

async def generation_node(state: AgentState) -> Dict[str, Any]:
    """
    🧠 生成节点
    注意：这里只生成内容，不更新 messages 历史，历史更新留给 Validation 节点。
    """
    logger.info("🧠 [GENERATION] 正在生成回答...")
    
    try:
        response = await chain.ainvoke({
            "context": state.get("rag_context", ""),
            "messages": state.get("messages", []),
            "question": state["query"]
        })
        
        logger.info(f"初步生成回答: {response[:50]}...")
        
        return {"answer": response}
        
    except Exception as e:
        logger.error(f"❌ [GENERATION] 失败: {e}")
        return {"answer": "抱歉，生成回答时出现错误。"}