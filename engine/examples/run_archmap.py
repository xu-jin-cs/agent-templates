"""
运行 archmap_agent 的示例
"""

from pathlib import Path
from engine import AgentEngine
from engine.llm_client import EchoLLMClient


def main():
    base = Path(__file__).parent.parent.parent
    config_path = base / "archmap_agent" / "archmap_agent_config.json"
    prompt_path = base / "archmap_agent" / "archmap_agent_system_prompt.md"

    engine = AgentEngine(
        config_path=str(config_path),
        llm_client=EchoLLMClient(),
        system_prompt=prompt_path.read_text(encoding="utf-8"),
    )

    report = engine.run({
        "project_path": "/tmp/demo_project",
        "mode": "baseline",
    })

    print(f"agent={report.agent_name} status={report.error or 'ok'}")
    for step in report.steps:
        print(f"  {step.step_id}: {step.status} outputs={step.outputs}")


if __name__ == "__main__":
    main()
