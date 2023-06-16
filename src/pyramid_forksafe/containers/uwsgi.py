# stdlib
import logging
from typing import TYPE_CHECKING

# pypi
try:
    from uwsgidecorators import postfork
except ImportError:
    postfork = None

# local
from pyramid_forksafe import registry_setup
from pyramid_forksafe.events import ApplicationPostFork

# typing
if TYPE_CHECKING:
    from pyramid.config import Configurator

# ==============================================================================

log = logging.getLogger(__name__)

# ------------------------------------------------------------------------------


def includeme(config: "Configurator") -> None:
    log.debug("Configuring ApplicationPostFork(uWSGI) - includeme")
    registry_setup(config)
    configure(config)


def configure(config: "Configurator") -> None:
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
    "configure",
    "includeme",
)
