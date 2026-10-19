"""Structured logging (text default / JSON opt-in)."""

from __future__ import annotations

import json
import logging
from io import StringIO

import pytest

from dependency_engine import DependencyEngine
from genice3.cli.genice import run
from genice3.logging_config import (
    JsonFormatter,
    bind_context,
    resolve_log_format,
    reset_context,
    setup_logging,
)


def test_resolve_log_format_prefers_cli_then_env(monkeypatch):
    monkeypatch.delenv("GENICE_LOG_FORMAT", raising=False)
    assert resolve_log_format(None) == "text"
    assert resolve_log_format("json") == "json"
    monkeypatch.setenv("GENICE_LOG_FORMAT", "json")
    assert resolve_log_format(None) == "json"
    assert resolve_log_format("text") == "text"


def test_json_formatter_includes_event_and_context():
    token = bind_context(run_id="abcd1234", unitcell="1h")
    try:
        record = logging.LogRecord(
            name="dependency_engine",
            level=logging.INFO,
            pathname=__file__,
            lineno=1,
            msg="Executing: %s",
            args=("orientations",),
            exc_info=None,
        )
        record.event = "task.execute"
        record.task = "orientations"
        record.duration_ms = 12.5
        line = JsonFormatter().format(record)
        data = json.loads(line)
        assert data["event"] == "task.execute"
        assert data["task"] == "orientations"
        assert data["duration_ms"] == 12.5
        assert data["run_id"] == "abcd1234"
        assert data["unitcell"] == "1h"
        assert data["msg"] == "Executing: orientations"
        assert data["level"] == "INFO"
        assert "ts" in data
    finally:
        reset_context(token)


def test_setup_logging_json_writes_ndjson_to_stderr(capsys):
    setup_logging(debug=False, fmt="json")
    logging.getLogger("test_logging_config").info(
        "hello",
        extra={"event": "run.start", "seed": 1},
    )
    err = capsys.readouterr().err.strip()
    data = json.loads(err.splitlines()[-1])
    assert data["event"] == "run.start"
    assert data["seed"] == 1
    assert data["msg"] == "hello"


def test_dependency_engine_task_execute_extra(capsys):
    setup_logging(debug=False, fmt="json")
    engine = DependencyEngine()

    @engine.task
    def reaction_A(raw_material: int):
        return raw_material * 2

    engine.resolve(target="reaction_A", inputs={"raw_material": 3})
    lines = [
        json.loads(line)
        for line in capsys.readouterr().err.splitlines()
        if line.strip().startswith("{")
    ]
    events = [row for row in lines if row.get("event") == "task.execute"]
    assert events
    assert events[0]["task"] == "reaction_A"
    assert "duration_ms" in events[0]


@pytest.fixture(autouse=True)
def _restore_text_logging():
    yield
    setup_logging(debug=False, fmt="text")


def test_cli_log_format_json_emits_run_events(capsys):
    code = run(["1h", "--rep", "1", "1", "1", "--seed", "1", "--log-format", "json"])
    assert code == 0
    captured = capsys.readouterr()
    assert len(captured.out) > 50
    # Structure on stdout must not look like NDJSON logs
    assert not captured.out.lstrip().startswith("{")

    rows = [
        json.loads(line)
        for line in captured.err.splitlines()
        if line.strip().startswith("{")
    ]
    events = {row["event"] for row in rows if "event" in row}
    assert "run.start" in events
    assert "run.end" in events
    assert "task.execute" in events
    assert "exporter.execute" in events
    assert all("run_id" in row for row in rows if row.get("event") == "run.start")


def test_cli_log_format_underscore_alias(capsys):
    code = run(["1h", "--seed", "1", "--log_format", "json", "-e", "gromacs"])
    assert code == 0
    rows = [
        json.loads(line)
        for line in capsys.readouterr().err.splitlines()
        if line.strip().startswith("{")
    ]
    assert any(row.get("event") == "run.start" for row in rows)
