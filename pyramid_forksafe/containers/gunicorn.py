import logging

log = logging.getLogger(__name__)


# local
from pyramid_forksafe.events import (
    ApplicationPostFork,
    ApplicationPreFork,
    ApplicationPostWorkerInit,
)


# ==============================================================================


def mark_configured(registry):
    """utility for developers to update the status"""
    log.debug("mark_configured")
    registry.pyramid_forksafe["environment"] = "gunicorn"
    registry.pyramid_forksafe["autoconfigure.log"].append("gunicorn mark_configured")
    registry.pyramid_forksafe["status"] = "gunicorn mark_configured"


def pre_fork(server, worker):
    log.debug("ApplicationPreFork(gunicorn) - pre_fork")
    registry = server.app.wsgi().registry
    registry.notify(ApplicationPreFork(registry))
    registry.pyramid_forksafe["executed_hooks"].add(
        ("containers.gunicorn.pre_fork", "ApplicationPreFork")
    )


def post_fork(server, worker):
    log.debug("ApplicationPostFork(gunicorn) - post_fork")
    registry = server.app.wsgi().registry
    registry.notify(ApplicationPostFork(registry))
    registry.pyramid_forksafe["executed_hooks"].add(
        ("containers.gunicorn.post_fork", "ApplicationPostFork")
    )


def post_worker_init(worker):
    log.debug("ApplicationPostWorkerInit(gunicorn) - post_worker_init")
    registry = worker.app.wsgi().registry
    registry.notify(ApplicationPostWorkerInit(registry))
    registry.pyramid_forksafe["executed_hooks"].add(
        ("containers.gunicorn.post_worker_init", "ApplicationPostWorkerInit")
    )


__all__ = ("mark_configured", "pre_fork", "post_fork", "post_worker_init")
