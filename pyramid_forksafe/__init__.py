import logging
log = logging.getLogger(__name__)


__VERSION__ = '0.1.0'


# ==============================================================================


def includeme(config):
    """
    this will try to auto-detect supported containers

    uWSGI will only load when run under that environment.

    gunicorn must run with the hooks enabled in it's own startup
    """
    log.debug("Trying to auto-configure")

    try:
        # import uwsgi
        log.debug("attempting to autoconfigure uwsgi")
        log.debug("- uwsgi available")
        import pyramid_forksafe.containers.uwsgi
        pyramid_forksafe.containers.uwsgi.includeme(config)
    except:
        log.debug("- uwsgi not available")
