# RAG 智能问答系统（支持表格解析优化）
![Python](https://img.shields.io/badge/Python-3.10-blue)
![LangChain](https://img.shields.io/badge/LangChain-0.1+-green)
![Redis](https://img.shields.io/badge/Redis-Vector%20DB-red)
![License](https://img.shields.io/badge/License-MIT-yellow)
![Status](https://img.shields.io/badge/Status-Active-brightgreen)
## 📑 目录
- [项目简介](#项目简介)
- [效果对比](#效果对比)
- [技术栈](#技术栈)
- [如何运行](#如何运行)
- [优化记录](#优化记录)
- [未来计划](#未来计划)
**项目经历 - RAG智能问答系统（PDF表格解析优化）**
- **背景（S）**：在构建本地PDF知识库问答系统时，使用pdfplumber默认的extract_text()方法提取财报PDF，发现表格内容行列错乱（如“营业收入”与数字无法对应），导致大模型无法检索到具体数值。
- **任务（T）**：提高系统对PDF表格数据的检索准确率，使其能正确回答“2023年营业收入是多少？”等数值类问题。
- **行动（A）**：研究pdfplumber的表格提取功能，改用extract_tables()方法获取结构化表格数据，并用“|”分隔符将每行单元格拼接为文本，替代原有混乱的表格区域。
- **结果（R）**：优化后，系统能准确返回“2023年营业收入1476.94亿元”等具体数值，检索准确率显著提升。
## 效果对比
| 修复前（表格行列错乱） | 修复后（结构化文本） |
|----------------------|----------------------|
| ![修复前](./images/before.png) | ![修复后](./images/after.png) |
[点击这里查看项目演示视频](https://b23.tv/ORF1rcC)
## 技术栈
- Python 3.10
- LangChain
- pdfplumber
- Redis (向量数据库)
- 阿里云百炼 (embedding + 大模型 API)

## 如何运行
1. 安装依赖：`pip install -r requirements.txt`
2. 启动 Redis 服务（`redis-server`）
3. 配置你的阿里云百炼 API Key（在代码中替换）
4. 运行 `python Indexing索引阶段.py`（构建向量索引）
5. 运行 `python 整合.py`（提问示例）

## 我的优化记录
**问题**：使用 `pdfplumber.extract_text()` 提取财报表格时，数字和文字混在一起，无法检索“营业收入”。  
**解决**：改用 `extract_tables()` 逐行用 `|` 拼接，保留表格结构。  
**结果**：可准确回答“2023年营业收入为 1476.94 亿元”。

## 未来计划
- 支持更多文档类型（Word、图片）
- 添加 Streamlit 前端界面
