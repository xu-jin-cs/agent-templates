# archmap_agent

架构测绘 Agent 模板，用于项目代码架构的基线全量测绘与增量 Diff 测绘。

## 能力范围

- 全量扫描项目源码、配置、依赖文件，建立代码基线。
- 解析模块边界、API 接口、存储结构、依赖矩阵。
- 生成架构图、数据链路图、时序图文本描述。
- 基于变更 Diff 做增量影响面分析，输出受影响模块、接口、数据表、前端资源清单。
- 将模块/API/存储资产向量化，供 RAG 知识库检索使用。

## 文件说明

- `archmap_agent_config.json`：结构化机器可读配置，包含输入参数、执行步骤、产物规范。
- `archmap_agent_system_prompt.md`：主系统提示词，供 LLM 对话加载使用。
- `archmap_agent_rules.md`：独立详细规则文档，补充边界、场景、禁用逻辑。

## 输入参数

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| project_path | string | 是 | 项目根目录绝对路径 |
| mode | enum | 是 | `baseline` / `incremental` |
| diff_doc | string | 增量模式必填 | 变更 Diff 文档路径或内容 |
| requirement_text | string | 增量分析时建议填写 | 需求文本，用于定位相关模块 |
| output_dir | string | 否 | 输出目录，默认 `{project_path}/archmap/` |

## 输出产物

- `01_执行摘要.md`
- `02_架构图.md`
- `03_数据链路图.md`
- `04_时序图.md`
- `05_模块资产清单.md`
- `06_API资产清单.md`
- `07_存储资产清单.md`
- `08_依赖矩阵.md`
- `09_粒度校验报告.md`
- `full_index.json`
- `module_hashes.json`
- `precise_analysis.json`（增量模式）
- `vector_cache.json`

## 与仓库其他 Agent 的数据流转

```
archmap_agent
    │
    ├─ 输出 precise_analysis.json ──→ split_mother_agent（指导任务分片）
    ├─ 输出模块/API/存储清单 ────────→ parallel_task_agent（辅助无依赖任务识别）
    └─ 输出架构图/数据链路图 ────────→ PM / FE / BE / 测试（影响面沟通）
```

## 核心约束

- 基线模式完整扫描项目代码，生成全套资产。
- 增量模式禁止全局扫描，必须基于 Diff 文档与已有基线资产局部更新。
- 所有产物统一输出至 `output_dir`，不额外嵌套目录。
- 禁止快照、回滚、增量日志、版本恢复相关逻辑。
