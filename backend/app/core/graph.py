from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from app.core.state import AgentState
from app.core.nodes.retrieval import retrieve_node
from app.core.nodes.generation import generation_node
from app.core.nodes.validation import validation_node

# 1. 初始化
workflow = StateGraph(AgentState)

# 2. 添加节点
workflow.add_node("retrieve", retrieve_node)
workflow.add_node("generate", generation_node)
workflow.add_node("validate", validation_node)

# 3. 设置边 (线性结构)
workflow.set_entry_point("retrieve")
workflow.add_edge("retrieve", "generate")
workflow.add_edge("generate", "validate")
workflow.add_edge("validate", END)

# 4. 编译 (带记忆功能)
memory = MemorySaver()
app = workflow.compile(checkpointer=memory)

# 导出给 main.py 或测试脚本使用
__all__ = ["app"]