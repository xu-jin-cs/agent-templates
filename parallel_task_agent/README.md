# parallel_task_agent

无依赖独立任务并行执行调度 Agent 模板。

## 能力范围

- 解析任务列表并判定任务间依赖关系。
- 将互相无依赖的前端、后端、测试等任务分发给对应角色 Agent 同步执行。
- 通过内存事件回调收集子 Agent 执行结果。
- 调用指定的 `merge_validator` 统一合并校验并行结果。
- 输出并行执行报告与合并校验摘要。

## 文件说明

- `parallel_agent_config.json`：结构化机器可读配置，包含输入参数、执行步骤、产物规范。
- `parallel_agent_system_prompt.md`：主系统提示词，供 LLM 对话加载使用。
- `parallel_task_scheduler_rules.md`：独立详细规则文档，补充边界、场景、禁用逻辑。

## 输入参数

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| tasks | array | 是 | 任务列表，每项含 role、description、input_files |
| roles | enum[] | 是 | 可并行角色，如 `frontend`、`backend`、`test` |
| merge_validator | string | 是 | 负责统一合并校验的 Agent 名称，通常为 PM |
| timeout_seconds | number | 否 | 单任务超时时间，默认 600 |

## 输出产物

- `parallel_execution_report.json`：每个任务的执行状态、输出产物、耗时、校验结果。
- `merged_validation_summary.md`：统一合并校验结论与遗留问题。
- `error_report.json`（依赖报错时）：错误码、错误信息、存在依赖的任务列表。

## 与仓库其他 Agent 的数据流转

```
PM / 后端引擎
    │
    ├─ 无依赖任务清单 ──────────────→ parallel_task_agent
    │                                    │
    │                                    ├─ 发现依赖 ──→ error_report.json
    │                                    └─ 无依赖 ────→ 并行执行 FE / BE / Test Agent
    │                                                       │
    └─ 接收 merged_validation_summary.md ←──────────────────┘
```

## 核心约束

- 仅处理互相无依赖的独立任务。
- 发现任务依赖时固定报错并终止，转交 `split_mother_agent`。
- 不接管子母分片逻辑。
- 子 Agent 通过内存事件回调返回结果，禁止轮询文件状态。
- 禁止快照、回滚、增量日志、版本恢复相关逻辑。
