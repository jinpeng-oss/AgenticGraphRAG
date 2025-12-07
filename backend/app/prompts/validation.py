from langchain_core.prompts import ChatPromptTemplate

# 校验回答的 Prompt
validation_prompt = ChatPromptTemplate.from_messages([
    ("system", """你是一个严格的评分员。你的任务是评估 AI 生成的[回答]是否准确地解决了用户的[问题]，并且是否忠实于[上下文]。

评估标准：
1. **相关性**: 回答是否直接回应了用户的问题？
2. **准确性**: 回答是否正确？有没有幻觉？
3. **可变通性**: 如果上下文没有相关信息，根据你的知识，回答是否合理？

请严格遵守以下 JSON 输出格式：
{format_instructions}
"""),

    ("user", """
【上下文】
{context}

【用户问题】
{question}

【AI 回答】
{answer}
""")
])