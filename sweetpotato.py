#!/usr/bin/env python3
"""A tool for managing Minecraft servers on GNU/Linux."""
import argparse
try:
    import bottle
except ImportError:
    bottle = None
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
try:
    from markdown import markdown
except ImportError:
    markdown = None
from threading import Thread


__author__ = 'Hristos N. Triantafillou <me@hristos.triantafillou.us>'
__license__ = 'GPLv3'
__mcversion__ = '1.8'
__progname__ = 'sweetpotato'
__version__ = '0.11 BETA'


BASE_DIR = os.path.dirname(os.path.realpath(__file__))
DEFAULT_PERMGEN = '256'
DEFAULT_SERVER_PORT = '25565'
DEFAULT_WORLD_NAME = 'SweetpotatoWorld'
DESCRIPTION = "Manage your Minecraft server on a GNU/Linux system."
HOME_DIR = os.getenv('HOME')
CONFIG_DIR = '{0}/.config/{1}'.format(HOME_DIR, __progname__)
DEFAULT_CONF_FILE = '{0}/{1}.conf'.format(CONFIG_DIR, __progname__)
REQUIRED = 'backup_dir mem_format mem_max mem_min port screen_name server_dir world_name'
SERVER_WAIT_TIME = 0.5
FORGE_DL_URL = 'http://files.minecraftforge.net/maven/net/minecraftforge/forge/{0}/{1}'
FORGE_JAR_NAME = 'forge-{}-universal.jar'
VANILLA_DL_URL = 'https://s3.amazonaws.com/Minecraft.Download/versions/{0}/{1}'
VANILLA_JAR_NAME = 'minecraft_server.{}.jar'


class Colors:
    blue = '\033[34m'
    light_blue = '\033[94m'
    yellow_green = '\033[92m'
    green = '\033[32m'
    light_red = '\033[91m'
    red = '\033[31m'
    yellow = '\033[33m'
    end = '\033[0m'


class SweetpotatoIOErrorBase(IOError):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return repr(self.msg)


class BackupFileAlreadyExistsError(SweetpotatoIOErrorBase):
    """Raised when the target backup file already exists."""
    pass


class ConfFileError(SweetpotatoIOErrorBase):
    """Raised when a given conf file doesn't exist or have the right section."""
    pass


class EmptySettingError(SweetpotatoIOErrorBase):
    """Raised when a required setting value is None."""
    pass


class MissingExeError(SweetpotatoIOErrorBase):
    """Raised when a required executable is missing."""
    pass


class NoDirFoundError(SweetpotatoIOErrorBase):
    """Raised when a given directory does not exist."""
    pass


class ServerAlreadyRunningError(SweetpotatoIOErrorBase):
    """Raised when the configured server is already running."""
    pass


class ServerNotRunningError(SweetpotatoIOErrorBase):
    """Raised when the server is not running but was expected to be."""
    pass


class UnsupportedVersionError(SweetpotatoIOErrorBase):
    """Raised when we try to generate a server.properties for an unsupported mc_version."""
    pass


class SweetpotatoConfig:
    """
    Representing the settings sweetpotato needs to function.
    """
    header = "## Generated by {0} at {1}".format(__progname__, datetime.now().strftime('%c'))

    def __init__(self):
        self.backup_dir = None
        self.compression = 'gz'
        self.conf_file = None
        self.forge = None
        self.level_seed = None
        self.mem_format = None
        self.mem_max = None
        self.mem_min = None
        self.mc_version = __mcversion__
        self.permgen = DEFAULT_PERMGEN
        self.port = DEFAULT_SERVER_PORT
        self.running = False
        self.screen_name = None
        self.server_dir = None
        self.world_name = DEFAULT_WORLD_NAME

    def as_conf_file(self):
        print(self.header)
        print('[Settings]')
        return [
            print('{0}: {1}'.format(line, value))
            for line, value in self.__dict__.items()
            if value is not None
            and value is not __mcversion__
            and value is not DEFAULT_SERVER_PORT
            and value is not DEFAULT_WORLD_NAME
            and line is not 'conf_file'
            and line is not 'force'
            and line is not 'running'
        ]

    @property
    def as_json(self):
        return json.dumps(self.__dict__, sort_keys=True, indent=4)

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
        if self.mc_version == '1.8':
            return vanilla_server_properties_18
        elif self.mc_version == '1.7.10':
            return vanilla_server_properties_1710
        else:
            raise UnsupportedVersionError(
                "We can't generate a server.properties for "
                "the version ov MC you are trying to use ({}).".format(self.mc_version)
            )


