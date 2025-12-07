import asyncio
from langchain_core.messages import HumanMessage
from app.core.graph import app

async def test_full_flow():
    # 模拟用户 session
    config = {"configurable": {"thread_id": "test_user_007"}}
    
    # 📝 测试 1: 正常问题
    query = "马斯克的太空公司是什么"
    print(f"\n{'='*50}\n🧠 用户提问: {query}\n{'='*50}")
    
    inputs = {
        "query": query,
        "messages": [HumanMessage(content=query)]
    }
    
    # 流式运行，查看每个步骤
    async for event in app.astream(inputs, config=config):
        for node, values in event.items():
            print(f"✅ 节点完成: [{node}]")
            if node == "validate":
                print(f"   👉 校验状态: {values.get('validation_status')}")
                print(f"   👉 校验理由: {values.get('validation_reason')}")
    
    # 获取最终记忆
    state = await app.aget_state(config)
    print(f"\n🤖 最终回答: {state.values['answer']}")
    
    # 📝 测试 2: 追问 (测试记忆)
    query2 = "它有什么著名的火箭？"
    print(f"\n{'='*50}\n🧠 用户追问: {query2}\n{'='*50}")
    
    inputs2 = {
        "query": query2,
        "messages": [HumanMessage(content=query2)]
    }
    
    async for event in app.astream(inputs2, config=config):
        pass # 简略输出
        
    state2 = await app.aget_state(config)
    print(f"\n🤖 最终回答: {state2.values['answer']}")

if __name__ == "__main__":
    asyncio.run(test_full_flow())