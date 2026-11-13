# stdlib
from typing import TYPE_CHECKING

# pypi
from zope.interface import implementer

# local
from .interfaces import IApplicationPostFork
from .interfaces import IApplicationPostWorkerInit
from .interfaces import IApplicationPreFork

from .interfaces import IApplicationWorkerInterrupt
from .interfaces import IApplicationWorkerAbort
from .interfaces import IApplicationWorkerExit
from .interfaces import IApplicationChildExit

# typing
if TYPE_CHECKING:
    from pyramid.registry import Registry

# ==============================================================================


@implementer(IApplicationPostFork)
class ApplicationPostFork(object):
    """An instance of this class is emitted as an :term:`event` when
    the application forks is
    called.

    Called just after a worker has been forked.

    The instance has an attribute, ``registry``, which corresponds to
    the current registry.

    This class implements the
    :class:`pyramid_forksafe.interfaces.IApplicationPostFork` interface.
    """

    def __init__(self, registry: "Registry"):
        print("ApplicationPostFork")
        self.registry = registry


@implementer(IApplicationPreFork)
class ApplicationPreFork(object):
    """An instance of this class is emitted as an :term:`event` when
    the application forks is called.

    Called just before a worker has been forked.

    The instance has an attribute, ``registry``, which corresponds to
    the current registry.

    This class implements the
    :class:`pyramid_forksafe.interfaces.IApplicationPreFork` interface.
    """

    def __init__(self, registry: "Registry"):
        print("ApplicationPreFork")
        self.registry = registry


@implementer(IApplicationPostWorkerInit)
class ApplicationPostWorkerInit(object):
    """An instance of this class is emitted as an :term:`event` when
    the application forks is called.

    Called just after a worker has initialized the application

    The instance has an attribute, ``registry``, which corresponds to
    the current registry.

    This class implements the
    :class:`pyramid_forksafe.interfaces.IApplicationPostWorkerInit` interface.
    """

    def __init__(self, registry: "Registry"):
        print("ApplicationPostWorkerInit")
        self.registry = registry


@implementer(IApplicationWorkerInterrupt)
class ApplicationWorkerInterrupt:
    """Emitted when Gunicorn calls its worker interrupt hook."""

    def __init__(self, registry: "Registry") -> None:
        self.registry = registry


@implementer(IApplicationWorkerAbort)
class ApplicationWorkerAbort:
    """Emitted when Gunicorn calls its worker abort hook."""

    def __init__(self, registry: "Registry") -> None:
        self.registry = registry


@implementer(IApplicationWorkerExit)
class ApplicationWorkerExit:
    """Emitted when A server calls its exit hook in a worker process."""

    def __init__(self, registry: "Registry") -> None:
        self.registry = registry


@implementer(IApplicationChildExit)
class ApplicationChildExit:
    """Emitted when The Gunicorn master reaps a worker."""

    def __init__(self, registry: "Registry") -> None:
        self.registry = registry


__all__ = (
    "ApplicationWorkerInterrupt",
    "ApplicationWorkerAbort",
    "ApplicationWorkerExit",
    "ApplicationChildExit",
    "ApplicationPostFork",
    "ApplicationPreFork",
    "ApplicationPostWorkerInit",
)
