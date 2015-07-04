#!/usr/bin/env python3
# TODO: test start, stop, restart, webui, ????
# TODO: run when already running
# TODO: stop when already stopped
# TODO: webui when already webui-ing
# import json
import os
import unittest
# import urllib.request

from sweetpotato.cli import setup_args
from sweetpotato.common import MCVERSION
from sweetpotato.core import SweetpotatoConfig
from sweetpotato.error import MissingExeError
from sweetpotato.java import get_jar
from sweetpotato.system import dependency_check, get_exe_path


BASE_DIR = os.path.dirname(os.path.realpath(__file__))
TEST_BACKUP_DIR = '/tmp/_sp_test_backup'
TEST_CONF_FILE = '/tmp/_sp_test.conf'
TEST_CONF_FILE2 = '/tmp/_sp_test.conf2'
TEST_MEM_FORMAT = 'MB'
TEST_MEM_MAX = '1024'
TEST_MEM_MIN = '512'
TEST_SERVER_DIR = '/tmp/_sp_test_server'
TEST_SERVER_DIR2 = '/tmp/_sp_test_server2'
TEST_WEBUI_PORT = 8181
TEST_WORLD_NAME = 'TestWorld'
TEST_WORLD_NAME2 = 'TestWorld2'
TEST_CONF = """
[Settings]
world_name: {0}
mem_max: {1}
mem_min: {2}
backup_dir: {3}
mem_format: {4}
server_dir: {5}
webui_port: {6}
""".format(TEST_WORLD_NAME, TEST_MEM_MAX, TEST_MEM_MIN, TEST_BACKUP_DIR,
           TEST_MEM_FORMAT, TEST_SERVER_DIR, TEST_WEBUI_PORT)
TEST_SERVER_PROPERTIES = """generator-settings=
op-permission-level=4
allow-nether=true
resource-pack-hash=
level-name=Sweetpotatoworld
enable-query=false
allow-flight=false
announce-player-achievements=true
server-port=25565
max-world-size=29999984
level-type=DEFAULT
enable-rcon=false
level-seed=
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
motd=Welcome to Sweetpotatoworld!
        """
JSON = """{
    "backup_dir": "/tmp/_sp_test_backup",
    "compression": "gz",
    "conf_file": null,
    "fancy": true,
    "force": false,
    "forge": null,
    "level_seed": null,
    "mc_version": "1.8.7",
    "mem_format": "MB",
    "mem_max": "1024",
    "mem_min": "512",
    "permgen": null,
    "port": "25565",
    "running": false,
    "screen_name": "Sweetpotatoworld",
    "server_dir": "/tmp/_sp_test_server",
    "webui_port": 8181,
    "world_name": "Sweetpotatoworld",
    "world_only": false
}"""


class SweetpotatoTests(unittest.TestCase):

    def setUp(self):
        self.config = SweetpotatoConfig()
        self.config.backup_dir = TEST_BACKUP_DIR
        self.config.mem_format = TEST_MEM_FORMAT
        self.config.mem_max = TEST_MEM_MAX
        self.config.mem_min = TEST_MEM_MIN
        self.config.server_dir = TEST_SERVER_DIR
        self.config.webui_port = TEST_WEBUI_PORT

        # Write the test conf file
        with open(TEST_CONF_FILE, 'w') as c:
            for l in TEST_CONF.strip().splitlines():
                c.write(l)
                c.write('\n')
            c.close()

        # Install a server to test with
        setup_args([
            '--conf', '{}'.format(TEST_CONF_FILE),
            '--create',
            '--quiet'
        ])

    def test_as_conf_file(self):
        self.assertIn(TEST_SERVER_DIR, self.config.as_conf_file)

    def test_json_output_fancy(self):  # TODO: test if forge and if not forge
        self.config.fancy = True
        self_json = self.config.as_json
        self.assertEqual(self_json, JSON)

    # this output is unsorted; hard to test
    # def test_json_output_not_pretty(self):
    #     self.assertEqual(self.config.as_json, JSON_NOT_PRETTY)

    def test_json_type(self):
        self.assertIsInstance(self.config.as_json, str)

    # TODO: doing this wrong ...
    # def test_json_url(self):
        # sweetpotato.arg_parse([
        #     '--conf', '{}'.format(TEST_CONF_FILE),
        #     '--quiet',
        #     '--web'
        # ])
        # t = Thread(target=sweetpotato.run_webui,
        #            args=(self.config, True))
        # t.start()
        # url = 'http://127.0.0.1:8181/json'
        # r = urllib.request.urlopen(url)
        # rs = r.readall().decode('utf-8')
        # r.close()
        # jo = json.loads(rs)
        # print(jo)
        # t._stop()

    def test_as_serverproperties(self):
        self.assertEqual(self.config.as_serverproperties,
                         TEST_SERVER_PROPERTIES)

    def test_agree_to_eula(self):
        eula_txt = os.path.join(TEST_SERVER_DIR, 'eula.txt')
        with open(eula_txt, 'r') as et:
            eula_txt_text = et.readlines()
            et.close()
        agreed = 'eula=true' in eula_txt_text[0]
        self.assertTrue(agreed)

    def test_dependency_check(self):
        check = dependency_check(('nothing', None))
        self.assertRaises(MissingExeError, check)

    @unittest.expectedFailure
    def test_get_fake_exe_path(self):
        fake = get_exe_path('FartBomb.EXE')
        self.assertTrue(fake)

    def test_get_real_exe_path(self):
        ls = get_exe_path('ls')
        self.assertEqual(ls, '/bin/ls')

    def test_get_jar(self):
        jar = get_jar(self.config)[0]
        self.assertEqual(jar, 'minecraft_server.{}.jar'.format(MCVERSION))

    # TODO: test listing (will be None)

    # def test_minimal_install(self):
    #     sweetpotato_py_file = SWEETPOTATO_PY.split(os.path.sep)[-1]
    #     init = open('/tmp/__init__.py', 'a')
    #     init.write('\n')
    #     init.close()
    #     temp_sweetpotato_py_file = os.path.join('/tmp/', sweetpotato_py_file)
    #     try:
    #         copy(SWEETPOTATO_PY, temp_sweetpotato_py_file)
    #     except SameFileError:
    #         pass
    #     os.chdir('/tmp')

        # command = './{0} -c {1} -q -W'.format(SCRIPT_NAME, TEST_CONF_FILE)

        # self.assertRaises(
        #     SystemExit,
        #     p=subprocess.Popen(command.split())
        # )

    def test_stop_when_stopped(self):
        self.assertRaises(
            SystemExit,
            setup_args, (
                '--conf', '{}'.format(TEST_CONF_FILE),
                '--quiet',
                '--stop'
            ))

    def test_uptime_when_server_not_running(self):
        self.assertRaises(
            SystemExit,
            setup_args, (
                '--conf', '{}'.format(TEST_CONF_FILE),
                '--quiet',
                '--uptime'
            ))


if __name__ == '__main__':
    unittest.main()
