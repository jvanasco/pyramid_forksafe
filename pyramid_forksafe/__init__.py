import logging
log = logging.getLogger(__name__)


# ==============================================================================


def includeme(config):
    log.debug("Trying to auto-configure")
    
    try:
        # import uwsgi
        import pyramid_forksafe.containers.uwsgi
        pyramid_forksafe.containers.uwsgi.includeme(config)
        log.debug("- uwsgi configured")
    except:
        log.debug("- uwsgi not available")
