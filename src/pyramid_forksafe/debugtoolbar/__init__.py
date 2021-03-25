from .panels.forksafe import PyramidForksafeDebugPanel


def includeme(config):
    """
    Pyramid API hook
    """
    config.add_debugtoolbar_panel(PyramidForksafeDebugPanel)
