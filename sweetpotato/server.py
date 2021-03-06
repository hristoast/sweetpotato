import os
import time
import urllib.error
import urllib.request

from datetime import datetime
from .common import FORGE_DL_URL, FORGE_JAR_NAME, SERVER_WAIT_TIME, \
    VANILLA_DL_URL, VANILLA_JAR_NAME, emit_msg
from .error import NoJarFoundError, ServerAlreadyRunningError, \
    ServerNotRunningError, UnsupportedVersionError
from .java import get_jar, get_java_procs
from .screen import is_screen_started, start_screen
from .system import create_dir, error_and_die, is_forced


def _agree_to_eula(eula_txt, force, quiet):
    """
    Checks for a eula.txt file in server
    and verifies it contains 'eula=true'.

    @param eula_txt:
    @param force:
    @return:
    """
    if os.path.isfile(eula_txt) and not force:
        f = open(eula_txt, 'r')
        if 'eula=true' in f.read():
            f.close()
            emit_msg('Eula agreed to!', quiet=quiet)
            return True
        else:
            f.close()
    emit_msg('Agreeing to the eula ...', quiet=quiet)
    f = open(eula_txt, 'w')
    f.write('eula=true\n')
    f.close()
    emit_msg('Eula agreed to!', quiet=quiet)
    return True


def create_server(settings, quiet):
    """
    Check for or create the configured backup_dir and server_dir, check for or
    download the server jar for the configured mc_version, then ensure that
    server.properties matches what our desired configurations are.

    @param settings:
    @param quiet:
    @return:
    """
    backup_dir = settings.backup_dir
    force = is_forced(settings)
    server_dir = settings.server_dir
    world_name = settings.world_name

    if settings.forge:
        forge_version = settings.forge
        jar_name = FORGE_JAR_NAME.format(forge_version)
        dl_url = FORGE_DL_URL.format(forge_version, jar_name)
    else:
        mc_version = settings.mc_version
        jar_name = VANILLA_JAR_NAME.format(mc_version)
        dl_url = VANILLA_DL_URL.format(mc_version, jar_name)

    is_running = is_server_running(settings.server_dir)
    if is_running:
        raise ServerAlreadyRunningError(
            'Can\'t create "{}" - it\'s already running!'.format(world_name))

    emit_msg('Creating "{}" ...'.format(world_name), quiet=quiet)

    if not backup_dir:
        error_and_die("No backup dir supplied!")
    if os.path.isdir(backup_dir):
        emit_msg('Found "{}"!'.format(backup_dir), quiet=quiet)
    else:
        emit_msg('Creating "{}" ...'.format(backup_dir), quiet=quiet)
        create_dir(backup_dir)
        emit_msg('"{}" created!'.format(backup_dir), quiet=quiet)

    if not os.path.isdir(server_dir):
        emit_msg('Creating "{}" ...'.format(server_dir), quiet=quiet)
        create_dir(server_dir)
        emit_msg('"{}" created!'.format(server_dir), quiet=quiet)
    else:
        emit_msg('Found "{}"!'.format(server_dir))

    full_jar_path = os.path.join(server_dir, jar_name)
    if not os.path.isfile(full_jar_path) or force:
        emit_msg('Downloading "{}" ... '.format(jar_name), quiet=quiet)
        try:
            local_jar = urllib.request.urlretrieve(dl_url, full_jar_path)[0]
            jar = open(local_jar)
            jar.close()
        except urllib.error.HTTPError as e:
            error_and_die(e.msg + ' Is your version valid?', quiet=quiet)
        emit_msg('"{}" downloaded!'.format(jar_name), quiet=quiet)
    else:
        emit_msg('Found "{}"!'.format(jar_name), quiet=quiet)

    eula_txt = os.path.join(server_dir, 'eula.txt')
    _agree_to_eula(eula_txt, force, quiet)

    server_properties = os.path.join(server_dir, 'server.properties')
    write_server_properties(server_properties, settings, quiet)

    emit_msg('World "{}" has been created!'.format(world_name), quiet=quiet)


def _format_launch_cmd(settings):
    """
    Reads from settings to return the proper command string for launching
    the configured server.

    @param settings:
    @return:
    """
    jar_name, launch_cmd = get_jar(settings)
    mem_format = settings.mem_format
    mem_max = settings.mem_max
    mem_min = settings.mem_min

    return launch_cmd.format(mem_min, mem_max, mem_format[0], jar_name)


