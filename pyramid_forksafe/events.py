from zope.interface import (
    implementer,
    )


from pyramid_forksafe.interfaces import (
    IApplicationPostFork,
    IApplicationPreFork,
    IApplicationPostWorkerInit,
)


# ==============================================================================


@implementer(IApplicationPostFork)
class ApplicationPostFork(object):
    """ An instance of this class is emitted as an :term:`event` when
    the application forks is
    called.

    Called just after a worker has been forked.

    The instance has an attribute, ``registry``, which corresponds to
    the current registry.

    This class implements the
    :class:`pyramid_forksafe.interfaces.IApplicationPostFork` interface.
    """
    def __init__(self, registry):
        self.registry = registry


@implementer(IApplicationPreFork)
class ApplicationPreFork(object):
    """ An instance of this class is emitted as an :term:`event` when
    the application forks is called.

    Called just before a worker has been forked.

    The instance has an attribute, ``registry``, which corresponds to
    the current registry.

    This class implements the
    :class:`pyramid_forksafe.interfaces.IApplicationPreFork` interface.
    """
    def __init__(self, registry):
        self.registry = registry


@implementer(IApplicationPostWorkerInit)
class ApplicationPostWorkerInit(object):
    """ An instance of this class is emitted as an :term:`event` when
    the application forks is called.

    Called just after a worker has initialized the application

    The instance has an attribute, ``registry``, which corresponds to
    the current registry.

    This class implements the
    :class:`pyramid_forksafe.interfaces.IApplicationPostWorkerInit` interface.
    """
    def __init__(self, registry):
        self.registry = registry
