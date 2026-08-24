"""Unit tests for dependency_engine.Input and the pull resolver."""

import pytest

from dependency_engine import (
    DependencyEngine,
    Input,
    UnsetInputError,
    collect_inputs,
    input_fields,
    reactive,
)


class _Host:
    engine = None
    n = Input(default=1)
    required = Input(required=True)
    shaped = Input(default=(1, 2), coerce=lambda v: tuple(v))
    public_n = Input(default=0, public=True)

    def __init__(self):
        self.engine = DependencyEngine()


def test_input_default_and_assignment():
    host = _Host()
    assert host.n == 1
    host.n = 7
    assert host.n == 7


def test_input_required_unset():
    host = _Host()
    with pytest.raises(UnsetInputError, match="required is not set"):
        _ = host.required


def test_input_required_custom_error():
    class C:
        engine = None
        x = Input(
            required=True,
            unset_error=lambda: RuntimeError("missing x"),
        )

        def __init__(self):
            self.engine = DependencyEngine()

    with pytest.raises(RuntimeError, match="missing x"):
        _ = C().x


def test_input_coerce_keeps_kind():
    host = _Host()
    host.shaped = [3, 4]
    assert host.shaped == (3, 4)


def test_input_clears_engine_cache():
    host = _Host()
    host.engine.cache["n"] = 99
    host.n = 2
    assert host.engine.cache == {}


def test_collect_inputs_and_fields():
    host = _Host()
    host.required = "ok"
    fields = input_fields(_Host)
    assert set(fields) == {"n", "required", "shaped", "public_n"}
    assert fields["public_n"].public is True
    values = collect_inputs(host)
    assert values["n"] == 1
    assert values["required"] == "ok"


def test_reactive_public_flag():
    @reactive
    def internal(x):
        return x

    @reactive(public=True)
    def visible(internal):
        return internal

    assert getattr(internal, "_reactive_public") is False
    assert getattr(visible, "_reactive_public") is True
