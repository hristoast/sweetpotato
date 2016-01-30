import os
import subprocess

from .common import FORGE_JAR_NAME, VANILLA_JAR_NAME
from .error import NoJarFoundError


def get_java_procs():
    """
    Checks for running Java processes and return the
    cwd, exe, and pid of any we find.
    """
    cwd, exe, pid = None, None, None
    p = subprocess.Popen(['pgrep', 'java'], stdout=subprocess.PIPE)
    output = p.communicate()[0]

    if output and len(output.split()) is 1:
        # One Java process
        pid = output.decode().strip()
        c = subprocess.Popen(
            ['/bin/ls', '-l', '/proc/{0}/cwd'.format(pid)],
            stdout=subprocess.PIPE)
        c_out = c.communicate()[0]
        cwd = c_out.decode().split()[-1]
        e = subprocess.Popen(
            ['/bin/ls', '-l', '/proc/{0}/exe'.format(pid)],
            stdout=subprocess.PIPE)
        e_out = e.communicate()[0]
        try:
            exe = e_out.decode().split()[-1]
        except IndexError:
            # process may have stopped/restarted
            return None
    elif output and len(output.split()) > 1:
        # More than one Java process
        proc_list = []
        for P in output.decode().split():
            pid = P
            c = subprocess.Popen(
                ['/bin/ls', '-l', '/proc/{0}/cwd'.format(pid)],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            c_out = c.communicate()[0]
            cwd = c_out.decode().split()[-1]
            e = subprocess.Popen(
                ['/bin/ls', '-l', '/proc/{0}/exe'.format(pid)],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            e_out = e.communicate()[0]
            exe = e_out.decode().split()[-1]
            proc_list.append((cwd, exe, pid))
        return proc_list

    if cwd and exe and pid:
        return cwd, exe, pid
    else:
        return None


def get_jar(settings):
    """
    Returns the name of our server's jar, be it vanilla or forge.

    @param settings:
    @return:
    """
    if settings.forge:
        forge_version = settings.forge
        jar_name = FORGE_JAR_NAME.format(forge_version)
        launch_cmd = ' java -Xms{0}{2} -Xmx{1}{2} -XX:MaxPermSize={3}M -jar {4} nogui'
    else:
        mc_version = settings.mc_version
        jar_name = VANILLA_JAR_NAME.format(mc_version)
        launch_cmd = ' java -Xms{0}{2} -Xmx{1}{2} -jar {3} nogui'
    if jar_name in os.listdir(settings.server_dir):
        return jar_name, launch_cmd
    else:
        raise NoJarFoundError(
            'The configured server jar file "{}" does not exist.'
            ' Do you need to run --create?'.format(jar_name))
