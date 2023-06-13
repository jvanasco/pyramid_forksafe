# stdlib
from typing import TYPE_CHECKING

# pypi
from zope.interface import implementer  # type: ignore[import]

# local
from .interfaces import IApplicationPostFork
from .interfaces import IApplicationPostWorkerInit
from .interfaces import IApplicationPreFork

# typing
if TYPE_CHECKING:
    from pyramid.registry import Registry  # type: ignore[import]

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


__all__ = (
    "ApplicationPostFork",
    "ApplicationPreFork",
    "ApplicationPostWorkerInit",
)
