import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
from operator import itemgetter
import os

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_redis import RedisConfig, RedisVectorStore

# 假设你的 load_key 在 config 目录下
from config.load_key import load_key

# 页面配置
st.set_page_config(page_title="RAG PDF 问答", layout="centered")
st.title("📄 RAG PDF 智能问答系统")
st.markdown("基于2023政府工作报告/财报的问答演示（需要本地Redis服务运行）")

# 用户输入
query = st.text_input("请输入你的问题：", placeholder="例如：2023年营业收入是多少？")

if query:
    with st.spinner("检索中..."):
        # 1. 配置API Key
        if not os.environ.get("DASHSCOPE_API_KEY"):
            os.environ["DASHSCOPE_API_KEY"] = load_key("BAILIAN_API_KEY")

        # 2. 嵌入模型（与索引时一致）
        embedding_model = DashScopeEmbeddings(model="text-embedding-v3")

        # 3. 连接Redis向量库
        redis_url = "redis://localhost:6379"
        config = RedisConfig(index_name="maotai03", redis_url=redis_url)
        vector_store = RedisVectorStore(embedding_model, config=config)
        retriever = vector_store.as_retriever()


        # 4. 辅助函数：将检索到的文档片段合并为字符串
        def collect_documents(docs):
            return "\n".join([doc.page_content for doc in docs])


        # 5. 大模型（DeepSeek via 阿里云百炼）
        llm = ChatOpenAI(
            model="deepseek-v3",
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
            openai_api_key=load_key("BAILIAN_API_KEY"),
        )

        # 6. 提示词模板
        prompt_template = ChatPromptTemplate.from_messages([
            ("user", """你是一个答疑机器人，根据已知信息回答问题。
            已知信息：{context}
            问题：{question}
            如果已知信息不包含答案，请回复“无法回答”。""")
        ])

        # 7. RAG链
        chain = (
                {
                    "context": itemgetter("question") | retriever | collect_documents,
                    "question": itemgetter("question")
                }
                | prompt_template
                | llm
                | StrOutputParser()
        )

        # 8. 调用并显示结果
        response = chain.invoke({"question": query})
        st.success("回答：")
        st.write(response)