def agree_to_eula(eula_txt, force, print_pre):
    """
    Checks for a eula.txt file in server, and verifies it contains 'eula=true'.

    @param eula_txt:
    @param force:
    @param print_pre:
    @return:
    """
    # TODO: not do this if the MC version is low enough
    if os.path.isfile(eula_txt) and not force:
        f = open(eula_txt, 'r')
        if 'eula=true' in f.read():
            f.close()
            print(print_pre + Colors.light_blue + 'Eula agreed to!' + Colors.end)
            return True
        else:
            f.close()
    print(print_pre + Colors.light_blue + 'Agreeing to the eula ...', end=' ')
    f = open(eula_txt, 'w')
    f.write('eula=true\n')
    f.close()
    print('Done!' + Colors.end)
    return True


def create_server(settings):
    """
    Check for or create the configured backup_dir and server_dir, check for or
    download the server jar for the configured mc_version, then ensure that
    server.properties matches what our desired configurations are.

    @param settings:
    @return:
    """
    print_pre = '[' + Colors.yellow_green + 'create' + Colors.end + '] '
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
        raise ServerAlreadyRunningError("Can't create '{}' - it's already running!".format(world_name))

    print(print_pre + Colors.blue + 'Creating "{}" ...'.format(world_name) + Colors.end)

    if os.path.isdir(backup_dir):
        print(print_pre + Colors.light_blue + 'Found {}!'.format(backup_dir) + Colors.end)
    else:
        print(print_pre + Colors.light_blue + 'Creating {} ...'.format(backup_dir), end=' ')
        sys.stdout.flush()
        list_or_create_dir(backup_dir)
        print('Done!' + Colors.end)

    if not os.path.isdir(server_dir):
        print(print_pre + Colors.light_blue + 'Creating {} ...'.format(server_dir), end=' ')
        sys.stdout.flush()
        list_or_create_dir(server_dir)
        print('Done!' + Colors.end)
    else:
        print(print_pre + Colors.light_blue + 'Found {}!'.format(server_dir) + Colors.end)

    full_jar_path = os.path.join(server_dir, jar_name)
    if not os.path.isfile(full_jar_path) or force:
        print(print_pre + Colors.light_blue + 'Downloading {} ...'.format(jar_name), end=' ')
        sys.stdout.flush()
        try:
            local_jar = urllib.request.urlretrieve(dl_url, full_jar_path)[0]
            jar = open(local_jar)
            jar.close()
        except urllib.error.HTTPError as e:
            error_and_die(e.msg + ' Is your version valid?')
        print('Done!' + Colors.end)
    else:
        print(print_pre + Colors.light_blue + 'Found {}!'.format(jar_name) + Colors.end)

    eula_txt = os.path.join(server_dir, 'eula.txt')
    agree_to_eula(eula_txt, force, print_pre)

    server_properties = os.path.join(server_dir, 'server.properties')
    write_server_properties(print_pre, server_properties, settings)

    print(print_pre + Colors.blue + 'World "{}" has been created!'.format(world_name) + Colors.end)


def dependency_check(*deps):
    if None in deps:
        raise MissingExeError("Unable to find all dependencies. Please ensure that screen and java are installed.")


def error_and_die(msg):
    """
    For those times when you just want to quit and say why.

    @param msg:
    @return:
    """
    sys.stderr.write(
        Colors.light_red + 'FATAL: ' + Colors.red + msg.__str__().strip("'") + Colors.end + '\n'
    )
    sys.exit(1)


