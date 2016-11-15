from zope.interface import (
    Attribute,
    Interface,
    )


# ==============================================================================


class IApplicationPostFork(Interface):
    """
    An event type that is emitted whenever any :app:`Pyramid` forks.
    Called just after a worker has been forked.
    See the documentation attached to
    :class:`pyramid_forksafe.events.ApplicationPostFork` for more information.
    """
    registry = Attribute('Forked application registry')


class IApplicationPreFork(Interface):
    """
    An event type that is emitted whenever any :app:`Pyramid` forks.
    Called just before a worker is forked.
    See the documentation attached to
    :class:`pyramid_forksafe.events.ApplicationPreFork` for more information.
    """
    registry = Attribute('Forked application registry')


class IApplicationPostWorkerInit(Interface):
    """
    An event type that is emitted whenever any :app:`Pyramid` forks.
    Called just after a worker has initialized the application
    See the documentation attached to
    :class:`pyramid_forksafe.events.ApplicationPostFork` for more information.
    """
    registry = Attribute('Forked application registry')
