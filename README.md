# agent-templates
## 项目概述
一套适配 **Claude Code / Kimi** 的标准化可复用AI Agent协作模板仓库，面向软件研发全流程（需求、架构、并行开发、分片拆解、测试交付）。
所有Agent遵循统一规范：分层文件结构、标准化入参/产物、明确职责隔离、内置异常捕获机制，可直接导入调度引擎或在Claude Code工作台加载使用。

### 核心解决痛点
1. 多AI角色协作边界混乱，并行/分片场景无统一调度规则
2. LLM执行流程无固定约束，易出现步骤遗漏、越权修改文件、幻觉流程
3. 缺少标准化结构化配置，难以对接自研自动化Harness调度引擎
4. 无统一异常、报错产物规范，任务失败无法追溯分片/执行节点

## 仓库目录与三大Agent模块
> 💡规范说明：每个Agent目录标准为4文件结构；`archmap_agent` 当前迭代中，后续补齐剩余文件。
每个Agent目录统一4文件标准结构：
- `xxx_agent_config.json`：机器可读结构化配置（入参Schema、工作流、输出产物）
- `xxx_agent_rules.md`：业务运行规则（场景、边界、依赖、风险约束）
- `xxx_agent_system_prompt.md`：LLM执行系统提示词
- `README.md`：单模块使用说明

agent-templates/
├── archmap_agent/ # 架构测绘 Agent（持续完善中）
├── split_mother_agent/ # 带依赖子母分片拆解 Agent（完整就绪）
├── parallel_task_agent/ # 无依赖并行任务调度 Agent（待上传）
└── README.md # 项目根文档
plaintext

### 各Agent能力分工与路由规则
1. **archmap_agent 架构测绘Agent**
用途：扫描项目代码、梳理模块、接口、数据表依赖，输出架构资产；
上游：原始代码仓库；下游：并行Agent / 子母分片Agent / PM。

2. **parallel_task_agent 并行任务调度Agent**
适用：任务互相无文件/数据依赖（前端、后端、测试同步开发）；
禁止：存在前后依赖的任务，检测到依赖自动转交split_mother_agent；
产物：并行执行报告、校验摘要、依赖冲突error_report.json。

3. **split_mother_agent 子母分片Agent**
适用：大型需求、存在任务依赖、单Agent上下文不足，需分片串行+局部并行；
路由：所有分片无依赖时，自动转交parallel_task_agent；
约束：max_shards固定1~9，单分片失败不阻塞整体，输出shard_error_report.json异常文件。

### 全局统一强制规范（所有Agent通用）
1. 禁止引入快照、增量日志、版本回滚等无关业务逻辑；
2. 每一步执行完成必须调用`TaskUpdate`同步任务状态；
3. 文件读写隔离：子Agent仅操作本分片/任务对应文件，禁止跨范围修改；
4. 流程闭环：无论执行成功/失败，必须输出最终汇总Markdown文档；
5. 产物分层：正常执行输出标准文件，异常场景生成独立报错JSON用于问题追溯。

## 快速使用指南（Claude Code 工作台）
### 1. 仓库导入
克隆本仓库到本地/工作台：
```bash
git clone https://github.com/xu-jin-cs/agent-templates.git
cd agent-templates
打开对应 Agent 子目录。
2. 加载执行流程
Agent 启动时强制读取同目录 config.json + rules.md 作为执行基准；
传入外部入参（task_description、input_files、size 等）；
Agent 自动判定场景路由：并行 / 子母分片二选一；
按内置工作流完整执行，自动生成全部标准产物；
异常自动输出对应报错 JSON，汇总写入最终摘要文档。
3. 调度引擎接入方式
自研 Harness 调度引擎直接读取各目录xxx_agent_config.json，解析：
input_schema：入参校验规则
workflow_steps：标准化执行步骤
output_spec：全部产出文件名称、字段、消费方
协作流转示例（完整研发链路）
archmap_agent 扫描代码，输出架构依赖资产；
PM 输入需求 + 架构文件，Agent 自动判定任务依赖关系；
无依赖 → parallel_task_agent 同步启动前后端测试；
存在分层依赖 → split_mother_agent 分片串行执行，无依赖分片局部并行；
全部子任务完成后输出统一校验报告，交付 PM 验收。

## License
This project is open source under the MIT License. See the [LICENSE](./LICENSE) file for details.
