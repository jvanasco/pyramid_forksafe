# stdlib
import logging
from typing import TYPE_CHECKING

# local
from pyramid_forksafe.events import ApplicationPostFork
from pyramid_forksafe.events import ApplicationPostWorkerInit
from pyramid_forksafe.events import ApplicationPreFork

# typing
if TYPE_CHECKING:
    from pyramid.registry import Registry  # type: ignore[import]
    from gunicorn.workers.base import Worker  # type: ignore[import]

# ==============================================================================

log = logging.getLogger(__name__)

# ------------------------------------------------------------------------------


def mark_configured(registry: "Registry") -> None:
    """utility for developers to update the status"""
    log.debug("mark_configured")
    registry.pyramid_forksafe["environment"] = "gunicorn"
    registry.pyramid_forksafe["autoconfigure.log"].append("gunicorn mark_configured")
    registry.pyramid_forksafe["status"] = "gunicorn mark_configured"


def pre_fork(server, worker: "Worker") -> None:
    log.debug("ApplicationPreFork(gunicorn) - pre_fork")
    registry = server.app.wsgi().registry
    registry.notify(ApplicationPreFork(registry))
    registry.pyramid_forksafe["executed_hooks"].add(
        ("containers.gunicorn.pre_fork", "ApplicationPreFork")
    )


def post_fork(server, worker: "Worker") -> None:
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


__all__ = (
    "mark_configured",
    "post_fork",
    "post_worker_init",
    "pre_fork",
)
