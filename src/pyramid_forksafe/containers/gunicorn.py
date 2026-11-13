# stdlib
import logging
import os
from typing import Any, TYPE_CHECKING, Type, Union

# local
from pyramid_forksafe.events import ApplicationChildExit
from pyramid_forksafe.events import ApplicationWorkerAbort
from pyramid_forksafe.events import ApplicationWorkerExit
from pyramid_forksafe.events import ApplicationWorkerInterrupt
from pyramid_forksafe.events import ApplicationPostFork
from pyramid_forksafe.events import ApplicationPostWorkerInit
from pyramid_forksafe.events import ApplicationPreFork

# typing
if TYPE_CHECKING:
    from pyramid.registry import Registry
    from gunicorn.arbiter import Arbiter
    from gunicorn.workers.base import Worker

# ==============================================================================

log = logging.getLogger(__name__)

# ------------------------------------------------------------------------------


def mark_configured(registry: "Registry") -> None:
    """utility for developers to update the status"""
    log.debug("mark_configured")
    registry.pyramid_forksafe["environment"] = "gunicorn"
    registry.pyramid_forksafe["autoconfigure.log"].append("gunicorn mark_configured")
    registry.pyramid_forksafe["status"] = "gunicorn mark_configured"


def pre_fork(server: "Arbiter", worker: "Worker") -> None:
    log.debug("ApplicationPreFork(gunicorn) - pre_fork")
    registry = server.app.wsgi().registry
    registry.notify(ApplicationPreFork(registry))
    registry.pyramid_forksafe["executed_hooks"].add(
        ("containers.gunicorn.pre_fork", "ApplicationPreFork")
    )


def post_fork(server: "Arbiter", worker: "Worker") -> None:
    log.debug("ApplicationPostFork(gunicorn) - post_fork")
    registry = server.app.wsgi().registry
    registry.notify(ApplicationPostFork(registry))
    registry.pyramid_forksafe["executed_hooks"].add(
        ("containers.gunicorn.post_fork", "ApplicationPostFork")
    )


def post_worker_init(worker: "Worker") -> None:
    log.debug("ApplicationPostWorkerInit(gunicorn) - post_worker_init")
    registry = worker.app.wsgi().registry
    registry.notify(ApplicationPostWorkerInit(registry))
    registry.pyramid_forksafe["executed_hooks"].add(
        ("containers.gunicorn.post_worker_init", "ApplicationPostWorkerInit")
    )


def _notify_loaded_app(
    app: Any,
    event_type: Type[
        Union[
            ApplicationChildExit,
            ApplicationWorkerAbort,
            ApplicationWorkerExit,
            ApplicationWorkerInterrupt,
        ]
    ],
    hook: str,
) -> None:
    """Dispatch to a configured Pyramid registry on an already-loaded app."""
    registry = getattr(app, "registry", None)
    state = getattr(registry, "pyramid_forksafe", None)
    if registry is None or state is None:
        return

    registry.notify(event_type(registry))
    state["executed_hooks"].add(("containers.gunicorn." + hook, event_type.__name__))


def worker_int(worker: "Worker") -> None:
    """Notify the loaded worker app when Gunicorn handles SIGINT or SIGQUIT."""
    _notify_loaded_app(
        getattr(worker, "wsgi", None), ApplicationWorkerInterrupt, "worker_int"
    )


def worker_abort(worker: "Worker") -> None:
    """Notify the loaded worker app when Gunicorn handles SIGABRT."""
    _notify_loaded_app(
        getattr(worker, "wsgi", None), ApplicationWorkerAbort, "worker_abort"
    )


def worker_exit(server: "Arbiter", worker: "Worker") -> None:
    """Notify the loaded worker app from the exiting worker process."""
    if worker.pid == os.getpid():
        _notify_loaded_app(
            getattr(worker, "wsgi", None), ApplicationWorkerExit, "worker_exit"
        )


def child_exit(server: "Arbiter", worker: "Worker") -> None:
    """Notify the preloaded master app after Gunicorn reaps a worker."""
    if server.cfg.preload_app:
        _notify_loaded_app(server.app.callable, ApplicationChildExit, "child_exit")


__all__ = (
    "child_exit",
    "worker_abort",
    "worker_exit",
    "worker_int",
    "mark_configured",
    "post_fork",
    "post_worker_init",
    "pre_fork",
)
