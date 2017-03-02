import logging
log = logging.getLogger(__name__)

# pypi
try:
    from uwsgidecorators import postfork
except ImportError as e:
    postfork = None

# local
from pyramid_forksafe.events import (
    ApplicationPostFork,
)


# ==============================================================================


def includeme(config):
    log.debug("Configuring ApplicationPostFork(uwsgi)")
    
    if postfork is None:
        log.debug("Could not setup for uwsgi environment")
    
    else:

        @postfork
        def post_fork_hook():
            log.debug("ApplicationPostFork(uwsgi) - notify")
            registry = config.registry
            registry.notify(ApplicationPostFork(registry))
