# 关键业务设计与源码导读

建议按“知识如何进入 → 如何被检索 → 如何参与分析 → 如何形成报告”的顺序阅读。README 中的四幅业务图对应以下真实函数与数据模型。

## 1. 模块输入与输出

| 业务 | 输入 | 核心入口 | 输出 |
| --- | --- | --- | --- |
| RAG 知识库 | 文件字节、文件名、标题 | `ingest_document()` | 文档与分块记录、导入任务摘要 |
| 混合检索 | `query`、`top_k`、已入库分块 | `search()` | 带引用与分阶段评分的 `SearchHit` 列表 |
| 智能分析 | `QuestionRequest`、检索上下文 | `answer_question()` → `provider.analyze()` | `QuestionAnswer` |
| 智能报告 | `ReportRequest`、设备与运维记录 | `create_report()` → `get_report()` | 任务摘要、统计、Markdown 内容与下载地址 |

## 2. 知识库：内容、元数据与来源关联

阅读路径：[知识服务](../app/modules/knowledge/service.py) → [文档解析](../app/services/document_parser.py) → [数据模型](../app/db/models.py)。

1. `ingest_document()` 对完整上传内容计算 SHA-256，并检查文档表中是否存在相同摘要；重复内容返回 409。
2. `parse_document()` 依据扩展名选择解析器，支持 PDF、DOCX、TXT、Markdown，提取可读文本。
3. `chunk_document()` 按段落组织内容，目标长度为 800 字符，衔接时保留前块末尾 120 字符。它优先保留段落完整性，单个长段落可能超过目标长度。
4. `KnowledgeDocument` 保存标题、文件名、摘要和分块数量；`KnowledgeChunk` 保存 `document_id`、序号和内容。知识服务提交这些记录以及导入任务结果。

讲解重点是：检索使用统一分块模型，不需要知道原文件来自哪一种解析器；引用可以通过文档 ID 和分块序号回到具体内容。

## 3. 检索：候选、评分、融合与重排

阅读路径：[检索实现](../app/services/retrieval/local_hybrid.py) → [SearchHit 模型](../app/modules/knowledge/schemas.py)。

`search()` 当前读取全部知识分块及文档信息，然后依次计算两种分数：

- 关键词分数综合查询词频、分块词频与文档频率。
- 向量分数使用 SHA-256 将词元映射到 128 维带符号特征向量，归一化后计算余弦相似度。

两路排名通过 `1 / (60 + rank)` 累加形成 RRF 分数。最终重排分数为 RRF 分数加查询词覆盖比例，排序后才截取 `top_k`。因此图中的双分支表示两种逻辑评分，不表示两个线程或外部服务并发执行。

每条 `SearchHit` 同时返回内容、文档 ID、分块 ID、标题、引用与四项评分。介绍这一模块时，可以直接沿着 `tokenize()` → `deterministic_embedding()` → `search()` 的顺序说明评分来源。

查询时按统一规则计算分块特征、关键词相关度与查询覆盖比例，整个排序过程可以结合返回的阶段评分进行解释。

## 4. 分析：编排与模型协议分开

阅读路径：[分析路由](../app/modules/analysis/router.py) → [Provider](../app/services/llm/providers.py) → [分析模型](../app/modules/analysis/schemas.py) → [错误响应](../app/core/errors.py)。

调用顺序是 `answer_question()` → `search_knowledge()` → `provider.analyze()` → `QuestionAnswer`。路由保留检索引用，并将结果转换为回答、风险等级、建议列表、引用列表和 Provider 名称。

`LLMProvider` 定义统一的 `analyze(question, contexts)` 接口。参考响应实现与 HTTP 实现共享接口；HTTP 实现负责上下文组装、OpenAI 兼容请求、30 秒超时、JSON 解析和必需字段检查。请求或 JSON 解析失败返回 Provider 不可用错误，必需字段缺失返回响应无效错误。

提示中的上下文约束和响应中的引用共同支持答案审阅；讲解时可以展示问题、检索分块、上下文组织与最终响应之间的对应关系。

## 5. 报告：统计口径与结果生命周期

阅读路径：[报告请求模型](../app/modules/reports/schemas.py) → [报告服务](../app/modules/reports/service.py) → [报告路由](../app/modules/reports/router.py)。

- `_request_key()` 对完整报告请求生成摘要；`create_report()` 先查找同摘要的成功任务，命中后返回原任务 ID 与 `reused=True`。
- `_statistics()` 对当前设备状态分组统计，对运维记录按事件类型与严重级别聚合。日期范围转换为 UTC 的 `[开始日 00:00, 结束日次日 00:00)`，完整覆盖结束日期。
- `_render_markdown()` 将统一统计模型渲染成报告。`TaskRecord.result_json` 保存内容、统计和生成时间，`get_report()` 负责结果读取，下载路由设置 Markdown 响应类型与文件名。

结果复用以请求参数为依据，同参数请求可返回已保存的报告快照，生成时间用于识别报告所对应的时间点。报告生成在请求内同步执行，任务表统一记录内容、统计和状态。

## 6. 推荐讲解路线

先从 [README 的总体架构](../README.md#系统架构)说明 API、业务服务、存储与 Provider 的边界，再逐个说明输入、关键处理、输出和异常路径。每个模块都可以回答四个问题：数据从哪里来，如何处理，结果如何追溯，模块之间如何协作。
