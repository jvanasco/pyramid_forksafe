"""Minimal Pyramid app loaded by the live server tests."""

import os
from typing import Union

from pyramid.config import Configurator
from pyramid.request import Request
from pyramid.response import Response

from pyramid_forksafe import events
from pyramid_forksafe.containers.uwsgi import configure_worker_exit


def record(name: str) -> None:
    """Append one event and its process ID with a single write."""
    with open(os.environ["FORKSAFE_TEST_EVENTS"], "ab", buffering=0) as journal:
        journal.write("{} {}\n".format(name, os.getpid()).encode("ascii"))


def subscriber(
    event: Union[
        events.ApplicationPreFork,
        events.ApplicationPostFork,
        events.ApplicationPostWorkerInit,
        events.ApplicationWorkerInterrupt,
        events.ApplicationWorkerAbort,
        events.ApplicationWorkerExit,
        events.ApplicationChildExit,
    ],
) -> None:
    """Record an event delivered by a real server hook."""
    record(type(event).__name__)


def previous_uwsgi_exit() -> None:
    """Record execution of the pre-existing uWSGI exit callback."""
    record("previous_atexit")


def health(request: Request) -> Response:
    """Confirm that a worker is accepting requests."""
    return Response("ready")


config = Configurator()
config.include("pyramid_forksafe")
config.add_view(health)
for event_type in (
    events.ApplicationPreFork,
    events.ApplicationPostFork,
    events.ApplicationPostWorkerInit,
    events.ApplicationWorkerInterrupt,
    events.ApplicationWorkerAbort,
    events.ApplicationWorkerExit,
    events.ApplicationChildExit,
):
    config.add_subscriber(subscriber, event_type)

if os.environ["FORKSAFE_TEST_SERVER"] == "uwsgi":
    import uwsgi

    uwsgi.atexit = previous_uwsgi_exit
    configure_worker_exit(config)

application = config.make_wsgi_app()
