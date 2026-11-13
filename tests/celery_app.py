"""Celery app loaded by the live prefork test."""

import os
from typing import Any

from billiard import set_start_method
from celery import Celery, signals

from pyramid_forksafe.containers.celery import configure
from tests.server_app import config, record

app = Celery("forksafe_test", broker=os.environ["FORKSAFE_TEST_BROKER"])
app.conf.worker_pool_start_method = "fork"
# Billiard defaults to spawn on macOS even when Celery enables forking.
set_start_method("fork", force=True)
configure(config)


@signals.worker_ready.connect
def record_ready(**kwargs: Any) -> None:
    """Record when the parent is ready for warm shutdown."""
    record("worker_ready")
