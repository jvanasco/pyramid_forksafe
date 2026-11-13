"""Verify Celery registration and signal dispatch without a worker."""

import sys
from types import ModuleType, SimpleNamespace
from typing import Any, List
from unittest.mock import Mock

import pytest
from pyramid.config import Configurator

from pyramid_forksafe import events
from pyramid_forksafe.containers import celery


def test_celery_registration(monkeypatch: "pytest.MonkeyPatch") -> None:
    """Register each signal once and dispatch only in the expected process."""
    fake_celery = ModuleType("celery")
    fake_signals = SimpleNamespace(
        worker_before_create_process=Mock(),
        worker_process_init=Mock(),
        worker_process_shutdown=Mock(),
    )
    setattr(fake_celery, "signals", fake_signals)
    monkeypatch.setitem(sys.modules, "celery", fake_celery)
    getpid = Mock(return_value=123)
    monkeypatch.setattr(celery, "os", SimpleNamespace(getpid=getpid))
    config = Configurator()
    received: List[Any] = []
    for event_type in (
        events.ApplicationPreFork,
        events.ApplicationPostWorkerInit,
        events.ApplicationWorkerExit,
    ):
        config.registry.registerHandler(received.append, (event_type,))

    celery.configure(config)
    celery.configure(config)
    handlers = []
    for name in (
        "worker_before_create_process",
        "worker_process_init",
        "worker_process_shutdown",
    ):
        connect = getattr(fake_signals, name).connect
        assert connect.call_count == 1
        args, kwargs = connect.call_args
        assert kwargs == {"weak": False}
        handlers.append(args[0])

    for handler in handlers:
        handler(sender=None)
    assert [type(event) for event in received] == [events.ApplicationPreFork]
    getpid.return_value = 456
    for handler in handlers:
        handler(sender="celery@localhost")
    assert [type(event) for event in received] == [
        events.ApplicationPreFork,
        events.ApplicationPostWorkerInit,
        events.ApplicationWorkerExit,
    ]
    assert all(event.registry is config.registry for event in received)
    assert config.registry.pyramid_forksafe["executed_hooks"] == {
        ("containers.celery.worker_before_create_process", "ApplicationPreFork"),
        ("containers.celery.worker_process_init", "ApplicationPostWorkerInit"),
        ("containers.celery.worker_process_shutdown", "ApplicationWorkerExit"),
    }
