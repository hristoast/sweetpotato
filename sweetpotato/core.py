# TODO: @run_if_bottle decorator and the like
import configparser
import json
import os
import sys
import tarfile

from datetime import datetime
from .common import DEFAULT_COMPRESSION, DEFAULT_EXCLUDE_FILES, \
    DEFAULT_SCREEN_NAME, DEFAULT_SERVER_PORT, DEFAULT_WORLD_NAME, MCVERSION, \
    PROGNAME, PYTHON33_OR_GREATER, emit_msg
from .error import ConfFileError, EmptySettingError, NoDirFoundError, \
    ServerNotRunningError
from .screen import is_screen_started
from .server import get_uptime, get_uptime_raw, list_players, \
    list_players_as_list, send_command
from .system import create_dir, error_and_die, is_forced


class SweetpotatoConfig:
    """Representing the settings sweetpotato needs to function."""
    header = "## Generated by {0} at {1}".format(
        PROGNAME, datetime.now().strftime('%c'))

    def __init__(self):
        self.backup_dir = None
        self.compression = DEFAULT_COMPRESSION
        self.conf_file = None
        self.exclude_files = DEFAULT_EXCLUDE_FILES
        self.fancy = False
        self.force = False
        self.forge = None
        self.level_seed = None
        self.mem_format = None
        self.mem_max = None
        self.mem_min = None
        self.mc_version = MCVERSION
        self.port = DEFAULT_SERVER_PORT
        self.running = False
        self.screen_name = DEFAULT_SCREEN_NAME
        self.server_dir = None
        self.playerdata_only = False
        self.verbose_backup = False
        self.world_name = DEFAULT_WORLD_NAME
        self.world_only = False

    @property
    def as_conf_file(self):
        conf = self.header + '\n'
        conf += '[Settings]\n'
        for k, v in self.__dict__.items():
            if v is not None \
                    and k is not 'conf_file' \
                    and k is not 'exclude_files' \
                    and k is not 'force' \
                    and k is not 'running'\
                    and not (v is False and k is 'fancy'):
                conf += '{0}: {1}\n'.format(k, v)
            elif k == 'exclude_files':
                conf += '{}:'.format(k)
                if isinstance(v, str):
                    conf += ' {}\n'.format(v)
                else:
                    for i in v:
                        conf += (' ' + i)
                    conf += '\n'
        return conf.strip()

    @property
    def as_json(self):
        # TODO: don't copy?
        self_dict = self.__dict__.copy()
        try:
            players = list_players_as_list(list_players(self))
            raw = get_uptime_raw(self.server_dir, self.world_name, False)
            u = get_uptime(raw)
            uptime = {
                'days': u[0],
                'hours': u[1],
                'minutes': u[2],
                'seconds': u[3]}
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
        if self.mc_version == '1.7.10':
            return vanilla_server_properties_1710
        else:
            return vanilla_server_properties_18
        # TODO: can probably generalize this ...
        # else:
        #     raise UnsupportedVersionError(
        #         "We can't generate a server.properties for "
        #         "the version ov MC you are trying to use ({}).".format(
        #             self.mc_version))


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
    # TODO: getboolean() seems to _only_ work for true/false -- not True, yes, no, False, or anything else...
    if len(file.split('/')) == 1:
        file_path = os.path.join(os.getcwd(), file)
    else:
        file_path = file
    if not os.path.isfile(file_path):
        raise ConfFileError(
            'The specified conf file does not exist: {}'.format(file_path))

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

    exclude = c[section].get("exclude_files")
    if exclude:
        exclude_list = exclude.split(" ")
    else:
        exclude_list = []
    if settings.exclude_files not in exclude_list:
        exclude_list.append(settings.exclude_files)

    fancy = c[section].getboolean('fancy')
    world_only = c[section].getboolean('world_only')
    try:
        # Special booleans that can be set with truthy values other than True.
        # Or values that we serialize into Python data structures.
        options_dict.pop('exclude_files')
        options_dict.update(exclude_files=exclude_list)
        options_dict.pop('fancy')
        options_dict.update(fancy=fancy)
        options_dict.pop('world_only')
        options_dict.update(world_only=world_only)
    except KeyError:
        pass
    return settings.__dict__.update(**options_dict)


def reread_settings(old_settings):
    """
    Reloads settings. Useful for the WebUI, in case you've modified your
    conf file since having started it.

    @param old_settings:
    @return: s
    """
    # Create a fresh settings object to work with
    s = SweetpotatoConfig()
    # Now read from the old, passed-in conf file
    if old_settings.conf_file:
        read_conf_file(old_settings.conf_file, s)
    return s


