import argparse
import configparser
import os
import sys

from .common import (COMPRESSION_CHOICES, DAEMON_PY3K_ERROR, DEFAULT_COMPRESSION,
                     DEFAULT_CONF_FILE, DEFAULT_LOG_DIR, DEFAULT_PERMGEN,
                     DEFAULT_PIDFILE, DEFAULT_SERVER_PORT, DEFAULT_WEBUI_PORT,
                     DEFAULT_WORLD_NAME, DEP_PKGS, DESCRIPTION, MCVERSION,
                     PROGNAME, VERSION, Colors, sp_prnt)
from .core import (SweetpotatoConfig, read_conf_file, run_server_backup,
                   validate_directories, validate_mem_values, validate_settings)
try:
    from .daemon import daemon_action
except ImportError:
    daemon_action = None
from .error import (BackupFileAlreadyExistsError, ConfFileError,
                    EmptySettingError, MissingExeError, NoDirFoundError,
                    ServerAlreadyRunningError, ServerNotRunningError)
from .server import (create_server, is_server_running, get_uptime, get_uptime_raw,
                     get_uptime_string, list_players, restart_server, save_all,
                     send_command, start_server, stop_server)
from .system import dependency_check, error_and_die, get_exe_path
from .web import run_webui


def setup_args(args):
    parser = argparse.ArgumentParser(description=DESCRIPTION, prog=PROGNAME)

    actions = parser.add_mutually_exclusive_group(required=True)
    actions.add_argument('-b', '--backup', action='store_true',
                         help='back up your Minecraft server (live)')
    actions.add_argument('-C', '--create', action='store_true',
                         help='create a server from settings')
    actions.add_argument('-D', '--daemon',
                         choices=['stop', 'start', 'restart'],
                         help="run the WebUI as a background process")
    actions.add_argument('-g', '--genconf', action='store_true',
                         help='generate conf file from passed-in arguments')
    actions.add_argument('-j', '--json', action='store_true',
                         help='output settings as json')
    actions.add_argument('-l', '--list', action='store_true',
                         help='list logged-in players')
    actions.add_argument('-o', '--offline', action='store_true',
                         help='make an offline backup (stops the server)')
    actions.add_argument('-r', '--restart', action='store_true',
                         help='restart the server')
    actions.add_argument('-A', '--save-all', '--save', action='store_true',
                         help='Send a "save-all" to the server')
    actions.add_argument('--say', help=argparse.SUPPRESS)
    actions.add_argument('--start', action='store_true',
                         help='start the server in a screen session')
    # actions.add_argument('--save', action='store_true',
    #                      help='save the current config')
    actions.add_argument('--stop', action='store_true', help='stop the server')
    # actions.add_argument('--testing', action='store_true',
    #                      help=argparse.SUPPRESS)
    actions.add_argument('-U', '--uptime', action='store_true',
                         help='Show server uptime in hours')
    actions.add_argument('-W', '--web', action='store_true',
                         help='run the WebUI')
    # actions.add_argument('--wipe', action='store_true', help='Wipe configs')

    settings = parser.add_argument_group('Settings',
                                         'config options for %(prog)s')
    settings.add_argument('-c', '--conf',
                          help='config file containing your settings',
                          metavar='CONF FILE')
    settings.add_argument('-d', '--backup-dir',
                          help='the FULL path to your backups folder',
                          metavar='/path/to/backups')
    settings.add_argument('-x', '--fancy', action='store_true',
                          help="print json with fancy indentation and sorting")
    settings.add_argument('-F', '--force',
                          help='forces writing of server files,'
                               ' even when they already exist',
                          action='store_true')
    settings.add_argument('--level-seed', '--seed', metavar="LEVEL SEED",
                          help='optional and only applied'
                               'during world creation')
    settings.add_argument('-p', '--port',
                          help='port you wish to run your server on.'
                               ' Default: ' + DEFAULT_SERVER_PORT)
    settings.add_argument('-q', '--quiet', action='store_true',
                          help='Silence all output')
    settings.add_argument('-s', '--server-dir', metavar='/path/to/server',
                          help='set the FULL path to the directory'
                               ' containing your server files')
    settings.add_argument('-S', '--screen', metavar='SCREEN NAME',
                          help='set the name of your screen session.'
                               ' Default: the same as your world')
    settings.add_argument('-v', '--mc-version', metavar='MC VERSION',
                          help='set the version of minecraft.'
                               ' Default: ' + MCVERSION)
    settings.add_argument('-w', '--world', metavar='WORLD NAME',
                          help='set the name of your Minecraft world.'
                               ' Default: ' + DEFAULT_WORLD_NAME)
    settings.add_argument('--world-only', help='back up only the world files',
                          action='store_true')
    settings.add_argument('-z', '--compression', choices=COMPRESSION_CHOICES,
                          dest='compression',
                          help='select compression type.'
                               ' Default: ' + DEFAULT_COMPRESSION)

    mem_values = settings.add_mutually_exclusive_group()
    mem_values.add_argument('-gb', '-GB',
                            help='set min/max memory usage (in gigabytes)',
                            metavar=('MIN', 'MAX'), nargs=2)
    mem_values.add_argument('-mb', '-MB',
                            help='set min/max memory usage (in megabytes)',
                            metavar=('MIN', 'MAX'), nargs=2)

    forge_settings = parser.add_argument_group('Mods',
                                               'Options for Forge users')
    forge_settings.add_argument('-f', '--forge',
                                help='version of Forge you are using.',
                                metavar='FORGE VERSION')
    forge_settings.add_argument('-P', '--permgen',
                                help='Amount of permgen to use in MB.'
                                     ' Default: ' + DEFAULT_PERMGEN)

    webui_settings = parser.add_argument_group('WebUI',
                                               'More configuration options for'
                                               ' the WebUI and daemon mode')
    webui_settings.add_argument('--log-dir', '-L', metavar="LOG DIR",
                                help='set the log location.'
                                     ' Default: ' + DEFAULT_LOG_DIR)
    webui_settings.add_argument('--pidfile', '-pid', metavar='PID FILE',
                                help='set the pid file used when running in'
                                     ' daemon mode. Default: ' +
                                     DEFAULT_PIDFILE)
    webui_settings.add_argument('--webui-port', dest='webui_port',
                                metavar='WEBUI PORT',
                                help='Port to bind to for the WebUI.'
                                     ' Default: ' + str(DEFAULT_WEBUI_PORT))

    parser.add_argument('-V', '--version', action='version',
                        version='%(prog)s ' + VERSION)

    args = parser.parse_args(args)
    s = SweetpotatoConfig()

    # Read a passed-in conf file
    if args.conf:
        try:
            read_conf_file(args.conf, s)
        except ConfFileError as e:
            error_and_die(e)
        s.conf_file = os.path.realpath(args.conf)
    # Or try to read the default conf file
    elif not args.conf:
        try:
            read_conf_file(DEFAULT_CONF_FILE, s)
            s.conf_file = DEFAULT_CONF_FILE
        except (configparser.NoSectionError, ConfFileError):
            pass
    if args.backup_dir:
        s.backup_dir = args.backup_dir
    if args.fancy:
        s.fancy = True
    if args.force:
        s.force = args.force
    if args.forge:
        s.forge = args.forge
    if args.mb:
        s.mem_format = 'MB'
        s.mem_max = args.mb[1]
        s.mem_min = args.mb[0]
    elif args.gb:
        s.mem_format = 'GB'
        s.mem_max = args.gb[1]
        s.mem_min = args.gb[0]
    if args.level_seed:
        s.level_seed = args.level_seed
    if args.permgen:
        s.permgen = args.permgen
    if args.port:
        s.port = args.port
    if args.quiet:
        s.quiet = True
    else:
        s.quiet = False
    if args.server_dir:
        s.server_dir = args.server_dir
    if args.screen:
        s.screen_name = args.screen
    if args.mc_version:
        s.mc_version = args.mc_version
    if args.webui_port:
        s.webui_port = args.webui_port
    if args.world:
        s.world_name = args.world
    if args.world_only:
        s.world_only = True
    if args.compression:
        s.compression = args.compression

    if s.forge:
        s.mc_version = s.forge.split('-')[0]
        if not s.permgen:
            s.permgen = DEFAULT_PERMGEN

    try:
        validate_settings(s)
        if s.world_name != DEFAULT_WORLD_NAME and not args.screen and \
           s.screen_name == DEFAULT_WORLD_NAME:
            s.screen_name = s.world_name
    except EmptySettingError as e:
        error_and_die(e)

    try:
        validate_directories(s.backup_dir, s.server_dir)
    except NoDirFoundError as e:
        if not args.create and not args.genconf:
            error_and_die(e)

    try:
        validate_mem_values(s.mem_min, s.mem_max)
    except ValueError:
        error_and_die('The maximum memory value must be greater'
                      ' than the minimum!')

    running = is_server_running(s.server_dir)

    if args.backup:
        pre = '[' + Colors.yellow_green + 'live-backup' + Colors.end + ']'
        try:
            run_server_backup(pre, s, s.quiet, running, s.world_only)
        except BackupFileAlreadyExistsError as e:
            send_command('say Backup Done!', s.screen_name)
            error_and_die(e)
    elif args.create:
        try:
            create_server(s, s.quiet)
        except ServerAlreadyRunningError as e:
            error_and_die(e.msg.strip('"'))
    elif args.daemon:
        if daemon_action:
            daemon_action(args.daemon)
        else:
            error_and_die(DAEMON_PY3K_ERROR)
    elif args.genconf:
        print(s.as_conf_file)
    elif args.json:
        if running:
            s.running = running
        print(s.as_json)
    elif args.list:
        if running:
            pre = '[' + Colors.yellow_green + 'list' + Colors.end + ']'
            players = list_players(s)
            if players:
                for p in players:
                    sp_prnt(p.strip(), pre=pre)
            else:
                sp_prnt('Nobody on right now :(', pre=pre, quiet=s.quiet)
        else:
            error_and_die(s.world_name + " is not running!", quiet=s.quiet)
    elif args.offline:
        pre = '[' + Colors.yellow_green + 'offline-backup' + Colors.end + ']'
        try:
            run_server_backup(pre, s, s.quiet, running, s.world_only, offline=True)
        except BackupFileAlreadyExistsError as e:
            start_server(None, s, s.quiet)
            error_and_die(e)
    elif args.save_all:
        if running:
            pre = '[' + Colors.yellow_green + 'save-all' + Colors.end + ']'
            sp_prnt('Saving "{}" ...'.format(s.world_name), quiet=s.quiet, end='')
            save_all(s)
            sp_prnt('Done!', quiet=s.quiet)
        else:
            error_and_die("{} is not running!".format(s.world_name), quiet=s.quiet)
    elif args.say:
        send_command('say ' + args.say, s.screen_name)
    elif args.restart:
        pre = '[' + Colors.yellow_green + 'restart' + Colors.end + ']'
        try:
            restart_server(pre, s, s.quiet)
        except BackupFileAlreadyExistsError as e:
            error_and_die(e)
    elif args.start:
        pre = '[' + Colors.yellow_green + 'start' + Colors.end + ']'
        try:
            start_server(pre, s, s.quiet)
        except ServerAlreadyRunningError as e:
            error_and_die(e, quiet=s.quiet)
    elif args.stop:
        pre = '[' + Colors.yellow_green + 'stop' + Colors.end + ']'
        try:
            stop_server(
                pre,
                s.screen_name,
                s.server_dir,
                s.world_name,
                s.quiet)
        except ServerNotRunningError as e:
            error_and_die(e, quiet=s.quiet)
    # elif args.testing:
    #     print(list_players_as_list(list_players(s)))
    elif args.uptime:
        try:
            raw_uptime = get_uptime_raw(s.server_dir, s.world_name, s.quiet)
            u = get_uptime(raw_uptime)
            uptime_string = get_uptime_string(u)
            pre = Colors.green + '{}'.format(s.world_name)
            sp_prnt('has been up for ' + Colors.yellow_green + uptime_string,
                    pre=pre, quiet=s.quiet)
        except ServerNotRunningError as e:
            error_and_die(e, quiet=s.quiet)
    elif args.web:
        run_webui(s, s.quiet)
    else:
        parser.print_usage()


def parse_args():
    # TODO: get actual level seed
    # ensure dependencies are here
    try:
        [dependency_check(get_exe_path(p)) for p in DEP_PKGS]

    except MissingExeError as e:
        error_and_die(e)

    # process cli args and do our stuff
    args = sys.argv[1:]
    setup_args(args)