def get_exe_path(exe):
    """
    Checks for exe in $PATH.

    @param exe:
    @return:
    """
    p = subprocess.Popen(['which', exe], stdout=subprocess.PIPE)
    byte_output = p.communicate()[0]
    return byte_output.decode().strip() or None


def get_java_procs():
    """Checks for running Java processes and return the cwd, exe, and pid of any we find."""
    cwd, exe, pid = None, None, None
    p = subprocess.Popen(['pgrep', 'java'], stdout=subprocess.PIPE)
    output = p.communicate()[0]

    if output and len(output.split()) is 1:
        # One Java process
        pid = output.decode().strip()
        c = subprocess.Popen(['/bin/ls', '-l', '/proc/{0}/cwd'.format(pid)], stdout=subprocess.PIPE)
        c_out = c.communicate()[0]
        cwd = c_out.decode().split()[-1]
        e = subprocess.Popen(['/bin/ls', '-l', '/proc/{0}/exe'.format(pid)], stdout=subprocess.PIPE)
        e_out = e.communicate()[0]
        exe = e_out.decode().split()[-1]
    elif output and len(output.split()) > 1:
        # More than one Java process
        proc_list = []
        for P in output.decode().split():
            pid = P
            c = subprocess.Popen(['/bin/ls', '-l', '/proc/{0}/cwd'.format(pid)], stdout=subprocess.PIPE)
            c_out = c.communicate()[0]
            cwd = c_out.decode().split()[-1]
            e = subprocess.Popen(['/bin/ls', '-l', '/proc/{0}/exe'.format(pid)], stdout=subprocess.PIPE)
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
        launch_cmd = 'java -Xms{0}{2} -Xmx{1}{2} -XX:MaxPermSize={3}M -jar {4} nogui'
    else:
        mc_version = settings.mc_version
        jar_name = VANILLA_JAR_NAME.format(mc_version)
        launch_cmd = 'java -Xms{0}{2} -Xmx{1}{2} -jar {3} nogui'
    if jar_name in os.listdir(settings.server_dir):
        return jar_name, launch_cmd
    else:
        return False


def is_forced(settings):
    try:
        force = settings.force
    except AttributeError:
        force = None
    return force


# def is_forge(settings):


def is_screen_started(screen_name):
    """
    Checks the given screen name for a running session,
    returning the PID and name in a 'PID.NAME' formatted string.

    @param screen_name:
    @return:
    """
    l = []

    proc = subprocess.Popen(['screen', '-ls', '{0}'.format(screen_name)], stdout=subprocess.PIPE)
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
    java_procs = get_java_procs()
    server_dir = server_dir_name.rstrip('/')
    if isinstance(java_procs, tuple):
        # just one java proc
        if server_dir in java_procs:
            return java_procs
        else:
            return False
    elif isinstance(java_procs, list):
        # multiple java procs
        for proc in java_procs:
            if server_dir in proc[0]:
                return proc
    return False


def list_or_create_dir(d):
    """
    Returns a list of config files in the config directory, creating the folder if it does not exist.

    :param d:
    """
    if not os.path.isdir(d):
        try:
            os.makedirs(d)
        except PermissionError as e:
            error_and_die(e)
    return os.listdir(d)


def read_conf_file(file, settings):
    """
    The arg 'file' is a conf file path, and 'settings' is a dict containing your settings.

    Checks if 'file' is actually a file, if not checks for 'DEFAULT_FILE'. If that doesn't exist, we return 'settings'
    as it was passed in, the value for 'settings["CONFIG"]' remaining 'None'.

    :param file:
    :param settings:
    """
    # TODO: handle multiple servers by using their world name as a section header name
    # TODO: come up with a system for this
    if len(file.split('/')) == 1:
        file_path = os.path.join(os.getcwd(), file)
    else:
        file_path = file
    if not os.path.isfile(file_path):
        raise ConfFileError('The specified conf file does not exist: {}'.format(file_path))

    section = 'Settings'
    c = configparser.ConfigParser()
    try:
        c.read(file_path)
    except configparser.MissingSectionHeaderError:
        raise ConfFileError("The specified conf file does not have a valid 'Settings' section")

    options = c.options(section)
    options_dict = {}
    for o in options:
        options_dict[o] = c.get(section, o)
    return settings.__dict__.update(**options_dict)


