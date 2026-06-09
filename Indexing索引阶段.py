from langchain_community.document_loaders import TextLoader
# 1.加载原始文档
# loader = TextLoader("./resource/meituan_questions.txt", encoding="utf-8")
# documents = loader.load()
from langchain_core.documents import Document
import pdfplumber

full_text = ""
with pdfplumber.open("./resource/2023贵州茅台年报.pdf") as pdf:
    for page_num, page in enumerate(pdf.pages):
        # 1. 先提取普通文本（非表格区域）
        page_text = page.extract_text() or ""

        # 2. 提取该页所有表格
        tables = page.extract_tables()
        for table in tables:
            if not table:
                continue
            # 把表格转换成 Markdown 格式的文本块
            # 第一行作为表头
            header = table[0]
            # 后续行作为数据
            rows = table[1:]
            # 构造一个易读的表格文本
            table_md = "\n".join([
                "| " + " | ".join(str(cell) for cell in header) + " |",
                "| " + " | ".join(["---"] * len(header)) + " |"
            ])
            for row in rows:
                if any(row):  # 跳过全空行
                    table_md += "\n| " + " | ".join(str(cell) for cell in row) + " |"
            # 将表格文本追加到页面内容中（替换掉原本混乱的表格文字）
            page_text += "\n[表格内容]\n" + table_md + "\n"

        full_text += page_text + "\n"
documents = [Document(page_content=full_text, metadata={"source": "2023贵州茅台年报.pdf"})]

# 2.切分文档
from langchain_text_splitters import RecursiveCharacterTextSplitter

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50,
    separators=["\n\n", "\n", "。", "！", "？", "；", "，", " ", ""],

)

segments = text_splitter.split_documents(documents)



print(len(segments))
for segment in segments:
    print(segment.page_content)
    print("---------")


# 3.文本向量化+存储
import os
from langchain_community.embeddings import DashScopeEmbeddings
from config.load_key import load_key

# 构建向量化模型
if not os.environ.get("DASHSCOPE_API_KEY"):
    os.environ["DASHSCOPE_API_KEY"] = load_key("BAILIAN_API_KEY")
embedding_model = DashScopeEmbeddings(model="text-embedding-v3")

# 使用Redis构建向量数据库
redis_url = "redis://localhost:6379"

from langchain_redis import RedisConfig, RedisVectorStore
config = RedisConfig(
    index_name="maotai03",
    redis_url=redis_url
)

vector_store = RedisVectorStore(embedding_model, config=config)
# 文档保存到向量数据库中
vector_store.add_documents(segments)
print("加载完成")