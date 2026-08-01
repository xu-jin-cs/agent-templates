"""
执行过程数据模型
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class AgentInput:
    agent_name: str
    params: dict[str, Any]


@dataclass
class StepResult:
    step_id: str
    status: str  # ok / skipped / failed
    outputs: list[str] = field(default_factory=list)
    error: str | None = None


@dataclass
class ExecutionReport:
    agent_name: str
    mode: str | None
    steps: list[StepResult]
    outputs: list[str]
    error: str | None = None