def send_command(command, screen_name):
    """
    Send a command to the server.

    @param command:
    @param screen_name:
    @return:
    """
    cmd_line = 'screen -S {0} -X eval \'stuff "{1}"\015\''.format(screen_name, command)
    cmd_list = shlex.split(cmd_line)
    subprocess.call(cmd_list)


def start_screen(screen_name, server_dir):
    """
    Starts a screen session named 'screen_name' with a cwd of 'server_dir.

    @param screen_name:
    @param server_dir:
    @return:
    """
    command = 'screen -dmS {0}'.format(screen_name)
    os.chdir(server_dir)
    master, slave = pty.openpty()
    cmd_args = shlex.split(command)
    subprocess.Popen(cmd_args, close_fds=True, shell=False, stdin=slave, stdout=slave, stderr=slave)


def start_server(print_pre, settings):
    """
    Starts a configured server.

    @param print_pre:
    @param settings:
    @return:
    """
    jar_name, launch_cmd = get_jar(settings)
    mem_format = settings.mem_format
    mem_max = settings.mem_max
    mem_min = settings.mem_min
    screen_name = settings.screen_name
    server_dir = settings.server_dir
    world_name = settings.world_name

    screen_started = is_screen_started(screen_name)
    server_running = is_server_running(server_dir)

    if settings.forge:
        permgen = settings.permgen
        launch_server = launch_cmd.format(mem_min, mem_max, mem_format[0], permgen, jar_name)
    else:
        launch_server = launch_cmd.format(mem_min, mem_max, mem_format[0], jar_name)

    if not screen_started:
        start_screen(screen_name, server_dir)

    if not server_running:
        if print_pre:
            print(print_pre + Colors.light_blue + 'Starting "{}" ...'.format(world_name), end=' ')
        else:
            print('starting "{}" ...'.format(world_name), end=' ')
        sys.stdout.flush()
        send_command(launch_server, screen_name)
        print('Done!' + Colors.end)
    else:
        raise ServerAlreadyRunningError('World "{0}" already running with PID {1}'.format(
            settings.world_name,
            server_running[-1]
        ))


def stop_server(print_pre, screen_name, server_dir, world_name):
    """
    Stops a configured server.

    @param print_pre:
    @param screen_name:
    @param server_dir:
    @param world_name:
    @return:
    """
    server_running = is_server_running(server_dir)

    if server_running:
        server_pid = server_running[-1]
        print(print_pre + Colors.light_blue + 'Stopping "{}" ...'.format(world_name), end=' ')
        sys.stdout.flush()
        wait_for_server_shutdown(screen_name, server_pid)
        send_command('exit', screen_name)
        print('Done!' + Colors.end)
    else:
        raise ServerNotRunningError('Cannot stop "{}" - it is not running!'.format(world_name))


def restart_server(print_pre, settings):
    """
    Restarts a configured server.

    @param print_pre:
    @param settings:
    @return:
    """
    jar_name, launch_cmd = get_jar(settings)
    mem_format = settings.mem_format
    mem_max = settings.mem_max
    mem_min = settings.mem_min
    screen_name = settings.screen_name
    server_dir = settings.server_dir
    world_name = settings.world_name

    screen_started = is_screen_started(screen_name)
    server_running = is_server_running(server_dir)

    if settings.forge:
        permgen = settings.permgen
        launch_server = launch_cmd.format(mem_min, mem_max, mem_format[0], permgen, jar_name)
    else:
        launch_server = launch_cmd.format(mem_min, mem_max, mem_format[0], jar_name)

    if not screen_started:
        start_screen(screen_name, server_dir)

    if server_running:
        server_pid = server_running[-1]
        print(print_pre + Colors.light_blue + 'Restarting {} ...'.format(world_name), end=' ')
        sys.stdout.flush()
        wait_for_server_shutdown(screen_name, server_pid)
    else:
        print(print_pre + Colors.light_blue + 'Starting {} ...'.format(world_name), end=' ')
        sys.stdout.flush()
    send_command(launch_server, screen_name)
    print('Done!' + Colors.end)


