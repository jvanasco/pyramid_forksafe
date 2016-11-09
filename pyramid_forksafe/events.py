from zope.interface import (
    implementer,
    Interface,
    )


from pyramid_forksafe.interfaces import (
    IApplicationPostFork,
    IApplicationPreFork,
)


# ==============================================================================


@implementer(IApplicationPostFork)
class ApplicationPostFork(object):
    """ An instance of this class is emitted as an :term:`event` when
    the application forks is
    called.  The instance has an attribute, ``app``, which is an
    instance of the :term:`router` that will handle WSGI requests.
    This class implements the
    :class:`pyramid_forksafe.interfaces.IApplicationPostFork` interface.
    """
    def __init__(self, config):
        self.config = config


@implementer(IApplicationPreFork)
class ApplicationPreFork(object):
    """ An instance of this class is emitted as an :term:`event` when
    the application forks is
    called.  The instance has an attribute, ``app``, which is an
    instance of the :term:`router` that will handle WSGI requests.
    This class implements the
    :class:`pyramid_forksafe.interfaces.IApplicationPreFork` interface.
    """
    def __init__(self, config):
        self.config = config
