import configparser
import json
import os
import pty
import shlex
import subprocess
import sys
import time
import tarfile
import urllib.error
import urllib.request

from datetime import datetime
from .common import (DEFAULT_COMPRESSION, DEFAULT_SCREEN_NAME,
                     DEFAULT_SERVER_PORT, DEFAULT_WEBUI_PORT,
                     DEFAULT_WORLD_NAME, FORGE_DL_URL, FORGE_JAR_NAME,
                     MCVERSION, PROGNAME, REQUIRED, SERVER_WAIT_TIME,
                     VANILLA_DL_URL, VANILLA_JAR_NAME, Colors)
from .error import (ConfFileError, EmptySettingError, MissingExeError,
                    NoDirFoundError, NoJarFoundError,
                    ServerAlreadyRunningError, ServerNotRunningError,
                    UnsupportedVersionError)


class SweetpotatoConfig:
    """Representing the settings sweetpotato needs to function."""
    header = "## Generated by {0} at {1}".format(
        PROGNAME, datetime.now().strftime('%c'))

    def __init__(self):
        self.backup_dir = None
        self.compression = DEFAULT_COMPRESSION
        self.conf_file = None
        self.fancy = False
        self.force = False
        self.forge = None
        self.level_seed = None
        self.mem_format = None
        self.mem_max = None
        self.mem_min = None
        self.mc_version = MCVERSION
        self.permgen = None
        self.port = DEFAULT_SERVER_PORT
        self.running = False
        self.screen_name = DEFAULT_SCREEN_NAME
        self.server_dir = None
        self.webui_port = DEFAULT_WEBUI_PORT
        self.world_name = DEFAULT_WORLD_NAME
        self.world_only = False

    @property
    def as_conf_file(self):
        conf = self.header + '\n'
        conf += '[Settings]\n'
        for k, v in self.__dict__.items():
            if v is not None \
                    and k is not 'conf_file' \
                    and k is not 'force' \
                    and k is not 'running'\
                    and not (v is False and k is 'fancy'):
                conf += '{0}: {1}\n'.format(k, v)
        return conf.strip()

    @property
    def as_json(self):
        self_dict = self.__dict__.copy()
        try:
            self_dict.pop('pidfile')
        except KeyError:
            pass
        try:
            players = list_players_as_list(list_players(self))
            raw = get_uptime_raw(self.server_dir, self.world_name, False)
            u = get_uptime(raw)
            uptime = {
                'days': u[0],
                'hours': u[1],
                'minutes': u[2],
                'seconds': u[3]
            }
            self_dict['running'].update(players=players)
            self_dict['running'].update(uptime=uptime)
        except ServerNotRunningError:
            pass
        if self.fancy:
            return json.dumps(self_dict, sort_keys=True, indent=4)
        else:
            return json.dumps(self_dict)

    @property
    def as_serverproperties(self):
        vanilla_server_properties_1710 = """generator-settings=
op-permission-level=4
allow-nether=true
level-name={0}
enable-query=false
allow-flight=false
announce-player-achievements=true
server-port={1}
level-type=DEFAULT
enable-rcon=false
level-seed={2}
force-gamemode=false
server-ip=
max-build-height=256
spawn-npcs=true
white-list=false
spawn-animals=true
hardcore=false
snooper-enabled=true
online-mode=true
resource-pack=
pvp=true
difficulty=1
enable-command-block=false
gamemode=0
player-idle-timeout=0
max-players=20
spawn-monsters=true
generate-structures=true
view-distance=10
motd=Welcome to {0}!
        """.format(self.world_name, self.port, self.level_seed or '')
        vanilla_server_properties_18 = """generator-settings=
op-permission-level=4
allow-nether=true
resource-pack-hash=
level-name={0}
enable-query=false
allow-flight=false
announce-player-achievements=true
server-port={1}
max-world-size=29999984
level-type=DEFAULT
enable-rcon=false
level-seed={2}
force-gamemode=false
server-ip=
network-compression-threshold=256
max-build-height=256
spawn-npcs=true
white-list=false
spawn-animals=true
hardcore=false
snooper-enabled=true
online-mode=true
resource-pack=
pvp=true
difficulty=1
enable-command-block=false
gamemode=0
player-idle-timeout=0
max-players=20
max-tick-time=60000
spawn-monsters=true
generate-structures=true
view-distance=10
motd=Welcome to {0}!
        """.format(self.world_name, self.port, self.level_seed or '')
        if '1.8' in self.mc_version:
            return vanilla_server_properties_18
        elif self.mc_version == '1.7.10':
            return vanilla_server_properties_1710
        else:
            raise UnsupportedVersionError(
                "We can't generate a server.properties for "
                "the version ov MC you are trying to use ({}).".format(
                    self.mc_version)
            )


