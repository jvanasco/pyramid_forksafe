from pyramid_debugtoolbar.panels import DebugPanel

_ = lambda x: x


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

    def __init__(self, request):
        if hasattr(request.registry, "pyramid_forksafe"):
            self.data = {"registry_data": request.registry.pyramid_forksafe}
        else:
            # this can happen if we include the toolbar, but not the library
            self.data = {"registry_data": None}

    @property
    def nav_title(self):
        return _(self.name)

    @property
    def title(self):
        return _(self.name)

    @property
    def url(self):
        return ""

    def render_content(self, request):
        return DebugPanel.render_content(self, request)
