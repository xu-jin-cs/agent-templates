"""
Agent 调度引擎核心
读取 Agent 配置，顺序执行 workflow，驱动 LLM 完成各步骤。
"""

import json
import os
from pathlib import Path
from typing import Any

from .llm_client import LLMClient
from .models import AgentInput, ExecutionReport, StepResult
from .task_update import TaskUpdateHook
from .validators import ValidationError, validate_input


class AgentEngine:
    def __init__(
        self,
        config_path: str,
        llm_client: LLMClient,
        task_update: TaskUpdateHook | None = None,
        system_prompt: str | None = None,
    ):
        self.config = json.loads(Path(config_path).read_text(encoding="utf-8"))
        self.llm = llm_client
        self.task_update = task_update or TaskUpdateHook()
        self.system_prompt = system_prompt or ""
        self.agent_name = self.config["name"]

    def run(self, params: dict[str, Any]) -> ExecutionReport:
        self.task_update(self.agent_name, "in_progress", {"params": params})

        try:
            validate_input(self.config.get("input_schema", {}), params)
        except ValidationError as e:
            self.task_update(self.agent_name, "failed", {"error": str(e)})
            return ExecutionReport(self.agent_name, params.get("mode"), [], [], error=str(e))

        steps = self.config.get("workflow_steps", [])
        step_results: list[StepResult] = []
        outputs: list[str] = []

        for step in steps:
            result = self._run_step(step, params)
            step_results.append(result)
            outputs.extend(result.outputs)
            self.task_update(f"{self.agent_name}:{step['id']}", result.status, {"outputs": result.outputs})
            if result.status == "failed":
                break

        overall = "ok" if all(r.status in ("ok", "skipped") for r in step_results) else "failed"
        self.task_update(self.agent_name, overall, {"outputs": outputs})
        return ExecutionReport(self.agent_name, params.get("mode"), step_results, outputs, error=None)

    def _run_step(self, step: dict[str, Any], params: dict[str, Any]) -> StepResult:
        step_id = step["id"]
        trigger = step.get("trigger")

        if trigger and trigger.get("type") == "conditional":
            if not self._evaluate_condition(trigger.get("condition"), params):
                return StepResult(step_id, "skipped")

        context = self._read_inputs(step.get("input", []), params)
        user_prompt = self._build_prompt(step, params, context)

        try:
            result_text = self.llm.complete(self.system_prompt, user_prompt, context)
        except Exception as e:
            return StepResult(step_id, "failed", error=str(e))

        written = self._write_outputs(step.get("output", []), params, result_text)
        return StepResult(step_id, "ok", outputs=written)

    def _evaluate_condition(self, condition: str, params: dict[str, Any]) -> bool:
        # 简化判定：基于 precise_analysis 是否存在、mode 等
        if "precise_analysis" in condition.lower():
            return bool(params.get("_precise_analysis"))
        if "非法入参" in condition or "分片依赖冲突" in condition or "子 Agent 执行失败" in condition:
            return bool(params.get("_has_error"))
        return True

    def _read_inputs(self, inputs: list[str], params: dict[str, Any]) -> dict[str, str]:
        context: dict[str, str] = {}
        output_dir = self._output_dir(params)
        for item in inputs:
            if item in params:
                context[item] = str(params[item])
                continue
            path = Path(item) if Path(item).is_absolute() else Path(output_dir) / item
            if path.exists():
                context[str(path)] = path.read_text(encoding="utf-8")
        return context

    def _write_outputs(self, outputs: list[str], params: dict[str, Any], content: str) -> list[str]:
        written: list[str] = []
        output_dir = self._output_dir(params)
        for item in outputs:
            path = Path(output_dir) / item if not Path(item).is_absolute() else Path(item)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
            written.append(str(path))
        return written

    def _output_dir(self, params: dict[str, Any]) -> str:
        project = params.get("project_path", ".")
        default = os.path.join(project, "archmap")
        return params.get("output_dir") or default

    def _build_prompt(self, step: dict[str, Any], params: dict[str, Any], context: dict[str, str]) -> str:
        lines = [
            f"步骤编号: {step['id']}",
            f"步骤动作: {step['action']}",
            f"输入参数: {json.dumps(params, ensure_ascii=False)}",
            f"已读取文件: {list(context.keys())}",
            "请根据以上信息生成本步骤应输出的产物内容。",
        ]
        return "\n".join(lines)