def _agree_to_eula(eula_txt, force, print_pre, quiet):
    """
    Checks for a eula.txt file in server
    and verifies it contains 'eula=true'.

    @param eula_txt:
    @param force:
    @param print_pre:
    @return:
    """
    if os.path.isfile(eula_txt) and not force:
        f = open(eula_txt, 'r')
        if 'eula=true' in f.read():
            f.close()
            if not quiet:
                print(print_pre + Colors.light_blue + 'Eula agreed to!' +
                      Colors.end)
            return True
        else:
            f.close()
    if not quiet:
        print(print_pre + Colors.light_blue +
              'Agreeing to the eula ...', end=' ')
    f = open(eula_txt, 'w')
    f.write('eula=true\n')
    f.close()
    if not quiet:
        print('Done!' + Colors.end)
    return True


def _can_xz():
    if sys.version_info[1] < 3:
        return False
    else:
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
    print_pre = '[' + Colors.yellow_green + 'create' + Colors.end + '] '
    backup_dir = settings.backup_dir
    force = _is_forced(settings)
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
        if not quiet:
            raise ServerAlreadyRunningError(
                "Can't create '{}' - it's already running!".format(
                    world_name))
        else:
            die_silently()

    if not quiet:
        print(print_pre + Colors.blue + 'Creating "{}" ...'.format(
            world_name) + Colors.end)

    if os.path.isdir(backup_dir) and not quiet:
        print(print_pre + Colors.light_blue + 'Found {}!'.format(backup_dir)
              + Colors.end)
    else:
        if not quiet:
            print(print_pre + Colors.light_blue + 'Creating {} ...'.format(
                backup_dir), end=' ')
            sys.stdout.flush()
            _create_dir(backup_dir)
            print('Done!' + Colors.end)
        else:
            _create_dir(backup_dir)

    if not os.path.isdir(server_dir):
        if not quiet:
            print(print_pre + Colors.light_blue + 'Creating {} ...'.format(
                server_dir), end=' ')
            sys.stdout.flush()
            _create_dir(server_dir)
            print('Done!' + Colors.end)
        else:
            _create_dir(server_dir)
    elif not quiet:
            print(print_pre + Colors.light_blue + 'Found {}!'.format(
                server_dir) + Colors.end)

    full_jar_path = os.path.join(server_dir, jar_name)
    if not os.path.isfile(full_jar_path) and not quiet or force:
        print(print_pre + Colors.light_blue +
              'Downloading {} ...'.format(jar_name), end=' ')
        sys.stdout.flush()
        try:
            local_jar = urllib.request.urlretrieve(dl_url, full_jar_path)[0]
            jar = open(local_jar)
            jar.close()
        except urllib.error.HTTPError as e:
            error_and_die(e.msg + ' Is your version valid?')
        if not quiet:
            print('Done!' + Colors.end)
    elif not quiet:
        print(print_pre + Colors.light_blue +
              'Found {}!'.format(jar_name) + Colors.end)
    elif not os.path.isfile(full_jar_path) and quiet or force:
        try:
            local_jar = urllib.request.urlretrieve(dl_url, full_jar_path)[0]
            jar = open(local_jar)
            jar.close()
        except urllib.error.HTTPError:
            die_silently()

    eula_txt = os.path.join(server_dir, 'eula.txt')
    _agree_to_eula(eula_txt, force, print_pre, quiet)

    server_properties = os.path.join(server_dir, 'server.properties')
    write_server_properties(print_pre, server_properties, settings, quiet)

    if not quiet:
        print(print_pre + Colors.blue +
              'World "{}" has been created!'.format(world_name) + Colors.end)


