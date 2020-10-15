from __future__ import print_function
from __future__ import unicode_literals

# stdlib
import re
import unittest
import pdb


# pyramid testing requirements
from pyramid import testing
from pyramid.exceptions import ConfigurationError
from pyramid.response import Response
from pyramid.request import Request

# local
from pyramid_forksafe.events import ApplicationPostFork


# ------------------------------------------------------------------------------


# used to ensure the toolbar link is injected into requests
re_toolbar_link = re.compile(r'(?:href="http://localhost)(/_debug_toolbar/[\d]+)"')


def empty_view(request):
    # create a view
    return Response(
        "<html><head></head><body>OK</body></html>", content_type="text/html"
    )


def post_fork_hook(event):
    """
    called when the registration has been Notified of the event
    this would be written by a user.

    to test invocations, we will stash a "_calls" entry in the dict
    """
    if "_calls" not in event.registry.pyramid_forksafe:
        event.registry.pyramid_forksafe["_calls"] = 0
    event.registry.pyramid_forksafe["_calls"] += 1


class _TestDebugtoolbarPanel_Core(object):
    def setUp(self, load_main_library=True):
        """
        base class for
        """
        self.config = config = testing.setUp()
        config.add_settings(
            {"debugtoolbar.includes": ["pyramid_forksafe.debugtoolbar"]}
        )
        config.include("pyramid_debugtoolbar")

        if load_main_library:
            # DO NOT LOAD THE MAIN LIBRARY
            # THIS IS TO TRIGGER AN EDGE CASE
            config.include("pyramid_forksafe")

        self.settings = config.registry.settings

        # add a view
        config.add_view(empty_view)

    def tearDown(self):
        testing.tearDown()

    def test_panel_injected(self):
        # make the app
        app = self.config.make_wsgi_app()
        # make a request
        req1 = Request.blank("/")
        req1.remote_addr = "127.0.0.1"
        resp1 = req1.get_response(app)
        self.assertEqual(resp1.status_code, 200)
        self.assertIn("http://localhost/_debug_toolbar/", resp1.text)

        # check the toolbar
        links = re_toolbar_link.findall(resp1.text)
        self.assertIsNotNone(links)
        self.assertIsInstance(links, list)
        self.assertEqual(len(links), 1)
        toolbar_link = links[0]

        req2 = Request.blank(toolbar_link)
        req2.remote_addr = "127.0.0.1"
        resp2 = req2.get_response(app)
        self.assertEqual(resp2.status_code, 200)

        self.assertIn('<li class="" id="pDebugPanel-Forksafe">', resp2.text)
        self.assertIn(
            '<div id="pDebugPanel-Forksafe-content" class="panelContent" style="display: none;">',
            resp2.text,
        )
        self.assertIn(
            """<div class="pDebugPanelTitle">
              <h3>Forksafe</h3>
            </div>""",
            resp2.text,
        )


class TestDebugtoolbarPanel_Incorrect(_TestDebugtoolbarPanel_Core, unittest.TestCase):
    def setUp(self):
        _TestDebugtoolbarPanel_Core.setUp(self, load_main_library=False)


class TestDebugtoolbarPanel_Correct(_TestDebugtoolbarPanel_Core, unittest.TestCase):
    def setUp(self):
        _TestDebugtoolbarPanel_Core.setUp(self, load_main_library=True)


class _TestInvoked_Base(object):

    include_file = None

    def setUp(self):
        self.config = config = testing.setUp()
        config.add_settings(
            {"debugtoolbar.includes": ["pyramid_forksafe.debugtoolbar"]}
        )
        config.include("pyramid_debugtoolbar")
        config.include(self.include_file)
        self.settings = config.registry.settings
        # add a view
        config.add_view(empty_view)
        # add our hook
        config.add_subscriber(post_fork_hook, ApplicationPostFork)

    def tearDown(self):
        testing.tearDown()

    def test_simple(self):
        # make the app
        app = self.config.make_wsgi_app()
        # make a request
        req1 = Request.blank("/")
        req1.remote_addr = "127.0.0.1"
        resp1 = req1.get_response(app)
        self.assertEqual(resp1.status_code, 200)
        self.assertIn("http://localhost/_debug_toolbar/", resp1.text)

        # check this is empty
        # we're not running in a container, so no hooks are run
        # we are checking for an empty set
        self.assertFalse(app.registry.pyramid_forksafe["executed_hooks"])

        # we should start this with never having an event
        # even if we run a subtest that uses the containers...
        # the events should never run because we do not actually fork
        _count_pre = app.registry.pyramid_forksafe.get("_calls", 0)
        self.assertEqual(_count_pre, 0)

        # mimic a fork
        _event = ApplicationPostFork(app.registry)
        app.registry.notify(_event)
        _count_post = app.registry.pyramid_forksafe.get("_calls", 0)
        self.assertEqual(_count_post, 1)


class TestInvoked_Generic(_TestInvoked_Base, unittest.TestCase):

    include_file = "pyramid_forksafe"


class TestInvoked_Uwsgi(_TestInvoked_Base, unittest.TestCase):

    include_file = "pyramid_forksafe.containers.uwsgi"
