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
VERSION = '2.0'


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
# RELEASE = False
SERVER_WAIT_TIME = 1
# SHA = None
FORGE_DL_URL = 'http://files.minecraftforge.net/maven/net/minecraftforge/forge/{0}/{1}'
FORGE_JAR_NAME = 'forge-{}-universal.jar'
VANILLA_DL_URL = 'https://s3.amazonaws.com/Minecraft.Download/versions/{0}/{1}'
VANILLA_JAR_NAME = 'minecraft_server.{}.jar'

# _colors = collections.namedtuple(
#     'Colors',
#     ['blue', 'light_blue', 'yellow_green', 'green',
#      'light_red', 'red', 'yellow', 'end'])

# Colors = _colors(
#     blue='\033[34m',
#     light_blue='\033[94m',
#     yellow_green='\033[92m',
#     green='\033[32m',
#     light_red='\033[91m',
#     red='\033[31m',
#     yellow='\033[33m',
#     end='\033[0m')


# def get_git_rev():
#     """What branch and SHA are we working on?"""
#     # source_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
#     # print(source_dir)
#     # dot_git = os.path.isdir(os.path.join(source_dir, ".git"))
#     if not RELEASE:
#         # os.chdir(source_dir)
#         # git rev-parse --abbrev-ref HEAD
#         p_branch = subprocess.Popen(["git", "rev-parse", "--abbrev-ref", "HEAD"],
#                                     stderr=subprocess.PIPE, stdout=subprocess.PIPE)
#         branch = p_branch.communicate()[0].decode().split()[0]
#         p_sha = subprocess.Popen(["git", "rev-parse", '--short', "HEAD"],
#                                  stderr=subprocess.PIPE, stdout=subprocess.PIPE)
#         sha = p_sha.communicate()[0].decode().split()[0]
#     else:
#         branch = None
#         sha = None
#     return branch, sha


# def have_symbola():
#     pass


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
