import logging
log = logging.getLogger(__name__)


# local
from pyramid_forksafe.events import (
    ApplicationPostFork,
    ApplicationPreFork,
    ApplicationPostWorkerInit,
)


# ==============================================================================


def pre_fork(server, worker):
    log.debug("ApplicationPreFork(gunicorn) - pre_fork")
    registry = server.app.wsgi().registry
    registry.notify(ApplicationPreFork(registry))


def post_fork(server, worker):
    log.debug("ApplicationPostFork(gunicorn) - post_fork")
    registry = server.app.wsgi().registry
    registry.notify(ApplicationPostFork(registry))


def post_worker_init(worker):
    log.debug("ApplicationPostWorkerInit(gunicorn) - post_worker_init")
    registry = worker.app.wsgi().registry
    registry.notify(ApplicationPostWorkerInit(registry))
