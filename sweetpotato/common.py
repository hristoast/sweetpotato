# import collections
import logging
import os
import sys

AUTHOR_EMAIL = 'sweetpotato@bhgdo.com'
AUTHOR_NAME = 'Hristos N. Triantafillou'
AUTHOR = '{0} <{1}>'.format(AUTHOR_NAME, AUTHOR_EMAIL)
LICENSE = 'GPLv3'
MCVERSION = '1.10.2'
FORGEVERSION = MCVERSION + "-12.18.3.2185"
PROGNAME = 'sweetpotato'
VERSION = '2.1'


LOGFMT = "[%(levelname)s] %(message)s"
BASE_DIR = os.path.dirname(os.path.realpath(__file__))
DEFAULT_COMPRESSION = 'gz'
COMPRESSION_CHOICES = ['bz2', DEFAULT_COMPRESSION, 'xz']
DEFAULT_EXCLUDE_FILES = 'level.dat_new'
DEFAULT_SCREEN_NAME = '{}World'.format(PROGNAME).capitalize()
DEFAULT_SERVER_PORT = '25565'
DEFAULT_WORLD_NAME = DEFAULT_SCREEN_NAME
DESCRIPTION = "Manage your Minecraft server on a GNU/Linux system."
HOME_DIR = os.getenv('HOME')
CONFIG_DIR = '{0}/.config/{1}'.format(HOME_DIR, PROGNAME)
DEFAULT_CONF_FILE = '{0}/{1}.conf'.format(CONFIG_DIR, PROGNAME)
PYTHON33_OR_GREATER = sys.version_info.major >= 3 and sys.version_info.minor >= 3
SERVER_WAIT_TIME = 1
FORGE_DL_URL = 'http://files.minecraftforge.net/maven/net/minecraftforge/forge/{0}/{1}'
FORGE_JAR_NAME = 'forge-{}-universal.jar'
VANILLA_DL_URL = 'https://s3.amazonaws.com/Minecraft.Download/versions/{0}/{1}'
VANILLA_JAR_NAME = 'minecraft_server.{}.jar'


def emit_msg(msg: str, level=logging.INFO, quiet=False, *args, **kwargs) -> None:
    """Logging wrapper."""
    if not quiet:
        if level == logging.DEBUG:
            logging.debug(msg, *args, **kwargs)
        elif level == logging.INFO:
            logging.info(msg, *args, **kwargs)
        elif level == logging.WARN:
            logging.warn(msg, *args, **kwargs)
        elif level == logging.ERROR:
            logging.error(msg, *args, **kwargs)