def run_server_backup(print_pre, settings, offline=False):
    """
    Runs the configured backup on the configured server.

    @param print_pre:
    @param settings:
    @param offline:
    @return:
    """
    backup_dir = settings.backup_dir
    date_stamp = datetime.now().strftime('%Y-%m-%d')
    force = is_forced(settings)
    forge = settings.forge
    jar_name = VANILLA_JAR_NAME.format(settings.mc_version)
    mem_format = settings.mem_format
    mem_max = settings.mem_max
    mem_min = settings.mem_min
    launch_server = 'java -Xms{0}{2} -Xmx{1}{2} -jar {3} nogui'.format(mem_min, mem_max, mem_format[0], jar_name)
    screen_name = settings.screen_name
    server_dir = settings.server_dir
    world_name = settings.world_name
    compression = settings.compression

    backup_file = '{0}_{1}.tar.{2}'.format(date_stamp, world_name, compression)
    full_path_to_backup_file = os.path.join(backup_dir, backup_file)
    server_running = is_server_running(server_dir)

    if offline:
        print(print_pre + Colors.light_blue, end=' ')
        if server_running:
            server_pid = server_running[-1]
            print('Stopping "{}" ...'.format(world_name), end=' ')
            sys.stdout.flush()
            wait_for_server_shutdown(screen_name, server_pid)
            print('backing up ...', end=' ')
        else:
            print('Backing up "{}" ...'.format(world_name), end=' ')
        sys.stdout.flush()
    else:
        send_command('save-all', screen_name)
        send_command('save-off', screen_name)
        print(print_pre + Colors.light_blue + 'Running live backup of "{}"  ...'.format(world_name), end=' ')
        sys.stdout.flush()
        send_command('say Server backing up now', screen_name)

    list_or_create_dir(backup_dir)
    if not force:
        try:
            with open(full_path_to_backup_file, 'rb'):
                raise BackupFileAlreadyExistsError('File "{}" already exists!'.format(full_path_to_backup_file))
        except IOError:
            pass

    tar = tarfile.open(full_path_to_backup_file, 'w:{}'.format(compression))
    if forge:
        tar.add(server_dir, exclude=lambda x: 'dynmap' in x)
    else:
        tar.add(server_dir)
    tar.close()

    if not offline:
        send_command('say Backup complete', screen_name)
        send_command('save-on', screen_name)

    screen_started = is_screen_started(screen_name)
    server_running = is_server_running(server_dir)
    if offline and not server_running:
        if not screen_started:
            start_screen(screen_name, server_dir)
        print('starting "{}" ...'.format(world_name), end=' ')
        sys.stdout.flush()
        send_command(launch_server, screen_name)
    print('Done!' + Colors.end)


