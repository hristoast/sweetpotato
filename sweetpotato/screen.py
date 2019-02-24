import os
import subprocess


def is_screen_started(screen_name):
    """
    Checks the given screen name for a running session,
    returning the PID and name in a 'PID.NAME' formatted string.

    @param screen_name:
    @return:
    """
    with open(os.devnull, "w") as FNULL:
        proc = subprocess.Popen(
            ['screen', '-ls', '{0}'.format(screen_name)], stdout=subprocess.PIPE, stderr=FNULL)
        output = proc.communicate()[0]
        split_output = output.decode().split()

    if split_output[0] == 'No':
        # no screens named `screen_name`
        return False
    elif split_output[1] == 'is':
        # there is a screen running named `screen_name`
        for l in split_output:
            if screen_name in l:
                return l
    elif split_output[1] == 'are':
        # there are multiple screen sessions named `screen_name`, we can't know
        # which one truly is the right one so we will use the "first" one. We
        # do, however handle situations where we've got two screen names that
        # are similar (such as World and World2.)
        for l in split_output:
            if screen_name in l:
                if l.split('.')[1] == screen_name:
                    return l


def start_screen(screen_name, server_dir):
    """
    Starts a screen session named 'screen_name' with a cwd of 'server_dir.

    @param screen_name:
    @param server_dir:
    @return: True
    """
    command = 'screen -dmS ' + screen_name
    os.chdir(server_dir)
    os.system(command)
    return True
