import logging
log = logging.getLogger(__name__)


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
        import pyramid_forksafe.containers.uwsgi
        pyramid_forksafe.containers.uwsgi.includeme(config)
        log.debug("- uwsgi configured")
    except:
        log.debug("- uwsgi not available")