def run_webui(settings):
    """
    Run the WebUI or print a message about why not.

    @param settings:
    @return:
    """
    if bottle:
        app = bottle.app()
        static_path = os.path.join(BASE_DIR, 'data/static')
        tpl_path = os.path.join(BASE_DIR, 'data/tpl')

        bottle.debug(False)
        bottle.TEMPLATE_PATH.insert(0, tpl_path)

        if markdown:
            def readme_md_to_html(md_file):
                """
                Runs markdown() on a markdown-formatted README.md file to generate html.

                @param md_file:
                @return:
                """
                html = "% rebase('base.tpl', title='{}')\n".format(md_file)
                m = open(md_file, 'r')
                for l in m.readlines():
                    html += markdown(l)
                m.close()
                return html

            @bottle.route('/readme')
            def readme():
                path = bottle.request.path
                html = readme_md_to_html(os.path.join(BASE_DIR, 'README.md'))
                return bottle.template(
                    html,
                    path=path)
        else:
            @bottle.route('/readme')
            @bottle.view('readme_no_md')
            def readme():
                path = bottle.request.path
                return {'path': path}

        @bottle.get('/backup')
        @bottle.post('/backup')
        @bottle.view('backup')
        def backups():
            path = bottle.request.path
            request_method = bottle.request.method
            todays_file = '{0}_{1}.tar.{2}'.format(
                datetime.now().strftime('%Y-%m-%d'),
                settings.world_name,
                settings.compression
            )
            # noinspection PyTypeChecker
            backup_dir_contents = os.listdir(settings.backup_dir)
            if bottle.request.method == 'POST':
                t = Thread(target=run_server_backup, args=('', settings))
                t.daemon = True
                t.start()
            return {
                'backup_dir_contents': backup_dir_contents,
                'path': path,
                'request_method': request_method,
                'todays_file': todays_file,
                'world_name': settings.world_name
            }

        @bottle.route('/')
        @bottle.view('index')
        def index():
            is_running = is_server_running(settings.server_dir)
            path = bottle.request.path
            pid = None
            if is_running:
                pid = is_running[-1]
            return {
                'path': path,
                'pid': pid,
                'settings': settings,
                'server_running': is_running
            }

        @bottle.route('/json')
        def as_json():
            settings.running = is_server_running(settings.server_dir)
            return settings.__dict__

        @bottle.get('/server')
        @bottle.post('/server')
        @bottle.view('server')
        def server():
            is_running = is_server_running(settings.server_dir)
            path = bottle.request.path
            request_method = bottle.request.method
            restart = None
            start = None
            stop = None
            if bottle.request.method == 'POST':
                postdata = bottle.request.POST
                restart = postdata.get('restart')
                start = postdata.get('start')
                stop = postdata.get('stop')
                if restart is not None:
                    t = Thread(target=restart_server, args=('', settings))
                    t.daemon = True
                    t.start()
                elif start is not None:
                    t = Thread(target=start_server, args=('', settings))
                    t.daemon = True
                    t.start()
                elif stop is not None:
                    t = Thread(target=stop_server,
                               args=('', settings.screen_name, settings.server_dir, settings.world_name))
                    t.daemon = True
                    t.start()
            return {
                'path': path,
                'request_method': request_method,
                'restart': restart,
                'start': start,
                'stop': stop,
                'server_running': is_running,
                'world_name': settings.world_name
            }

        # noinspection PyUnresolvedReferences
        @bottle.route('/backups/<file_path:path>')
        def serve_backup(file_path):
            return bottle.static_file(file_path, root=settings.backup_dir)

        # noinspection PyUnresolvedReferences
        @bottle.route('/static/<file_path:path>')
        def serve_static(file_path):
            return bottle.static_file(file_path, root=static_path)

        @bottle.error(404)
        @bottle.view('404')
        def error404(error):
            path = bottle.request.path
            return {
                'error': error,
                'path': path
            }

        @bottle.error(500)
        @bottle.view('500')
        def error500(error):
            path = bottle.request.path
            return {
                'error': error,
                'path': path
            }
        bottle.run(app=app, quiet=False, reloader=True)
    else:
        error_and_die('The web component requires both bottle.py to function, '
                      'with Python-Markdown as an optional dependency.')


def validate_directories(*dirs):
    """
    Ensures that the passed-in directories exist.

    @param dirs:
    @return:
    """
    for d in dirs:
        if not os.path.isdir(d):
            raise NoDirFoundError(
                'The configured directory "{}" does not exist. Do you need to run --create?'.format(d)
            )


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

    # set a default screen name if need be
    if 'screen_name' in missing:
        settings.screen_name = settings.world_name
        missing.remove('screen_name')

    if missing:
        raise EmptySettingError('One or more required settings are not present: {}'.format(' '.join(missing)))
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
        send_command('stop', screen_name)