def dependency_check(*deps):
    if None in deps:
        raise MissingExeError("Unable to find all dependencies. Please"
                              "ensure that screen and java are installed.")


def die_silently():
    """
    For when we need to die quietly.

    @return:
    """
    sys.exit(1)


def error_and_die(msg):
    """
    For those times when you just want to quit and say why.

    @param msg:
    @return:
    """
    sys.stderr.write(
        Colors.light_red + 'FATAL: ' + Colors.red + msg.__str__().strip("'")
        + Colors.end + '\n'
    )
    sys.exit(1)


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
    permgen = settings.permgen

    if settings.forge:
        return launch_cmd.format(mem_min, mem_max, mem_format[0],
                                 permgen, jar_name)
    else:
        return launch_cmd.format(mem_min, mem_max, mem_format[0], jar_name)


def get_exe_path(exe):
    """
    Checks for exe in $PATH.

    @param exe:
    @return:
    """
    p = subprocess.Popen(['which', exe], stdout=subprocess.PIPE)
    byte_output = p.communicate()[0]
    return byte_output.decode().strip() or None


def _get_java_procs():
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
        exe = e_out.decode().split()[-1]
    elif output and len(output.split()) > 1:
        # More than one Java process
        proc_list = []
        for P in output.decode().split():
            pid = P
            c = subprocess.Popen(
                ['/bin/ls', '-l', '/proc/{0}/cwd'.format(pid)],
                stdout=subprocess.PIPE)
            c_out = c.communicate()[0]
            cwd = c_out.decode().split()[-1]
            e = subprocess.Popen(
                ['/bin/ls', '-l', '/proc/{0}/exe'.format(pid)],
                stdout=subprocess.PIPE)
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
        launch_cmd = 'java -Xms{0}{2} -Xmx{1}{2} -XX:MaxPermSize={3}M -jar'\
                     '{4} nogui'
    else:
        mc_version = settings.mc_version
        jar_name = VANILLA_JAR_NAME.format(mc_version)
        launch_cmd = 'java -Xms{0}{2} -Xmx{1}{2} -jar {3} nogui'
    if jar_name in os.listdir(settings.server_dir):
        return jar_name, launch_cmd
    else:
        raise NoJarFoundError(
            'The configured server jar file "{}" does not exist.'
            'Do you need to run --create?'.format(jar_name)
        )


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
    elif not quiet:
        raise ServerNotRunningError(
            '{} is not running'.format(world_name)
        )
    else:
        die_silently()


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
        s, ss
    )


def _is_forced(settings):
    try:
        force = settings.force
    except AttributeError:
        force = None
    return force


def _is_screen_started(screen_name):
    """
    Checks the given screen name for a running session,
    returning the PID and name in a 'PID.NAME' formatted string.

    @param screen_name:
    @return:
    """
    l = []

    proc = subprocess.Popen(
        ['screen', '-ls', '{0}'.format(screen_name)], stdout=subprocess.PIPE)
    output = proc.communicate()[0]
    new_output = output.decode().split('\n')
    split_output = output.split()

    for split_o in split_output:
        l.append(split_o.decode())

    if 'No Sockets found' in ' '.join(l[:3]):
        return False
    elif 'There is a screen' in ' '.join(l[:4]):
        for new_o in new_output:
            if screen_name in new_o:
                return new_o.split()[0]
    elif 'There are screens' in ' '.join(l[:3]):
        screen_list = []
        for out in new_output:
            if screen_name in out:
                for part in out.split():
                    if screen_name in part:
                        screen_list.append(part)
        return screen_list


def is_server_running(server_dir_name):
    """
    Checks /proc for a java process that has a cwd of 'server_dir_name'.

    @param server_dir_name:
    @return:
    """
    java_procs = _get_java_procs()
    server_dir = server_dir_name.rstrip('/')
    if isinstance(java_procs, tuple):
        # just one java proc
        if server_dir in java_procs:
            proc = {
                'cwd': java_procs[0],
                'exe': java_procs[1],
                'pid': java_procs[2]
            }
            return proc
        else:
            return False
    elif isinstance(java_procs, list):
        # multiple java procs
        for p in java_procs:
            if server_dir in p[0]:
                proc = {
                    'cwd': p[0],
                    'exe': p[1],
                    'pid': p[2]
                }
                return proc
    return False


