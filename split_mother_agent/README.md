# split_mother_agent

大型任务分片拆解与结果汇总 Agent 模板。

## 文件说明

- `split_mother_agent_config.json`：结构化机器可读配置，包含输入参数、执行步骤、产物规范。
- `split_mother_agent_system_prompt.md`：主系统提示词，供 LLM 对话加载使用。
- `split_mother_agent_rules.md`：独立详细规则文档，补充边界、场景、禁用逻辑。

## 使用方式

### 给 LLM 对话使用

以 `split_mother_agent_system_prompt.md` 作为 system prompt 加载，`split_mother_agent_rules.md` 作为附件引用，避免主提示词过长。

### 给调度框架使用

加载 `split_mother_agent_config.json`，按其中 `workflow_steps` 顺序执行，根据 `trigger` 条件输出异常产物 `shard_error_report.json`。

## 核心约束

- 必须调用 `task_breakdown` 后才能分片。
- 存在前后依赖的分片按序执行，无依赖的分片并行执行。
- 检测到无任何分片依赖时，自动转交并行任务调度 Agent。
- 子 Agent 仅执行本分片任务，禁止越权修改非分片范围文件。
- 母 Agent 必须校验结果后再汇总。
- 禁止快照、回滚、增量日志、版本恢复相关逻辑。

## 输出产物

- `task_breakdown.json`
- `shard_results/`
- `final_summary.md`
- `shard_error_report.json`（异常时）
