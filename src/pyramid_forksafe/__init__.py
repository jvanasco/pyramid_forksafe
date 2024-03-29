# stydlib
import logging
from typing import TYPE_CHECKING

# typing
if TYPE_CHECKING:
    from pyramid.config import Configurator

# ==============================================================================

__VERSION__ = "0.2.0"

# ------------------------------------------------------------------------------

log = logging.getLogger(__name__)

# ------------------------------------------------------------------------------


def registry_setup(config: "Configurator") -> None:
    """
    This function does the initial setup.
    Originally it was part of `includeme`, but has been migrated away so
    per-container setups can be used instead.
    """
    log.debug("registry_setup")
    config.registry.pyramid_forksafe = {
        "status": "attempting auto-configure",
        "autoconfigure.log": [],
        "environment": None,
        "executed_hooks": set([]),
    }


def includeme(config: "Configurator") -> None:
    """
    this will try to auto-detect supported containers

    uWSGI will only load when run under that environment.

    gunicorn must run with the hooks enabled in it's own startup
    """
    registry_setup(config)
    log.debug("attempting auto-configure")
    # uWSGI autoconfiguration
    try:
        log.debug("attempting to autoconfigure uWSGI")
        import pyramid_forksafe.containers.uwsgi

        pyramid_forksafe.containers.uwsgi.configure(config)

        log.debug("- uWSGI no error")
    except Exception as exc:
        config.registry.pyramid_forksafe["autoconfigure.log"].append(
            "uWSGI error: %s" % exc
        )
        config.registry.pyramid_forksafe["status"] = "uWSGI error"
        log.error("- uWSGI EXCEPTION | %s", exc)


__all__ = (
    "__VERSION__",
    "includeme",
    "registry_setup",
)
