# 自研 Agent 调度引擎

本目录提供一个最小可运行的 Python 调度引擎，用于把 `archmap_agent`、`parallel_task_agent`、`split_mother_agent` 的 `config.json` + `system_prompt.md` + `rules.md` 真正跑起来。

## 设计定位

- **不负责 LLM 能力本身**：只负责按配置顺序驱动 workflow、管理输入输出、调用你指定的 LLM Client。
- **可插拔**：LLM、任务状态同步（TaskUpdate）都是接口，你可以替换为自己的实现。
- **最小可用**：代码量小，便于阅读和二次开发。

## 目录结构

```
engine/
├── __init__.py
├── agent_engine.py      # 核心引擎：读取 config、执行 workflow
├── models.py            # 执行过程数据模型
├── validators.py        # 输入参数校验
├── llm_client.py        # LLM 调用抽象 + Echo 示例实现
├── task_update.py       # TaskUpdate 钩子 + 默认打印实现
├── README.md            # 本文件
├── requirements.txt     # Python 依赖
└── examples/
    └── run_archmap.py   # 运行 archmap_agent 的示例
```

## 快速开始

### 1. 安装依赖

```bash
cd engine
pip install -r requirements.txt
```

### 2. 接入你的 LLM

实现 `LLMClient` 抽象类：

```python
from engine.llm_client import LLMClient

class MyLLM(LLMClient):
    def complete(self, system_prompt: str, user_prompt: str, context: dict | None = None) -> str:
        # 调用你自己的 LLM API
        return response_text
```

### 3. 运行 Agent

```python
from pathlib import Path
from engine import AgentEngine
from engine.llm_client import EchoLLMClient

engine = AgentEngine(
    config_path="../archmap_agent/archmap_agent_config.json",
    llm_client=MyLLM(),  # 或 EchoLLMClient() 用于测试
    system_prompt=Path("../archmap_agent/archmap_agent_system_prompt.md").read_text(),
)

report = engine.run({
    "project_path": "/path/to/project",
    "mode": "baseline",
    "output_dir": "/path/to/project/archmap/",
})

print(report)
```

## 集成说明

### 与现有 Agent 的集成关系

```
engine/agent_engine.py
    ├── 读取 archmap_agent/archmap_agent_config.json
    ├── 读取 parallel_task_agent/parallel_agent_config.json
    └── 读取 split_mother_agent/split_mother_agent_config.json
```

引擎按 `workflow_steps` 顺序执行，每个步骤：

1. 读取 `input` 指定的文件或参数；
2. 拼装 prompt（system_prompt + 当前步骤描述 + 上下文）；
3. 调用 LLMClient 生成内容；
4. 写入 `output` 指定的文件；
5. 调用 TaskUpdate 同步状态。

### 需要用户自己实现的部分

| 组件 | 默认提供 | 建议替换 |
|------|----------|----------|
| LLM 调用 | `EchoLLMClient`（仅回显） | 接入 Claude / Kimi / DeepSeek 等真实 LLM |
| TaskUpdate | 打印到 stdout | 接入你的任务状态服务 |
| 条件触发器 | 简单字符串匹配 | 接入真实条件判定逻辑 |

### 条件步骤（trigger）

`config.json` 中部分步骤带 `trigger` 字段。当前引擎用简化规则判断是否跳过：

- 若 `condition` 包含 `precise_analysis`，检查 `params._precise_analysis` 是否存在；
- 若包含异常关键词，检查 `params._has_error` 是否为真；
- 否则默认执行。

生产环境中，建议扩展 `AgentEngine._evaluate_condition` 方法，接入你的规则引擎。

## 限制与说明

- 本引擎不生成真实架构内容，只负责编排 workflow；实际内容生成依赖你接入的 LLM。
- 文件写入按 `output_dir` 落地，不嵌套额外目录。
- 输入校验已实现 `required`、`enum`、`number`（含 minimum/maximum）、`array` 等基本类型。
- 异常时会停止 workflow 并返回 `ExecutionReport`。

## 下一步建议

1. 先运行 `examples/run_archmap.py` 确认框架联调通过。
2. 实现 `MyLLMClient` 接入真实 LLM。
3. 实现自定义 `TaskUpdateHook` 接入你的任务状态服务。
4. 扩展条件判定逻辑，满足生产需求。
