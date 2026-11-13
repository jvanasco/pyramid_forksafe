"""Bridge Celery prefork lifecycle signals to a Pyramid registry."""

import os
from typing import TYPE_CHECKING, Any, Type, Union

from pyramid_forksafe import registry_setup
from pyramid_forksafe.events import ApplicationPostWorkerInit
from pyramid_forksafe.events import ApplicationPreFork
from pyramid_forksafe.events import ApplicationWorkerExit

if TYPE_CHECKING:
    from pyramid.config import Configurator


def configure(config: "Configurator") -> None:
    """Register process-wide signal receivers before starting a prefork worker."""
    from celery import signals

    registry = config.registry
    if not hasattr(registry, "pyramid_forksafe"):
        registry_setup(config)
    state = registry.pyramid_forksafe
    if state.get("celery_configured"):
        return

    parent_pid = os.getpid()

    def notify(
        event_type: Type[
            Union[ApplicationPreFork, ApplicationPostWorkerInit, ApplicationWorkerExit]
        ],
        hook: str,
    ) -> None:
        """Dispatch the event and record successful delivery."""
        registry.notify(event_type(registry))
        state["executed_hooks"].add(("containers.celery." + hook, event_type.__name__))

    def before_create_process(**kwargs: Any) -> None:
        """Notify the worker parent before a pool child is created."""
        if os.getpid() == parent_pid:
            notify(ApplicationPreFork, "worker_before_create_process")

    def process_init(**kwargs: Any) -> None:
        """Notify a prefork child after initialization."""
        if os.getpid() != parent_pid:
            notify(ApplicationPostWorkerInit, "worker_process_init")

    def process_shutdown(**kwargs: Any) -> None:
        """Notify a prefork child before shutdown."""
        if os.getpid() != parent_pid:
            notify(ApplicationWorkerExit, "worker_process_shutdown")

    signals.worker_before_create_process.connect(before_create_process, weak=False)
    signals.worker_process_init.connect(process_init, weak=False)
    signals.worker_process_shutdown.connect(process_shutdown, weak=False)
    state["celery_configured"] = True
    state["environment"] = "Celery"
    state["status"] = "Celery hooks configured"
    state["autoconfigure.log"].append("Celery hooks configured")


__all__ = ("configure",)
