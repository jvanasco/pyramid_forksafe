from zope.interface import (
    Attribute,
    Interface,
    )


# ==============================================================================


class IApplicationPostFork(Interface):
    """
    An event type that is emitted whenever any :app:`Pyramid` forks.
    See the documentation attached to 
    :class:`pyramid_forksafe.events.ApplicationPostFork` for more information.
    """
    config = Attribute('Forked application config')


class IApplicationPreFork(Interface):
    """
    An event type that is emitted whenever any :app:`Pyramid` forks.
    See the documentation attached to 
    :class:`pyramid_forksafe.events.ApplicationPreFork` for more information.
    """
    config = Attribute('Forked application config')
