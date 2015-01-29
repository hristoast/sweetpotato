import sys

from sweetpotato.common import *
from sweetpotato.core import error_and_die
from sweetpotato.web import SweetpotatoDaemon

try:
    from daemon import runner
except ImportError:
    runner = None


__all__ = ['daemon_action', 'run_daemon']


def daemon_action(action):
    s = _setup_daemon()
    if runner:
        sys.argv.insert(1, action)
        daemon_runner = runner.DaemonRunner(s)
        daemon_runner.do_action()
    else:
        error_and_die(DAEMON_PY3K_ERROR)


def _ensure_default_log_dir():
    if not os.path.isdir(DEFAULT_LOG_DIR):
        os.makedirs(DEFAULT_LOG_DIR)


def _ensure_default_run_dir():
    if not os.path.isdir(os.path.dirname(DEFAULT_PIDFILE)):
        os.makedirs(os.path.dirname(DEFAULT_PIDFILE))


def run_daemon():
    s = _setup_daemon()
    if runner:
        daemon_runner = runner.DaemonRunner(s)
        daemon_runner.do_action()
    else:
        # TODO: warning about requiring patched version
        error_and_die(DAEMON_PY3K_ERROR)


def _setup_daemon():
    _ensure_default_log_dir()
    _ensure_default_run_dir()
    s = SweetpotatoDaemon()
    s.configure()
    return s
