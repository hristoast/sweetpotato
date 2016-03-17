import collections
import os
import subprocess
import sys

AUTHOR_EMAIL = 'me@hristos.triantafillou.us'
AUTHOR_NAME = 'Hristos N. Triantafillou'
AUTHOR = '{0} <{1}>'.format(AUTHOR_NAME, AUTHOR_EMAIL)
LICENSE = 'GPLv3'
MCVERSION = '1.8.9'
PROGNAME = 'sweetpotato'
VERSION = '0.34.34'


BASE_DIR = os.path.dirname(os.path.realpath(__file__))
DEFAULT_COMPRESSION = 'gz'
COMPRESSION_CHOICES = ['bz2', DEFAULT_COMPRESSION, 'xz']
DAEMON_PY3K_ERROR = """python-daemon-3K is not installed! Install it like this:

pip3 install git+https://github.com/hristoast/python-daemon"""
DEFAULT_EXCLUDE_FILES = ['level.dat_new']
DEFAULT_PERMGEN = '256'
DEFAULT_SCREEN_NAME = '{}World'.format(PROGNAME).capitalize()
DEFAULT_SERVER_PORT = '25565'
DEFAULT_WEBUI_PORT = 8080
DEFAULT_WORLD_NAME = DEFAULT_SCREEN_NAME
DESCRIPTION = "Manage your Minecraft server on a GNU/Linux system."
HOME_DIR = os.getenv('HOME')
CONFIG_DIR = '{0}/.config/{1}'.format(HOME_DIR, PROGNAME)
DEFAULT_CONF_FILE = '{0}/{1}.conf'.format(CONFIG_DIR, PROGNAME)
DEFAULT_LOG_DIR = os.path.join(CONFIG_DIR, 'logs')
DEFAULT_LOG_FILE = os.path.join(DEFAULT_LOG_DIR, 'daemon.log')
DEFAULT_PIDFILE = os.path.join(CONFIG_DIR, 'run', '{}.pid'.format(PROGNAME))
DEFAULT_PIDFILE_TIMEOUT = 1
DEP_PKGS = ('java', 'screen')
NO_BOTTLEPY_ERROR = 'The web component requires bottle.py to function, with Python-Markdown as an optional dependency.'
PYTHON33_OR_GREATER = sys.version_info.major >= 3 and sys.version_info.minor >= 3
README_MD = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'README.md')
REQUIRED = 'backup_dir mem_format mem_max mem_min port screen_name server_dir world_name'
SERVER_WAIT_TIME = 1
SYMBOLA_SWEETPOTATO = "🍠"
FORGE_DL_URL = 'http://files.minecraftforge.net/maven/net/minecraftforge/forge/{0}/{1}'
FORGE_JAR_NAME = 'forge-{}-universal.jar'
VANILLA_DL_URL = 'https://s3.amazonaws.com/Minecraft.Download/versions/{0}/{1}'
VANILLA_JAR_NAME = 'minecraft_server.{}.jar'
WEB_STATIC = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'static')
WEB_TPL = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'tpl')

_colors = collections.namedtuple(
    'Colors',
    ['blue', 'light_blue', 'yellow_green', 'green',
     'light_red', 'red', 'yellow', 'end'])

Colors = _colors(
    blue='\033[34m',
    light_blue='\033[94m',
    yellow_green='\033[92m',
    green='\033[32m',
    light_red='\033[91m',
    red='\033[31m',
    yellow='\033[33m',
    end='\033[0m')


def get_git_rev():
    """What SHA is this??"""
    source_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
    dot_git = os.path.isdir(os.path.join(source_dir, ".git"))
    if dot_git:
        os.chdir(source_dir)
        p = subprocess.Popen(["git", "rev-list", "HEAD"],
                             stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        sha = p.communicate()[0].decode().split()[0]
    else:
        sha = None
    return sha


def have_symbola():
    pass


def sp_prnt(*args, color=Colors.light_blue, end_color=Colors.end,
            pre=None, quiet=False, sweetpotato=False, **kwargs):
    """
    If quiet is Truthy, then don't do anything.

    Otherwise, do the special printing stuff.
    """
    if not quiet:
        msg = color
        if sweetpotato:
            msg += SYMBOLA_SWEETPOTATO + ' '
        if args:
            for arg in args:
                msg += arg
        if end_color:
            msg += end_color
        if pre:
            msg = pre + msg
        print(msg, **kwargs)
        sys.stdout.flush()
