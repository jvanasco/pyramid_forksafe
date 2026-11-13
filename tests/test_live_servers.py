"""Opt-in lifecycle checks against real Gunicorn and uWSGI processes."""

import os
import shutil
import signal
import socket
import subprocess
import sys
import sysconfig
import tempfile
import time
from pathlib import Path
from typing import Iterator, List, Mapping, Optional, Tuple

import pytest

pytestmark = pytest.mark.skipif(
    os.name != "posix" or os.environ.get("FORKSAFE_LIVE_TESTS") != "1",
    reason="set FORKSAFE_LIVE_TESTS=1 on POSIX to test real servers",
)

GUNICORN_CONFIG = """\
from pyramid_forksafe.containers.gunicorn import (
    child_exit, post_fork, post_worker_init, pre_fork,
    worker_abort, worker_exit, worker_int,
)
"""


class LiveServer:
    """Run one server and collect its lifecycle journal and logs."""

    def __init__(
        self,
        directory: Path,
        name: str,
        arguments: List[str],
        env_overrides: Optional[Mapping[str, str]] = None,
    ) -> None:
        executable = shutil.which(name)
        if executable is None:
            pytest.fail("{} is required for the live server tests".format(name))

        self.journal = directory / "events"
        self.journal.touch()
        self.log = directory / "server.log"
        self.socket = directory / "server.sock"
        env = os.environ.copy()
        env["FORKSAFE_TEST_EVENTS"] = str(self.journal)
        env["FORKSAFE_TEST_SERVER"] = name
        env["PYTHONPATH"] = os.pathsep.join(
            [
                str(Path(__file__).resolve().parent),
                str(Path(__file__).resolve().parents[1]),
                sysconfig.get_path("purelib"),
            ]
            + [
                str(Path(path).resolve())
                for path in env.get("PYTHONPATH", "").split(os.pathsep)
                if path
            ]
        )
        if name == "uwsgi" and Path(executable).parent != Path(sys.executable).parent:
            # A global pip installation ships uwsgidecorators beside its own Python.
            base_packages = sysconfig.get_path(
                "purelib", vars={"base": sys.base_prefix}
            )
            env["PYTHONPATH"] += os.pathsep + base_packages
        if env_overrides is not None:
            env.update(env_overrides)
        with self.log.open("wb") as output:
            self.process = subprocess.Popen(
                [executable] + arguments,
                cwd=str(directory),
                env=env,
                stdout=output,
                stderr=subprocess.STDOUT,
                start_new_session=True,
            )

    def fail(self, message: str) -> None:
        """Report a failure with the event journal and server output."""
        pytest.fail(
            "{}\nEvents:\n{}\nServer log:\n{}".format(
                message, self.journal.read_text(), self.log.read_text(errors="replace")
            )
        )

    def events(self) -> List[Tuple[str, int]]:
        """Read complete event records while workers are writing."""
        return [
            (name, int(pid))
            for name, pid in (
                line.split() for line in self.journal.read_text().split("\n")[:-1]
            )
        ]

    def wait_for_event(self, name: str, pid: int = 0) -> int:
        """Wait for an event, optionally from a specific process."""
        deadline = time.monotonic() + 15
        while time.monotonic() < deadline:
            for event, sender in self.events():
                if event == name and (not pid or sender == pid):
                    return sender
            if self.process.poll() is not None:
                break
            time.sleep(0.05)
        self.fail("Missing {} from PID {}".format(name, pid or "any"))
        raise AssertionError("unreachable")

    def wait_until_serving(self) -> None:
        """Wait until a worker responds over the Unix socket."""
        deadline = time.monotonic() + 15
        while time.monotonic() < deadline and self.process.poll() is None:
            try:
                with socket.socket(socket.AF_UNIX) as client:
                    client.settimeout(0.5)
                    client.connect(str(self.socket))
                    client.sendall(b"GET / HTTP/1.0\r\nHost: localhost\r\n\r\n")
                    if b" 200 " in client.recv(4096).split(b"\r\n", 1)[0]:
                        return
            except OSError:
                time.sleep(0.05)
        self.fail("Worker did not serve a request")

    def close(self) -> None:
        """Terminate and reap the server and stop any remaining workers."""
        try:
            self.process.send_signal(signal.SIGTERM)
            self.process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            pass
        finally:
            try:
                os.killpg(self.process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            self.process.wait(timeout=5)


@pytest.fixture
def server_directory() -> Iterator[Path]:
    """Create a short working directory for Unix-domain sockets."""
    with tempfile.TemporaryDirectory(prefix="forksafe-", dir="/tmp") as directory:
        yield Path(directory)


@pytest.mark.parametrize(
    "worker_signal,event",
    [
        (getattr(signal, "SIGQUIT", 3), "ApplicationWorkerInterrupt"),
        (signal.SIGABRT, "ApplicationWorkerAbort"),
    ],
)
def test_gunicorn_lifecycle(
    server_directory: Path, worker_signal: int, event: str
) -> None:
    """Gunicorn dispatches startup and exit events in their owning processes."""
    (server_directory / "gunicorn.conf.py").write_text(GUNICORN_CONFIG)
    server = LiveServer(
        server_directory,
        "gunicorn",
        [
            "--preload",
            "--workers",
            "1",
            "--bind",
            "unix:server.sock",
            "server_app:application",
        ],
    )
    try:
        master = server.process.pid
        worker = server.wait_for_event("ApplicationPostWorkerInit")
        assert worker != master
        os.kill(worker, worker_signal)
        server.wait_for_event("ApplicationChildExit", master)
        expected = [
            ("ApplicationPreFork", master),
            ("ApplicationPostFork", worker),
            ("ApplicationPostWorkerInit", worker),
            (event, worker),
            ("ApplicationWorkerExit", worker),
            ("ApplicationChildExit", master),
        ]
        if server.events()[: len(expected)] != expected:
            server.fail("Unexpected Gunicorn lifecycle events")
    finally:
        server.close()


def test_uwsgi_graceful_reload(server_directory: Path) -> None:
    """uWSGI dispatches post-fork and chains the old worker's exit callback."""
    server = LiveServer(
        server_directory,
        "uwsgi",
        [
            "--master",
            "--workers",
            "1",
            "--http-socket",
            "server.sock",
            "--wsgi-file",
            str(Path(__file__).with_name("server_app.py").resolve()),
            "--virtualenv",
            sys.prefix,
            "--need-app",
            "--die-on-term",
        ],
    )
    try:
        worker = server.wait_for_event("ApplicationPostFork")
        assert worker != server.process.pid
        server.wait_until_serving()
        server.process.send_signal(signal.SIGHUP)
        server.wait_for_event("previous_atexit", worker)
        expected = [
            ("ApplicationPostFork", worker),
            ("ApplicationWorkerExit", worker),
            ("previous_atexit", worker),
        ]
        if server.events()[: len(expected)] != expected:
            server.fail("Unexpected uWSGI lifecycle events")
    finally:
        server.close()


@pytest.fixture
def celery_broker(
    server_directory: Path, monkeypatch: "pytest.MonkeyPatch"
) -> Iterator[None]:
    """Start an isolated Redis broker on a private Unix socket."""
    broker_dir = server_directory / "redis"
    broker_dir.mkdir()
    address = broker_dir / "broker.sock"
    broker = LiveServer(
        broker_dir,
        "redis-server",
        [
            "--port",
            "0",
            "--unixsocket",
            str(address),
            "--save",
            "",
            "--appendonly",
            "no",
        ],
        env_overrides={"LC_ALL": "C"},
    )
    try:
        deadline = time.monotonic() + 10
        while not address.exists():
            if broker.process.poll() is not None or time.monotonic() >= deadline:
                broker.fail("Redis did not create its Unix socket")
            time.sleep(0.05)
        monkeypatch.setenv("FORKSAFE_TEST_BROKER", "redis+socket://" + str(address))
        yield
    finally:
        broker.close()


def test_celery_prefork_lifecycle(server_directory: Path, celery_broker: None) -> None:
    """Celery delivers prefork events in the parent and child processes."""
    server = LiveServer(
        server_directory,
        "celery",
        [
            "-A",
            "tests.celery_app:app",
            "worker",
            "--pool=prefork",
            "--concurrency=1",
            "--without-gossip",
            "--without-mingle",
            "--without-heartbeat",
        ],
    )
    try:
        parent = server.process.pid
        child = server.wait_for_event("ApplicationPostWorkerInit")
        assert child != parent
        server.wait_for_event("worker_ready", parent)
        server.process.send_signal(signal.SIGTERM)
        server.wait_for_event("ApplicationWorkerExit", child)
        try:
            status = server.process.wait(timeout=15)
        except subprocess.TimeoutExpired:
            server.fail("Celery did not complete warm shutdown")
            return
        expected = [
            ("ApplicationPreFork", parent),
            ("ApplicationPostWorkerInit", child),
            ("ApplicationWorkerExit", child),
        ]
        events = [entry for entry in server.events() if entry[0] != "worker_ready"]
        if status != 0 or events != expected:
            server.fail("Unexpected Celery lifecycle events or exit status")
    finally:
        server.close()