def _create_dir(d):
    """
    Creates a given directory if it does not exist.

    :param d:
    """
    if not os.path.isdir(d):
        try:
            os.makedirs(d)
        except PermissionError as e:
            error_and_die(e)


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
        'latest.log'
    )
    running = is_server_running(settings.server_dir)
    if running:
        send_command('list', _is_screen_started(settings.screen_name))

    def read_latest_log():
        if running:
            try:
                with open(latest_log, 'r') as log:
                    log_lines = log.readlines()
                    log.close()
                    return log_lines
            except (OSError, IOError):
                print('failed to read log oh noes!')
        return None

    ll = read_latest_log()

    if ll:
        while 'players online:' not in ll[-2:][0]:
            ll = read_latest_log()
        else:
            player_list = ll[-2:]
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


def read_conf_file(file, settings):
    """
    The arg 'file' is a conf file path, and 'settings' is a
    dict containing your settings.

    Checks if 'file' is actually a file, if not checks for 'DEFAULT_FILE'.
    If that doesn't exist, we return 'settings' as it was passed in,
    the value for 'settings["CONFIG"]' remaining 'None'.

    :param file:
    :param settings:
    """
    if len(file.split('/')) == 1:
        file_path = os.path.join(os.getcwd(), file)
    else:
        file_path = file
    if not os.path.isfile(file_path):
        raise ConfFileError(
            'The specified conf file does not exist: {}'.format(file_path)
        )

    section = 'Settings'
    c = configparser.ConfigParser()
    try:
        c.read(file_path)
    except configparser.MissingSectionHeaderError:
        raise ConfFileError(
            "The specified conf file does not have a valid"
            "'Settings' section")

    options = c.options(section)
    options_dict = {}
    for o in options:
        options_dict[o] = c.get(section, o)
    fancy = c[section].getboolean('fancy')
    try:
        options_dict.pop('fancy')
        options_dict.update(fancy=fancy)
    except KeyError:
        pass
    return settings.__dict__.update(**options_dict)


def send_command(command, screen_name):
    """
    Send a command to the server.

    @param command:
    @param screen_name:
    @return:
    """
    cmd_line = 'screen -S {0} -X eval \'stuff "{1}"\015\''.format(
        _is_screen_started(screen_name), command)
    cmd_list = shlex.split(cmd_line)
    subprocess.call(cmd_list)


def start_screen(screen_name, server_dir):
    """
    Starts a screen session named 'screen_name' with a cwd of 'server_dir.

    @param screen_name:
    @param server_dir:
    @return:
    """
    command = 'screen -dmS ' + screen_name
    os.chdir(server_dir)
    master, slave = pty.openpty()
    cmd_args = shlex.split(command)
    subprocess.Popen(cmd_args, close_fds=True, shell=False, stdin=slave,
                     stdout=slave, stderr=slave)


def start_server(print_pre, settings, quiet):
    """
    Starts a configured server.

    @param print_pre:
    @param settings:
    @return:
    """
    jar_name = None
    launch_cmd = None

    try:
        jar_name, launch_cmd = get_jar(settings)
    except NoJarFoundError as e:
        error_and_die(e)

    mem_format = settings.mem_format
    mem_max = settings.mem_max
    mem_min = settings.mem_min
    screen_name = settings.screen_name
    server_dir = settings.server_dir
    world_name = settings.world_name

    # screen_started = _is_screen_started(screen_name)
    server_running = is_server_running(server_dir)

    if settings.forge:
        permgen = settings.permgen
        launch_server = launch_cmd.format(mem_min, mem_max, mem_format[0],
                                          permgen, jar_name)
    else:
        launch_server = launch_cmd.format(mem_min, mem_max,
                                          mem_format[0], jar_name)

    # if not screen_started:
    #     start_screen(screen_name, server_dir)

    screen_started = _is_screen_started(screen_name)
    while not screen_started:
        count = 0
        start_screen(screen_name, server_dir)
        screen_started = _is_screen_started(screen_name)
        count += 1
        print(count)

    if not server_running:
        if not quiet:
            if print_pre:
                print(print_pre + Colors.light_blue +
                      'Starting "{}" ...'.format(world_name), end=' ')
            else:
                print('starting "{}" ...'.format(world_name), end=' ')
            sys.stdout.flush()
        send_command(launch_server, screen_started)
        if not quiet:
            print('Done!' + Colors.end)
    elif not quiet:
        raise ServerAlreadyRunningError(
            'World "{0}" already running with PID {1}'.format(
                settings.world_name,
                server_running.get('pid')
            ))
    else:
        die_silently()


