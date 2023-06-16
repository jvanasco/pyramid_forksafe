# stdlib
from typing import TYPE_CHECKING

# pypi
from pyramid_debugtoolbar.panels import DebugPanel

# typing
if TYPE_CHECKING:
    from pyramid.request import Request

# ==============================================================================


class PyramidForksafeDebugPanel(DebugPanel):
    """
    Sample debug panel
    """

    name = "Forksafe"
    has_content = True
    template = "pyramid_forksafe.debugtoolbar.panels:templates/forksafe.dbtmako"

    # only query the policy once
    _policy = None

    # stash
    _cookie_names = None

    def __init__(self, request: "Request"):
        if hasattr(request.registry, "pyramid_forksafe"):
            self.data = {"registry_data": request.registry.pyramid_forksafe}
        else:
            # this can happen if we include the toolbar, but not the library
            self.data = {"registry_data": None}

    @property
    def nav_title(self) -> str:
        return self.name

    @property
    def title(self) -> str:
        return self.name

    @property
    def url(self) -> str:
        return ""

    def render_content(self, request: "Request") -> str:
        return DebugPanel.render_content(self, request)
