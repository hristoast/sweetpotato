import os
import subprocess
import sys

from .common import Colors
from .error import MissingExeError


def create_dir(d):
    """
    Creates a given directory if it does not exist.

    :param d:
    """
    if not os.path.isdir(d):
        try:
            os.makedirs(d)
        except PermissionError as e:
            error_and_die(e)


def dependency_check(*deps):
    if None in deps:
        raise MissingExeError("Unable to find all dependencies. Please"
                              " ensure that screen and java are installed.")


def error_and_die(msg, quiet=False):
    """
    For those times when you just want to quit and say why.

    @param msg:
    @param quiet:
    @return:
    """
    if not quiet:
        sys.stderr.write(
            Colors.light_red + 'FATAL: ' + Colors.red + msg.__str__().strip("'") +
            Colors.end + '\n')
    sys.exit(1)


def is_forced(settings):
    """
    Not really a system thing, but this is where it
    doesn't cause an import loop.

    @param settings:
    @return: force
    """
    try:
        force = settings.force
    except AttributeError:
        force = None
    return force


def get_exe_path(exe: str) -> list or None:
    """
    Checks for exe in $PATH.

    @param exe:
    @return:
    """
    p = subprocess.Popen(['which', exe], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    byte_output = p.communicate()[0]
    return byte_output.decode().strip() or None