def stop_server(print_pre, screen_name, server_dir, world_name, quiet):
    """
    Stops a configured server.

    @param print_pre:
    @param screen_name:
    @param server_dir:
    @param world_name:
    @param quiet:
    @return:
    """
    server_running = is_server_running(server_dir)

    if server_running:
        server_pid = server_running.get('pid')
        if not quiet:
            print(print_pre + Colors.light_blue +
                  'Stopping "{}" ...'.format(world_name), end=' ')
        sys.stdout.flush()
        wait_for_server_shutdown(screen_name, server_pid)
        send_command('exit', _is_screen_started(screen_name))
        if not quiet:
            print('Done!' + Colors.end)
    elif not quiet:
        raise ServerNotRunningError(
            'Cannot stop "{}" - it is not running!'.format(world_name)
        )
    else:
        die_silently()


def reread_settings(settings):
    """
    Reloads settings. Useful for the WebUI, in case you've modified your
    conf file since having started it.

    @param settings:
    @return:
    """
    # Read a passed-in conf file
    if settings.conf_file:
        read_conf_file(settings.conf_file, settings)
    return settings


def restart_server(print_pre, settings, quiet):
    """
    Restarts a configured server.

    @param print_pre:
    @param settings:
    @return:
    """
    screen_name = settings.screen_name
    server_dir = settings.server_dir
    world_name = settings.world_name

    screen_started = _is_screen_started(screen_name)
    server_running = is_server_running(server_dir)

    launch_server = _format_launch_cmd(settings)

    if not screen_started:
        start_screen(screen_name, server_dir)

    if server_running:
        server_pid = server_running.get('pid')
        if not quiet:
            print(print_pre + Colors.light_blue +
                  'Restarting {} ...'.format(world_name), end=' ')
            sys.stdout.flush()
        wait_for_server_shutdown(screen_name, server_pid)
    elif not quiet:
        print(print_pre + Colors.light_blue +
              'Starting {} ...'.format(world_name), end=' ')
        sys.stdout.flush()
    send_command(launch_server, _is_screen_started(screen_name))
    if not quiet:
        print('Done!' + Colors.end)


def run_server_backup(print_pre, settings, quiet, running,
                      world_only, offline=False):
    """
    Runs the configured backup on the configured server.

    @param print_pre:
    @param settings:
    @param quiet:
    @param running:
    @param world_only:
    @param offline:
    @return:
    """
    backup_dir = settings.backup_dir
    date_stamp = datetime.now().strftime('%Y-%m-%d')
    force = _is_forced(settings)
    forge = settings.forge

    screen_name = settings.screen_name
    server_dir = settings.server_dir
    world_name = settings.world_name
    compression = settings.compression

    backup_file = '{0}_{1}.tar.{2}'.format(date_stamp, world_name, compression)
    full_path_to_backup_file = os.path.join(backup_dir, backup_file)
    backup_made_today = os.path.isfile(full_path_to_backup_file)

    if backup_made_today and not force:
        sys.stdout.flush()
        try:
            with open(full_path_to_backup_file, 'rb'):
                if not quiet:
                    error_and_die('File "{}" already exists!'.format(
                        full_path_to_backup_file))
                else:
                    die_silently()
        except IOError:
            pass

    if offline:
        print(print_pre + Colors.light_blue, end=' ')
        if running:
            server_pid = running.get('pid')
            if not quiet:
                print('Stopping "{}" ...'.format(world_name), end=' ')
            sys.stdout.flush()
            wait_for_server_shutdown(screen_name, server_pid)
            if not quiet:
                print('backing up ...', end=' ')
        elif not quiet:
            print('Backing up "{}" ...'.format(world_name), end=' ')
        sys.stdout.flush()
    elif running:
        send_command('save-all', _is_screen_started(screen_name))
        send_command('save-off', _is_screen_started(screen_name))
        if not quiet:
            print(print_pre + Colors.light_blue +
                  'Running live backup of "{}"  ...'.format(
                      world_name), end=' ')
        sys.stdout.flush()
        send_command('say Server backing up now',
                     _is_screen_started(screen_name))

    _create_dir(backup_dir)

    if not _can_xz() and settings.compression == 'xz':
        compression = 'gz'

    tar = tarfile.open(full_path_to_backup_file, 'w:{}'.format(compression))
    if world_only:
        if not running and not offline:
            print_pre = '[' + Colors.yellow_green + 'backup' + Colors.end +\
                        '] '
            print(print_pre + Colors.light_blue, end='')
            print('Backing up "{}" ...'.format(world_name), end=' ')
            sys.stdout.flush()
        tar.add(os.path.join(server_dir, world_name))
    elif forge:
        tar.add(server_dir, exclude=lambda x: 'dynmap' in x)
    else:
        tar.add(server_dir)
    tar.close()

    if not offline and running:
        send_command('say Backup complete', _is_screen_started(screen_name))
        send_command('save-on', _is_screen_started(screen_name))

    if not quiet:
        print('Done!' + Colors.end)


