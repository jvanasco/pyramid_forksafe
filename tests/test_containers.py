import os
import sys
from types import SimpleNamespace
from typing import Any, Callable, List, Type
from unittest.mock import Mock

import pytest
from pyramid.config import Configurator

from pyramid_forksafe import registry_setup
from pyramid_forksafe import events
from pyramid_forksafe.containers import gunicorn, uwsgi


@pytest.mark.parametrize(
    "hook,event_type,use_worker_app",
    [
        ("pre_fork", events.ApplicationPreFork, False),
        ("post_fork", events.ApplicationPostFork, False),
        ("post_worker_init", events.ApplicationPostWorkerInit, True),
        ("worker_int", events.ApplicationWorkerInterrupt, True),
        ("worker_abort", events.ApplicationWorkerAbort, True),
        ("worker_exit", events.ApplicationWorkerExit, True),
        ("child_exit", events.ApplicationChildExit, False),
    ],
)
def test_gunicorn_dispatch(
    hook: str, event_type: Type[Any], use_worker_app: bool
) -> None:
    """Each hook dispatches once to the registry for its process."""
    master, worker = Configurator(), Configurator()
    registry_setup(master)
    registry_setup(worker)
    master_app = master.make_wsgi_app()
    worker_app = worker.make_wsgi_app()
    master_loader = Mock(return_value=master_app)
    worker_loader = Mock(return_value=worker_app)
    server = SimpleNamespace(
        app=SimpleNamespace(wsgi=master_loader, callable=master_app),
        cfg=SimpleNamespace(preload_app=True),
    )
    process = SimpleNamespace(
        app=SimpleNamespace(wsgi=worker_loader), wsgi=worker_app, pid=os.getpid()
    )
    target, other = (worker, master) if use_worker_app else (master, worker)
    received: List[Any] = []
    target.registry.registerHandler(received.append, (event_type,))
    other.registry.registerHandler(Mock(side_effect=AssertionError), (event_type,))

    callback = getattr(gunicorn, hook)
    if hook in ("post_worker_init", "worker_int", "worker_abort"):
        callback(process)
    else:
        callback(server, process)

    assert len(received) == 1
    assert type(received[0]) is event_type
    assert received[0].registry is target.registry
    assert target.registry.pyramid_forksafe["executed_hooks"] == {
        ("containers.gunicorn." + hook, event_type.__name__)
    }
    assert not other.registry.pyramid_forksafe["executed_hooks"]
    if hook not in ("pre_fork", "post_fork", "post_worker_init"):
        master_loader.assert_not_called()
        worker_loader.assert_not_called()


def test_gunicorn_skips_unavailable_apps() -> None:
    """Signal and exit hooks tolerate workers that did not load an app."""
    load = Mock(side_effect=AssertionError)
    worker = SimpleNamespace(app=SimpleNamespace(wsgi=load), pid=os.getpid(), wsgi=None)
    server = SimpleNamespace(
        app=SimpleNamespace(wsgi=load, callable=None),
        cfg=SimpleNamespace(preload_app=True),
    )
    gunicorn.worker_int(worker)
    gunicorn.worker_abort(worker)
    gunicorn.worker_exit(server, worker)
    gunicorn.child_exit(server, worker)
    load.assert_not_called()


def test_gunicorn_exit_process_guards() -> None:
    """An exit observed in the wrong process cannot dispatch an event."""
    config = Configurator()
    registry_setup(config)
    app = config.make_wsgi_app()
    server = SimpleNamespace(
        app=SimpleNamespace(callable=app), cfg=SimpleNamespace(preload_app=False)
    )
    worker = SimpleNamespace(wsgi=app, pid=os.getpid() + 1)
    gunicorn.worker_exit(server, worker)
    gunicorn.child_exit(server, worker)
    assert not config.registry.pyramid_forksafe["executed_hooks"]


def test_uwsgi_postfork_registration(monkeypatch: "pytest.MonkeyPatch") -> None:
    """The registered callback emits a post-fork event on the app registry."""
    callbacks: List[Callable[[], None]] = []
    monkeypatch.setattr(uwsgi, "postfork", callbacks.append)
    config = Configurator()
    received: List[events.ApplicationPostFork] = []
    config.registry.registerHandler(received.append, (events.ApplicationPostFork,))
    uwsgi.includeme(config)
    assert len(callbacks) == 1
    callbacks[0]()
    assert len(received) == 1
    assert received[0].registry is config.registry
    assert config.registry.pyramid_forksafe["executed_hooks"] == {
        ("containers.uwsgi.post_fork_hook", "ApplicationPostFork")
    }


def test_uwsgi_worker_exit_registration(monkeypatch: "pytest.MonkeyPatch") -> None:
    """Opt-in registration chains the callback once and filters master exits."""
    previous = Mock()
    plugin = SimpleNamespace(atexit=previous, worker_id=Mock(return_value=0))
    monkeypatch.setitem(sys.modules, "uwsgi", plugin)
    config = Configurator()
    registry_setup(config)
    received: List[events.ApplicationWorkerExit] = []
    config.registry.registerHandler(received.append, (events.ApplicationWorkerExit,))

    uwsgi.configure_worker_exit(config)
    uwsgi.configure_worker_exit(config)
    plugin.atexit()
    previous.assert_called_once_with()
    assert not received

    plugin.worker_id.return_value = 1
    plugin.atexit()
    assert previous.call_count == 2
    assert len(received) == 1
    assert received[0].registry is config.registry
    assert config.registry.pyramid_forksafe["executed_hooks"] == {
        ("containers.uwsgi.worker_exit", "ApplicationWorkerExit")
    }

    config.registry.registerHandler(
        Mock(side_effect=RuntimeError), (events.ApplicationWorkerExit,)
    )
    with pytest.raises(RuntimeError):
        plugin.atexit()
    assert previous.call_count == 3