# TODO: tweak the file name
def run_server_backup(exclude_files: list, settings: SweetpotatoConfig,
                      quiet: bool, running: bool, world_only: bool,
                      force=False, playerdata_only=False, verbose_backup=False):
    """
    Runs the configured backup on the configured server.

    @param exclude_files:
    @param settings:
    @param quiet:
    @param running:
    @param world_only:
    @param force:
    @param verbose_backup:
    @return:
    """
    backup_dir = settings.backup_dir
    # TODO: make this toggle-able
    date_stamp = datetime.now().strftime('%Y-%m-%d-%H%M%S')
    if not force:
        force = is_forced(settings)

    screen_name = settings.screen_name
    server_dir = settings.server_dir
    server_dir_name = server_dir.split(os.path.sep)[-1]
    world_name = settings.world_name
    compression = settings.compression

    if playerdata_only:
        backup_file = '{0}_{1}_playerdata.tar.{2}'.format(date_stamp, world_name, compression)
    else:
        backup_file = '{0}_{1}.tar.{2}'.format(date_stamp, world_name, compression)
    full_path_to_backup_file = os.path.join(backup_dir, backup_file)
    backup_made_today = os.path.isfile(full_path_to_backup_file)

    def _can_xz():
        if PYTHON33_OR_GREATER:
            return False
        else:
            return True

    def _exclude_me(tarinfo):
        # TODO: maybe some day don't do whatever it is I do that forces me to use isinstance ...
        # Excluding just one file
        if isinstance(exclude_files, str):
            if tarinfo.name == exclude_files:
                return None

        # List of files to exclude
        else:
            for _file in exclude_files:
                if _file in tarinfo.name:
                    return None
        emit_msg("Adding: " + tarinfo.name, quiet=(not verbose_backup))
        return tarinfo

    if backup_made_today and not force:
        sys.stdout.flush()
        try:
            with open(full_path_to_backup_file, 'rb'):
                error_and_die('File "{}" already exists!'.format(full_path_to_backup_file),
                              quiet=quiet)
        except IOError:
            pass

    if running and not playerdata_only:
        send_command('save-all', is_screen_started(screen_name))
        send_command('save-off', is_screen_started(screen_name))
        send_command('say Server backing up now',
                     is_screen_started(screen_name))

    create_dir(backup_dir)

    if not _can_xz() and settings.compression == 'xz':
        compression = 'gz'

    os.chdir(os.path.join(server_dir, '..'))
    tar = tarfile.open(full_path_to_backup_file, 'w:{}'.format(compression))
    emit_msg('Backing up "{}" ... '.format(world_name))
    if playerdata_only:
        try:
            tar.add(os.path.join(server_dir_name, world_name, "playerdata"), filter=_exclude_me)
        except FileNotFoundError:
            pass
    elif world_only:
        # File "/home/llx/.local/lib/python3.6/site-packages/sweetpotato/core.py", line 332, in run_server_backup
        #   tar.add(os.path.join(server_dir_name, world_name), filter=_exclude_me)
        # FileNotFoundError: [Errno 2] No such file or directory: 'MMGA/MMGA/level.dat_new'
        try:
            tar.add(os.path.join(server_dir_name, world_name), filter=_exclude_me)
        except FileNotFoundError:
            pass
    else:
        try:
            tar.add(server_dir_name, filter=_exclude_me)
        except FileNotFoundError:
            pass
    tar.close()

    if running and not playerdata_only:
        send_command('say Backup complete', is_screen_started(screen_name))
        send_command('save-on', is_screen_started(screen_name))

    if not quiet:
        # TODO: wtf is this if for?!
        if verbose_backup:
            emit_msg('Backup of "{}" completed!'.format(world_name), quiet=quiet)
        else:
            emit_msg('Backup of "{}" completed!'.format(world_name))
        emit_msg("Backup file: " + full_path_to_backup_file)


def save_settings(settings):
    # TODO: this
    pass


def validate_directories(*dirs):
    """
    Ensures that the passed-in directories exist.

    @param dirs:
    @return:
    """
    for d in dirs:
        if d:
            if not os.path.isdir(d):
                raise NoDirFoundError(
                    'The configured directory "{}" does not exist.'
                    ' Do you need to run --create?'.format(d))


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
        error_and_die('The provided memory values are invalid!')
    except TypeError:
        error_and_die('No memory values were provided!')

    if min_value > max_value:
        raise ValueError


def validate_settings(settings):
    """
    Ensures that all required settings have a value.

    @param settings:
    @return:
    """
    missing = []
    if missing:
        raise EmptySettingError(
            'One or more required settings are not present: {}'.format(
                ' '.join(missing)))
    else:
        return True
