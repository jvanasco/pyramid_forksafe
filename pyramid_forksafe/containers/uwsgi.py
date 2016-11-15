import logging
log = logging.getLogger(__name__)

# pypi
from uwsgidecorators import postfork

# local
from pyramid_forksafe.events import (
    ApplicationPostFork,
)


# ==============================================================================


def includeme(config):
    log.debug("Configuring ApplicationPostFork(uwsgi)")

    @postfork
    def post_fork_hook():
        log.debug("ApplicationPostFork(uwsgi) - notify")
        registry = config.registry
        registry.notify(ApplicationPostFork(registry))
