import logging

log = logging.getLogger(__name__)

# pypi
try:
    from uwsgidecorators import postfork
except ImportError as e:
    postfork = None

# local
from pyramid_forksafe import registry_setup
from pyramid_forksafe.events import ApplicationPostFork


# ==============================================================================


def includeme(config):
    log.debug("Configuring ApplicationPostFork(uWSGI) - includeme")
    registry_setup(config)
    configure(config)


def configure(config):
    log.debug("Configuring ApplicationPostFork(uWSGI) - configure")

    if postfork is None:
        log.debug("Could not setup for uWSGI environment")
        config.registry.pyramid_forksafe["autoconfigure.log"].append(
            "uWSGI not available"
        )

    else:
        config.registry.pyramid_forksafe["autoconfigure.log"].append("uWSGI available")
        config.registry.pyramid_forksafe["environment"] = "uWSGI"

        @postfork
        def post_fork_hook():
            log.debug("ApplicationPostFork(uWSGI) - notify")
            registry = config.registry
            registry.notify(ApplicationPostFork(registry))
            config.registry.pyramid_forksafe["executed_hooks"].add(
                ("containers.uwsgi.post_fork_hook", "ApplicationPostFork")
            )

        config.registry.pyramid_forksafe["autoconfigure.log"].append(
            "uWSGI hook configured"
        )
        config.registry.pyramid_forksafe["status"] = "uWSGI hook configured"


__all__ = (
    "includeme",
    "configure",
)
