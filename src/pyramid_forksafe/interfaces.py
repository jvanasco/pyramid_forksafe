from zope.interface import Attribute
from zope.interface import Interface

# ==============================================================================


class IApplicationPostFork(Interface):
    """
    An event type that is emitted whenever any :app:`Pyramid` forks.
    Called just after a worker has been forked.
    See the documentation attached to
    :class:`pyramid_forksafe.events.ApplicationPostFork` for more information.
    """

    registry = Attribute("Forked application registry")


class IApplicationPreFork(Interface):
    """
    An event type that is emitted whenever any :app:`Pyramid` forks.
    Called just before a worker is forked.
    See the documentation attached to
    :class:`pyramid_forksafe.events.ApplicationPreFork` for more information.
    """

    registry = Attribute("Forked application registry")


class IApplicationPostWorkerInit(Interface):
    """
    An event type that is emitted whenever any :app:`Pyramid` forks.
    Called just after a worker has initialized the application
    See the documentation attached to
    :class:`pyramid_forksafe.events.ApplicationPostFork` for more information.
    """

    registry = Attribute("Forked application registry")


class IApplicationWorkerInterrupt(Interface):
    """Emitted when Gunicorn calls its worker interrupt hook."""

    registry = Attribute("Application registry")


class IApplicationWorkerAbort(Interface):
    """Emitted when Gunicorn calls its worker abort hook."""

    registry = Attribute("Application registry")


class IApplicationWorkerExit(Interface):
    """Emitted when A server calls its exit hook in a worker process."""

    registry = Attribute("Application registry")


class IApplicationChildExit(Interface):
    """Emitted when The Gunicorn master reaps a worker."""

    registry = Attribute("Application registry")


__all__ = (
    "IApplicationWorkerInterrupt",
    "IApplicationWorkerAbort",
    "IApplicationWorkerExit",
    "IApplicationChildExit",
    "IApplicationPostFork",
    "IApplicationPreFork",
    "IApplicationPostWorkerInit",
)
