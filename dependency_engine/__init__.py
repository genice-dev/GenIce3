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

# Sentinel: Input に default も default_factory もない。
_MISSING = object()


class UnsetInputError(Exception):
    """Raised when a required ``Input`` has not been assigned."""


def reactive(func=None, *, public=False):
    """Marker decorator to register a function as a DependencyEngine task.

    The decorated function name becomes the reactive property name
    (for example, ``genice.cages``). Names should be nouns.

    Args:
        public: If True, the task is part of the public API listing.

    Side effect: the function is registered in ``_REACTIVE_REGISTRY``.
    Use ``get_reactive_tasks(module_name)`` to obtain the task list for a module.
    """

    def decorate(fn):
        fn._reactive_public = public
        _REACTIVE_REGISTRY.append((fn.__module__, fn))
        return fn

    if func is None:
        return decorate
    return decorate(func)


def get_reactive_tasks(module_name: str):
    """Return functions decorated with ``@reactive`` in the given module."""
    return [f for mod, f in _REACTIVE_REGISTRY if mod == module_name]


class Input:
    """Descriptor for a DAG root (settable reactive input).

    Assignment stores the value, optionally coerces it (same kind of object),
    runs ``on_set``, and clears ``obj.engine.cache``. Getter and
    ``collect_inputs`` are derived from the class-level declaration.

    Do not use ``coerce`` to change the public type (for example str to a
    constructed object). Keep a separate factory method for that.
    """

    def __init__(
        self,
        *,
        default=_MISSING,
        default_factory=None,
        public=False,
        required=False,
        coerce=None,
        on_set=None,
        unset_error=None,
        doc=None,
    ):
        if required and (default is not _MISSING or default_factory is not None):
            raise TypeError("required Input cannot have a default")
        if default is not _MISSING and default_factory is not None:
            raise TypeError("specify default or default_factory, not both")
        self.default = default
        self.default_factory = default_factory
        self.public = public
        self.required = required
        self.coerce = coerce
        self.on_set = on_set
        self.unset_error = unset_error
        self.name = None
        self.private_name = None
        if doc is not None:
            self.__doc__ = doc

    def __set_name__(self, owner, name):
        self.name = name
        self.private_name = f"_{name}"
        if "_input_fields" not in owner.__dict__:
            owner._input_fields = {}
        owner._input_fields[name] = self

    def is_set(self, obj) -> bool:
        """Return True if this input has been assigned on ``obj``."""
        return self.private_name in obj.__dict__

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        if self.private_name in obj.__dict__:
            return obj.__dict__[self.private_name]
        if self.required:
            if self.unset_error is not None:
                err = self.unset_error
                raise err() if callable(err) else err
            raise UnsetInputError(
                f"{type(obj).__name__}.{self.name} is not set."
            )
        if self.default_factory is not None:
            return self.default_factory()
        if self.default is not _MISSING:
            return self.default
        raise UnsetInputError(f"{type(obj).__name__}.{self.name} is not set.")

    def __set__(self, obj, value):
        if self.coerce is not None:
            value = self.coerce(value)
        obj.__dict__[self.private_name] = value
        logger = getattr(obj, "logger", None)
        if logger is not None:
            logger.debug("  %s=%r", self.name, value)
        if self.on_set is not None:
            self.on_set(obj, value)
        engine = getattr(obj, "engine", None)
        if engine is not None:
            engine.cache.clear()


def input_fields(cls) -> dict:
    """Return ``{name: Input}`` declared on ``cls`` (including bases)."""
    fields = {}
    for base in reversed(cls.__mro__):
        fields.update(getattr(base, "_input_fields", {}))
    return fields


def collect_inputs(obj) -> dict:
    """Return a dict of all ``Input`` values on ``obj`` for ``engine.resolve``."""
    return {name: getattr(obj, name) for name in input_fields(type(obj))}


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
