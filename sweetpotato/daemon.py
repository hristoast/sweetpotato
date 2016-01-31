try:
    import bottle
except ImportError:
    bottle = None
import configparser
import os
import sys

try:
    from lockfile import LockTimeout
except ImportError:
    LockTimeout = None
from .common import (DAEMON_PY3K_ERROR, DEFAULT_CONF_FILE, DEFAULT_LOG_DIR, DEFAULT_LOG_FILE,
                     DEFAULT_PIDFILE, DEFAULT_PIDFILE_TIMEOUT, PROGNAME)
from .core import SweetpotatoConfig, read_conf_file
from .error import ConfFileError
from .system import error_and_die
from .web import run_webui

try:
    from daemon import runner
except ImportError:
    runner = None


# TODO: daemon doesn't work with multiple servers under the same user.
class SweetpotatoDaemon(SweetpotatoConfig):
    """
    A bootstrap-able version of SweetpotatoConfig to be used for the daemon
    """
    def __init__(self):
        super().__init__()
        self.stdin_path = '/dev/null'
        self.stdout_path = DEFAULT_LOG_FILE
        self.stderr_path = DEFAULT_LOG_FILE
        self.pidfile_path = DEFAULT_PIDFILE
        self.pidfile_timeout = DEFAULT_PIDFILE_TIMEOUT

    def configure(self):
        """
        Provides a way to configure a SweetpotatoConfig instance outside of the
        normal command line means.

        We won't be taking command-line options, so the only source for
        configurations will be the default config file.

        @return:
        """
        try:
            read_conf_file(DEFAULT_CONF_FILE, self)
            self.conf_file = DEFAULT_CONF_FILE
        except (configparser.NoSectionError, ConfFileError):
            error_and_die('You must set a default configuration to use {}d!'.format(PROGNAME))

    def run(self):
        while True:
            run_webui(self, True)


def daemon_action(action):
    """
    Run the daemon with the supplied action.

    :param action:
    :return:
    """
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
    if LockTimeout and bottle:
        if runner:
            daemon_runner = runner.DaemonRunner(s)
            try:
                daemon_runner.do_action()
            except (LockTimeout, runner.DaemonRunnerStopFailureError) as e:
                error_and_die(e, quiet=s.quiet)
        else:
            error_and_die(DAEMON_PY3K_ERROR, quiet=s.quiet)
    else:
        # error_and_die("The 'lockfile' module is not installed! Please install it and try again.")
        error_and_die("TODO: ERROR ABOUT DEPENDENCIES GOES HERE!", quiet=s.quiet)


def _setup_daemon():
    _ensure_default_log_dir()
    _ensure_default_run_dir()
    s = SweetpotatoDaemon()
    s.configure()
    return s
