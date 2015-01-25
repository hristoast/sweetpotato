from .core import error_and_die
from .web import run_webui


try:
    import daemon
except ImportError:
    daemon = None


__all__ = ['run_daemon']


def run_daemon(settings):
    if daemon:
        print('DAEMON HUH!')
        # runner = daemon.
    else:
        error_and_die('python-daemon-3K is not installed!')
