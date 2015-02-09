import os

AUTHOR_EMAIL = 'me@hristos.triantafillou.us'
AUTHOR_NAME = 'Hristos N. Triantafillou'
AUTHOR = '{0} <{1}>'.format(AUTHOR_EMAIL, AUTHOR_NAME)
LICENSE = 'GPLv3'
MCVERSION = '1.8.1'
PROGNAME = 'sweetpotato'
VERSION = '0.34.19b'


BASE_DIR = os.path.dirname(os.path.realpath(__file__))
DEFAULT_COMPRESSION = 'gz'
COMPRESSION_CHOICES = ['bz2', DEFAULT_COMPRESSION, 'xz']
DAEMON_PY3K_ERROR = 'python-daemon-3K is not installed!'
DEFAULT_PERMGEN = '256'
DEFAULT_SCREEN_NAME = 'SweetpotatoWorld'
DEFAULT_SERVER_PORT = '25565'
DEFAULT_WEBUI_PORT = 8080
DEFAULT_WORLD_NAME = DEFAULT_SCREEN_NAME
DESCRIPTION = "Manage your Minecraft server on a GNU/Linux system."
EGG_DIR = BASE_DIR.rstrip('/sweetpotato')
HOME_DIR = os.getenv('HOME')
CONFIG_DIR = '{0}/.config/{1}'.format(HOME_DIR, PROGNAME)
DEFAULT_CONF_FILE = '{0}/{1}.conf'.format(CONFIG_DIR, PROGNAME)
DEFAULT_LOG_DIR = os.path.join(CONFIG_DIR, 'logs')
DEFAULT_PIDFILE = os.path.join(CONFIG_DIR, 'run', 'sweetpotato.pid')  # TODO: ensure run exists
DEFAULT_PIDFILE_TIMEOUT = 1
README_MD = os.path.join(EGG_DIR, 'README.md')
REQUIRED = 'backup_dir mem_format mem_max mem_min port screen_name server_dir world_name'
SERVER_WAIT_TIME = 0.5
FORGE_DL_URL = 'http://files.minecraftforge.net/maven/net/minecraftforge/forge/{0}/{1}'
FORGE_JAR_NAME = 'forge-{}-universal.jar'
VANILLA_DL_URL = 'https://s3.amazonaws.com/Minecraft.Download/versions/{0}/{1}'
VANILLA_JAR_NAME = 'minecraft_server.{}.jar'
WEB_STATIC = os.path.join(EGG_DIR, 'data/static')
WEB_TPL = os.path.join(EGG_DIR, 'data/tpl')


class Colors:
    blue = '\033[34m'
    light_blue = '\033[94m'
    yellow_green = '\033[92m'
    green = '\033[32m'
    light_red = '\033[91m'
    red = '\033[31m'
    yellow = '\033[33m'
    end = '\033[0m'
