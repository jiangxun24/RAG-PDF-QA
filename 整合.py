from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_redis import RedisConfig, RedisVectorStore
from config.load_key import load_key
from operator import itemgetter
import os

# ---------------------- 1. 定义用户查询 ----------------------
query = "归属于公司普通股股东的净利润的加权平均净资产收益率，基本每股收益，稀释每股收益分别是多少？"

# ---------------------- 2. 配置向量模型 ----------------------
if not os.environ.get("DASHSCOPE_API_KEY"):
    os.environ["DASHSCOPE_API_KEY"] = load_key("BAILIAN_API_KEY")

embedding_model = DashScopeEmbeddings(model="text-embedding-v3")

# ---------------------- 3. 配置 Redis 向量库 ----------------------
redis_url = "redis://localhost:6379"
config = RedisConfig(
    index_name="maotai03",
    redis_url=redis_url
)

# 初始化向量库与检索器
vector_store = RedisVectorStore(embedding_model, config=config)
retriever = vector_store.as_retriever()

# ---------------------- 4. 定义大模型 ----------------------
llm = ChatOpenAI(
    model="deepseek-v3",
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    openai_api_key=load_key("BAILIAN_API_KEY"),
)

# ---------------------- 5. 定义提示词模板 ----------------------
prompt_template = ChatPromptTemplate.from_messages([
    ("user", """你是一个答疑机器人，你的任务是根据下述给定的已知信息回答用户的问题。
    已知信息：{context}
    用户问题：{question}
    如果已知信息不包含用户问题的答案，或者已知信息不足以回答用户的问题，请直接回复“我无法回答您的问题”。
    请不要输出已知信息中不包含的信息或答案。
    请用中文回答用户问题。""")
])

# ---------------------- 6. 定义文档收集函数 ----------------------
def collect_documents(segments):
    text = []
    for segment in segments:
        text.append(segment.page_content)
    return text

# ---------------------- 7. 构建完整 RAG 链 ----------------------
chain = (
    {
        "context": itemgetter("question") | retriever | collect_documents,
        "question": itemgetter("question")
    }
    | prompt_template
    | llm
    | StrOutputParser()
)

# ---------------------- 8. 执行查询 ----------------------
response = chain.invoke({"question": query})
print(response)