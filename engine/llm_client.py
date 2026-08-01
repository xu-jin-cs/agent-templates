"""
LLM 调用抽象
用户需继承此类并实现 complete 方法，接入自己的 LLM provider。
"""

from abc import ABC, abstractmethod


class LLMClient(ABC):
    @abstractmethod
    def complete(self, system_prompt: str, user_prompt: str, context: dict | None = None) -> str:
        """
        调用 LLM 返回文本结果。
        system_prompt: 当前 Agent system prompt
        user_prompt: 当前步骤需要 LLM 执行的任务描述
        context: 前置步骤已读取的文件内容 {file_path: content}
        """
        raise NotImplementedError


class EchoLLMClient(LLMClient):
    """
    默认示例实现：仅把 prompt 打印/返回，不调用真实 LLM。
    用于框架联调和集成测试。
    """

    def complete(self, system_prompt: str, user_prompt: str, context: dict | None = None) -> str:
        ctx_preview = "\n".join([f"[{k}]\n{v[:200]}..." for k, v in (context or {}).items()])
        return f"[ECHO_LLM]\nsystem:\n{system_prompt[:200]}...\nuser:\n{user_prompt}\ncontext:\n{ctx_preview}\n"