def write_server_properties(print_pre, file, settings):
    """
    Checks for a server.properties for the specified server_dir
    and world_name, and writes if need be (or forced)

    @param print_pre:
    @param file:
    @param settings:
    @return:
    """
    def do_the_write():
        print(print_pre + Colors.light_blue + 'Generating server.properties ...', end=' ')
        sys.stdout.flush()
        file_to_write = open(file, 'w')
        try:
            for l in settings.as_serverproperties.split('\n'):
                file_to_write.write(l + '\n')
        except UnsupportedVersionError as e:
            error_and_die(e)
        file_to_write.close()
        print('Done!' + Colors.end)

    found_msg = print_pre + Colors.light_blue + 'Found server.properties!' + Colors.end
    if os.path.isfile(file):
        f = open(file, 'r')
        f_readlines = f.readlines()
        # Write a new file if any of the three values we change have changed
        if not 'level-name={}\n'.format(settings.world_name) in f_readlines \
            or not 'server-port={}\n'.format(settings.port) in f_readlines \
            or not 'level-seed={}\n'.format(settings.level_seed or '') in f_readlines \
                or settings.force:
            do_the_write()
        else:
            print(found_msg)
        f.close()
    else:
        do_the_write()


def arg_parse(argz):
    parser = argparse.ArgumentParser(description=DESCRIPTION, prog=__progname__)

    actions = parser.add_mutually_exclusive_group(required=True)
    actions.add_argument('-b', '--backup', action='store_true', help='back up your Minecraft server (live)')
    actions.add_argument('-C', '--create', action='store_true', help='create a server from settings')
    actions.add_argument('-g', '--genconf', action='store_true', help='generate conf file from passed-in CLI arguments')
    actions.add_argument('-j', '--json', action='store_true', help='output settings as json')
    actions.add_argument('-o', '--offline', action='store_true', help='make an offline backup (stops the server)')
    actions.add_argument('-r', '--restart', action='store_true', help='restart the server')
    actions.add_argument('--start', action='store_true', help='start the server in a screen session')
    actions.add_argument('--stop', action='store_true', help='stop the server')
    actions.add_argument('-W', '--web', action='store_true', help='run the WebUI')
    # TODO: port option for web ui
    # TODO: some sort of --fork option for the WebUI, to run it in the background

    settings = parser.add_argument_group('Settings', 'config options for %(prog)s')
    settings.add_argument('-c', '--conf', help='config file containing your settings', metavar='CONF FILE')
    settings.add_argument('-d', '--backup-dir', help='the FULL path to your backups folder',
                          metavar='/path/to/backups')
    settings.add_argument('-F', '--force', help='forces writing of server files, even when they already exist',
                          action='store_true')

    forge_settings = settings.add_mutually_exclusive_group()
    forge_settings.add_argument('-f', '--forge', help='version of Forge you are using.', metavar='FORGE VERSION')
    forge_settings.add_argument('-P', '--permgen',
                                help='Amount of permgen to use in MB. Default: {}'.format(DEFAULT_PERMGEN))

    settings.add_argument('--level-seed', '--seed', help='optional and only applied during world creation')
    settings.add_argument('-p', '--port', help='port you wish to run your server on. Default: 25565')
    settings.add_argument('-s', '--server-dir', metavar='/path/to/server',
                          help='set the FULL path to the directory containing your server files')
    settings.add_argument('-S', '--screen', metavar='SCREEN NAME',
                          help='set the name of your screen session. Default: the same as your world')
    settings.add_argument('-v', '--mc-version', metavar='MC VERSION',
                          help='set the version of minecraft. Default: The latest stable')
    settings.add_argument('-w', '--world', help='set the name of your Minecraft world. Default: SweetpotatoWorld',
                          metavar='WORLD NAME')
    settings.add_argument('-z', '--compression', choices=['bz2', 'gz', 'xz'], dest='compression',
                          help='select compression type. Default: gz')

    mem_values = settings.add_mutually_exclusive_group()
    mem_values.add_argument('-gb', '-GB', help='set min/max memory usage (in gigabytes)',
                            metavar=('MIN', 'MAX'), nargs=2)
    mem_values.add_argument('-mb', '-MB', help='set min/max memory usage (in megabytes)',
                            metavar=('MIN', 'MAX'), nargs=2)
    parser.add_argument('-V', '--version', action='version', version='%(prog)s {0}'.format(__version__))

    settings = SweetpotatoConfig()

    try:
        read_conf_file(DEFAULT_CONF_FILE, settings)
    except (configparser.NoSectionError, ConfFileError):
        pass
    # TODO: read from json input?

    args = parser.parse_args(argz)
    if args.conf:
        try:
            read_conf_file(args.conf, settings)
        except ConfFileError as e:
            error_and_die(e)
        settings.conf_file = args.conf
    if args.backup_dir:
        settings.backup_dir = args.backup_dir
    if args.force:
        settings.force = args.force
    if args.forge:
        settings.forge = args.forge
    if args.mb:
        settings.mem_format = 'MB'
        settings.mem_max = args.mb[1]
        settings.mem_min = args.mb[0]
    elif args.gb:
        settings.mem_format = 'GB'
        settings.mem_max = args.gb[1]
        settings.mem_min = args.gb[0]
    if args.level_seed:
        settings.level_seed = args.level_seed
    if args.permgen:
        settings.permgen = args.permgen
    if args.port:
        settings.port = args.port
    if args.server_dir:
        settings.server_dir = args.server_dir
    if args.screen:
        settings.screen_name = args.screen
    if args.mc_version:
        settings.mc_version = args.mc_version
    if args.world:
        settings.world_name = args.world
    if args.compression:
        settings.compression = args.compression

    if settings.forge:
        settings.mc_version = settings.forge.split('-')[0]

    try:
        validate_settings(settings)
    except EmptySettingError as e:
        error_and_die(e)

    try:
        validate_directories(settings.backup_dir, settings.server_dir)
    except NoDirFoundError as e:
        if not args.create and not args.genconf:
            error_and_die(e)

    try:
        validate_mem_values(settings.mem_min, settings.mem_max)
    except ValueError:
        error_and_die('The maximum memory value must be greater than the minimum!')

    running = is_server_running(settings.server_dir)

    if args.backup:
        print_pre = '[' + Colors.yellow_green + 'live-backup' + Colors.end + '] '
        try:
            run_server_backup(print_pre, settings)
        except BackupFileAlreadyExistsError as e:
            send_command('say Backup Done!', settings.screen_name)
            error_and_die(e)
    elif args.create:
        try:
            create_server(settings)
        except ServerAlreadyRunningError as e:
            error_and_die(e.msg.strip('"'))
    elif args.genconf:
        settings.as_conf_file()
    elif args.json:
        if running:
            settings.running = running
        print(settings.as_json)
    elif args.offline:
        print_pre = '[' + Colors.yellow_green + 'offline-backup' + Colors.end + '] '
        try:
            run_server_backup(print_pre, settings, offline=True)
        except BackupFileAlreadyExistsError as e:
            start_server(None, settings)
            error_and_die(e)
    elif args.restart:
        print_pre = '[' + Colors.yellow_green + 'restart' + Colors.end + '] '
        try:
            restart_server(print_pre, settings)
        except BackupFileAlreadyExistsError as e:
            error_and_die(e)
    elif args.start:
        print_pre = '[' + Colors.yellow_green + 'start' + Colors.end + '] '
        try:
            start_server(print_pre, settings)
        except ServerAlreadyRunningError as e:
            error_and_die(e)
    elif args.stop:
        print_pre = '[' + Colors.yellow_green + 'stop' + Colors.end + '] '
        try:
            stop_server(
                print_pre,
                settings.screen_name,
                settings.server_dir,
                settings.world_name
            )
        except ServerNotRunningError as e:
            error_and_die(e)
    elif args.web:
            run_webui(settings)
    else:
        parser.print_usage()


def main():
    # ensure dependencies are here
    try:
        dependency_check(
            get_exe_path('java'),
            get_exe_path('screen')
        )
    except MissingExeError as e:
        error_and_die(e)

    # process cli args and do our stuff
    argz = sys.argv[1:]
    arg_parse(argz)


if __name__ == '__main__':
    main()