def get_uptime_raw(server_dir, world_name, quiet):
    """
    If the configured server is running, read the server.properties file
    to get the start time, and return an uptime in hours based on that.

    The time will be slightly inaccurate because the server writes the new
    date string to your server.properties file towards the end of the
    startup sequence.

    On vanilla servers this duration should be slight, but on modded servers
    the difference might be closer to a minute because the startup is longer.

    If the server is not running, return False.

    @param server_dir:
    @param world_name:
    @param quiet:
    @return:
    """
    fmt = '%a %b %d %H:%M:%S %Z %Y'
    now = datetime.now()
    server_running = is_server_running(server_dir)
    if server_running:
        server_properties = os.path.join(server_dir, 'server.properties')
        with open(server_properties, 'r') as sp:
            spl = sp.readlines()
            sp.close()
        server_start_time_string = spl[1].strip().strip('#')
        server_start_time = datetime.strptime(server_start_time_string, fmt)
        uptime = now - server_start_time
        return uptime
    else:
        raise ServerNotRunningError(
            '{} is not running'.format(world_name))


def get_uptime(raw_uptime):
    """
    Takes a raw datetime.timedelta object and returns the total
    days, hours, minutes, and seconds.

    @param raw_uptime:
    @return:
    """
    days = raw_uptime.days
    hours = raw_uptime.seconds // 60 // 60
    if hours:
        total_minutes = raw_uptime.seconds // 60
        minutes = total_minutes - hours * 60
        seconds = raw_uptime.seconds - (minutes * 60) - (hours * 60 * 60)
    else:
        minutes = raw_uptime.seconds // 60
        if minutes:
            seconds = raw_uptime.seconds - minutes * 60
        else:
            seconds = raw_uptime.seconds
    return days, hours, minutes, seconds


def get_uptime_string(uptime):
    d = uptime[0]
    h = uptime[1]
    m = uptime[2]
    s = uptime[3]

    # get the right pluralization
    if d == 1:
        ds = 'day'
    else:
        ds = 'days'
    if h == 1:
        hs = 'hour'
    else:
        hs = 'hours'
    if m == 1:
        ms = 'minute'
    else:
        ms = 'minutes'
    if s == 1:
        ss = 'second'
    else:
        ss = 'seconds'
    return '{0} {1}, {2} {3}, {4} {5}, and {6} {7}'.format(
        d, ds,
        h, hs,
        m, ms,
        s, ss)


def is_server_running(server_dir_name):
    """
    Checks /proc for a java process that has a cwd of 'server_dir_name'.

    @param server_dir_name:
    @return:
    """
    if not server_dir_name:
        error_and_die("No server directory name supplied!")
    java_procs = get_java_procs()
    server_dir = server_dir_name.rstrip('/')
    if isinstance(java_procs, tuple):
        # just one java proc
        if server_dir in java_procs:
            proc = {'cwd': java_procs[0],
                    'exe': java_procs[1],
                    'pid': java_procs[2]}
            return proc
        else:
            return False
    elif isinstance(java_procs, list):
        # multiple java procs
        for p in java_procs:
            if server_dir in p[0]:
                proc = {'cwd': p[0],
                        'exe': p[1],
                        'pid': p[2]}
                return proc
    return False


def list_players(settings):
    """
    Send a 'list' command to the server and try to read the list of
    logged-in players.

    @param settings:
    @return:
    """
    latest_log = os.path.join(
        settings.server_dir,
        'logs',
        'latest.log')
    running = is_server_running(settings.server_dir)
    if running:
        send_command('list', is_screen_started(settings.screen_name))

    def read_latest_log():
        if running:
            try:
                with open(latest_log, 'r') as log:
                    log_lines = log.readlines()
                    log.close()
                    return log_lines
            except (OSError, IOError):
                emit_msg('failed to read log oh noes!')  # TODO: set level to error
        return None

    ll = read_latest_log()

    if ll:
        try:
            while 'players online:' not in ll[-2:][0]:
                ll = read_latest_log()
            else:
                player_list = ll[-2:]
        except TypeError:
            player_list = None  # oh.
    else:
        player_list = ll

    if player_list:
        if 'There are 0/20 players online' in player_list[0]:
            return None
        else:
            return player_list
    else:
        return None


def list_players_as_list(player_list):
    """
    Takes the output of list_players() and puts each logged-in player into a
    Python list, if there are any.

    @param player_list:
    @return:
    """
    if player_list:
        if 'There are 0/20 players online' in player_list[0]:
            return None
        else:
            return player_list[-2:][1].split(']:')[1].strip().split(',')
    else:
        return None


