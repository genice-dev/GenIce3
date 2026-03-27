"""
Dependency-resolution engine for reactive pipelines.

Executes only the tasks needed to reach a given goal, working backwards
from the target. May be split into a separate package in the future.
"""

import inspect
from logging import getLogger
import time

# @reactive でデコレートされた関数を (モジュール名, 関数) で保持。
# 利用側が _register_tasks で get_reactive_tasks(__name__) により自モジュール分だけ登録する。
_REACTIVE_REGISTRY = []


def reactive(func):
    """Marker decorator to register a function as a DependencyEngine task.

    The decorated function name becomes the reactive property name
    (for example, ``genice.cages``). Names should be nouns.

    Side effect: the function is registered in ``_REACTIVE_REGISTRY``.
    Use ``get_reactive_tasks(module_name)`` to obtain the task list for a module.
    """
    _REACTIVE_REGISTRY.append((func.__module__, func))
    return func


def get_reactive_tasks(module_name: str):
    """Return functions decorated with ``@reactive`` in the given module."""
    return [f for mod, f in _REACTIVE_REGISTRY if mod == module_name]


class DependencyEngine:
    """Engine that back-solves dependencies and runs only needed tasks."""

    logger = getLogger("dependency_engine")

    def __init__(self):
        self.registry = {}  # { 'output_name': function }
        self.cache = {}

    def task(self, func):
        """Decorator to register a task with ``func.__name__`` as its output name."""
        self.registry[func.__name__] = func
        return func

    def resolve(self, target: str, inputs: dict):
        """Resolve ``target`` by recursively computing its dependencies."""

        # 1. 既に計算済み or 入力として与えられているならそれを返す
        if target in inputs:
            return inputs[target]
        if target in self.cache:
            return self.cache[target]

        # 2. 生成ルール（関数）を探す
        if target not in self.registry:
            raise ValueError(f"Don't know how to make '{target}'")

        func = self.registry[target]

        # 3. その関数の引数（依存先）を調べて、再帰的に解決する
        sig = inspect.signature(func)
        dependencies = {}
        for param_name in sig.parameters:
            dependencies[param_name] = self.resolve(param_name, inputs)

        # 4. 実行して結果を保存
        self.logger.info(f"Executing: {target}")
        now = time.time()
        result = func(**dependencies)
        delta = time.time() - now
        self.logger.debug(f"  {delta:.4f} sec for {target}")
        self.cache[target] = result
        return result


def _demo():
    """Package self-test demo (run with ``python -m dependency_engine``)."""
    engine = DependencyEngine()

    @engine.task
    def reaction_A(raw_material: int):
        return raw_material * 2

    @engine.task
    def reaction_B(reaction_A: int, catalyst: int):
        return reaction_A + catalyst

    result = engine.resolve(
        target="reaction_B", inputs={"raw_material": 10, "catalyst": 5}
    )
    print(result)


if __name__ == "__main__":
    _demo()
