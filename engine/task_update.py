"""
TaskUpdate 钩子
用户可替换为自有任务状态同步实现。
"""

from typing import Callable


TaskUpdateFunc = Callable[[str, str, dict | None], None]


class TaskUpdateHook:
    def __init__(self, callback: TaskUpdateFunc | None = None):
        self.callback = callback or self._default

    @staticmethod
    def _default(task_id: str, status: str, meta: dict | None = None) -> None:
        print(f"[TaskUpdate] {task_id} -> {status}")

    def __call__(self, task_id: str, status: str, meta: dict | None = None) -> None:
        self.callback(task_id, status, meta)