def restart_server(settings, quiet):
    """
    Restarts a configured server.

    @param settings:
    @return:
    """
    screen_name = settings.screen_name
    server_dir = settings.server_dir
    world_name = settings.world_name

    screen_started = is_screen_started(screen_name)
    server_running = is_server_running(server_dir)

    launch_server = _format_launch_cmd(settings)

    if not screen_started:
        start_screen(screen_name, server_dir)

    if server_running:
        server_pid = server_running.get('pid')
        emit_msg('Restarting "{}" ...'.format(world_name), quiet=quiet)
        wait_for_server_shutdown(screen_name, server_pid)
    else:
        emit_msg('Starting "{}" ...'.format(world_name), quiet=quiet)
    send_command(launch_server, is_screen_started(screen_name))
    emit_msg('"{}" restarted!'.format(world_name), quiet=quiet)


def save_all(settings):
    """
    Sends a 'save-all' command to the server.
    """
    send_command("save-all", is_screen_started(settings.screen_name))
    return True


def send_command(command, screen_name):
    """
    Send a command to the server.

    @param command:
    @param screen_name:
    @return:
    """
    cmd_line = 'screen -S {0} -X eval \'stuff "{1}"\015\''.format(
        is_screen_started(screen_name), command)
    os.system(cmd_line)
    # cmd_list = shlex.split(cmd_line)
    # subprocess.call(cmd_list)


def start_server(settings, quiet):
    """
    Starts a configured server.

    @param settings:
    @return:
    """
    jar_name = None
    launch_cmd = None

    try:
        jar_name, launch_cmd = get_jar(settings)
    except NoJarFoundError as e:
        error_and_die(e, quiet=quiet)

    mem_format = settings.mem_format
    mem_max = settings.mem_max
    mem_min = settings.mem_min
    screen_name = settings.screen_name
    server_dir = settings.server_dir
    world_name = settings.world_name

    screen_started = is_screen_started(screen_name)
    server_running = is_server_running(server_dir)

    launch_server = launch_cmd.format(mem_min, mem_max, mem_format[0], jar_name)

    if not screen_started:
        start_screen(screen_name, server_dir)

    if not server_running:
        emit_msg('Starting "{}" ...'.format(world_name), quiet=quiet)
        send_command(launch_server, is_screen_started(screen_name))
        emit_msg('"{}" started!'.format(world_name), quiet=quiet)
    else:
        raise ServerAlreadyRunningError(
            'World "{0}" already running with PID {1}'.format(
                settings.world_name, server_running.get('pid')))


def stop_server(screen_name, server_dir, world_name, quiet):
    """
    Stops a configured server.

    @param screen_name:
    @param server_dir:
    @param world_name:
    @param quiet:
    @return:
    """
    # TODO: we need a timeout here and an option to kill when that timeout is reached
    server_running = is_server_running(server_dir)

    if server_running:
        server_pid = server_running.get('pid')
        emit_msg('Stopping "{}" ...'.format(world_name), quiet=quiet)
        wait_for_server_shutdown(screen_name, server_pid)
        send_command(' exit', is_screen_started(screen_name))
        emit_msg('"{}" stopped!'.format(world_name), quiet=quiet)
    else:
        raise ServerNotRunningError(
            'Cannot stop "{}" - it is not running!'.format(world_name))


def wait_for_server_shutdown(screen_name, server_pid):
    """
    In case we've tried to stop before the server has fully started.

    @param screen_name:
    @param server_pid:
    @return:
    """
    while os.path.exists("/proc/{}".format(server_pid)):
        time.sleep(SERVER_WAIT_TIME)
        send_command(' stop', is_screen_started(screen_name))


def write_server_properties(file, settings, quiet):
    """
    Checks for a server.properties for the specified server_dir
    and world_name, and writes if need be (or forced)

    @param file:
    @param settings:
    @return:
    """
    def do_the_write():
        emit_msg('Generating server.properties ...', quiet=quiet)
        file_to_write = open(file, 'w')
        try:
            for l in settings.as_serverproperties.split('\n'):
                file_to_write.write(l + '\n')
        except UnsupportedVersionError as e:
            error_and_die(e, quiet=quiet)
        file_to_write.close()
        emit_msg('server.properties generated!', quiet=quiet)

    found_msg = 'Found server.properties!'
    if os.path.isfile(file):
        f = open(file, 'r')
        f_readlines = f.readlines()
        # Write a new file if any of the three values we change have changed
        if not 'level-name={}\n'.format(settings.world_name) in f_readlines \
            or not 'server-port={}\n'.format(settings.port) in f_readlines \
            or not 'level-seed={}\n'.format(settings.level_seed or '') \
                in f_readlines or settings.force:
            do_the_write()
        else:
            emit_msg(found_msg, quiet=quiet)
        f.close()
    else:
        do_the_write()