def validate_directories(*dirs):
    """
    Ensures that the passed-in directories exist.

    @param dirs:
    @return:
    """
    for d in dirs:
        if not os.path.isdir(d):
            raise NoDirFoundError(
                'The configured directory "{}" does not exist.'
                'Do you need to run --create?'.format(d))


def validate_mem_values(min_mem, max_mem):
    """
    Ensure that the given mem values are numbers
    and that the min is less than the max

    @param min_mem:
    @param max_mem:
    @return:
    """
    min_value = None
    max_value = None
    try:
        min_value = int(min_mem)
        max_value = int(max_mem)
    except ValueError:
        error_and_die('The memory values you provided are invalid!')

    if min_value > max_value:
        raise ValueError


def validate_settings(settings):
    """
    Ensures that all required settings have a value.

    @param settings:
    @return:
    """
    missing = []
    for setting, value in settings.__dict__.items():
        if setting in REQUIRED and value is None:
            missing.append(setting)

    if missing:
        raise EmptySettingError(
            'One or more required settings are not present: {}'.format(
                ' '.join(missing)))
    else:
        return True


def wait_for_server_shutdown(screen_name, server_pid):
    """
    In case we've tried to stop before the server has fully started.

    @param screen_name:
    @param server_pid:
    @return:
    """
    while os.path.exists("/proc/{0}".format(server_pid)):
        time.sleep(SERVER_WAIT_TIME)
        send_command('stop', _is_screen_started(screen_name))


def write_server_properties(print_pre, file, settings, quiet):
    """
    Checks for a server.properties for the specified server_dir
    and world_name, and writes if need be (or forced)

    @param print_pre:
    @param file:
    @param settings:
    @return:
    """
    def do_the_write():
        if not quiet:
            print(print_pre + Colors.light_blue +
                  'Generating server.properties ...', end=' ')
            sys.stdout.flush()
        file_to_write = open(file, 'w')
        try:
            for l in settings.as_serverproperties.split('\n'):
                file_to_write.write(l + '\n')
        except UnsupportedVersionError as e:
            if not quiet:
                error_and_die(e)
            else:
                die_silently()
        file_to_write.close()
        if not quiet:
            print('Done!' + Colors.end)

    found_msg = (print_pre + Colors.light_blue +
                 'Found server.properties!' + Colors.end)
    if os.path.isfile(file):
        f = open(file, 'r')
        f_readlines = f.readlines()
        # Write a new file if any of the three values we change have changed
        if not 'level-name={}\n'.format(settings.world_name) in f_readlines \
            or not 'server-port={}\n'.format(settings.port) in f_readlines \
            or not 'level-seed={}\n'.format(settings.level_seed or '') \
                in f_readlines or settings.force:
            do_the_write()
        elif not quiet:
            print(found_msg)
        f.close()
    else:
        do_the_write()
