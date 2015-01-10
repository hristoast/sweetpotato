#!/usr/bin/env python3
# TODO: test start, stop, restart, webui, ????
# TODO: run when already running
# TODO: stop when already stopped
# TODO: webui when already webui-ing
import os
import pty
import unittest
import shlex
import subprocess
import sweetpotato

from shutil import SameFileError, copy


BASE_DIR = os.path.dirname(os.path.realpath(__file__))
SCRIPT_NAME = 'sweetpotato.py'
SWEETPOTATO_PY = os.path.join(BASE_DIR, SCRIPT_NAME)
TEST_BACKUP_DIR = '/tmp/_sp_test_backup'
TEST_CONF_FILE = '/tmp/_sp_test.conf'
TEST_CONF_FILE2 = '/tmp/_sp_test.conf2'
TEST_MEM_FORMAT = 'MB'
TEST_MEM_MAX = '1024'
TEST_MEM_MIN = '512'
TEST_SERVER_DIR = '/tmp/_sp_test_server'
TEST_SERVER_DIR2 = '/tmp/_sp_test_server2'
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
""".format(TEST_WORLD_NAME, TEST_MEM_MAX, TEST_MEM_MIN,
           TEST_BACKUP_DIR, TEST_MEM_FORMAT, TEST_SERVER_DIR)
TEST_SERVER_PROPERTIES = """generator-settings=
op-permission-level=4
allow-nether=true
resource-pack-hash=
level-name=SweetpotatoWorld
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
motd=Welcome to SweetpotatoWorld!
        """
JSON = """{
    "backup_dir": "/tmp/_sp_test_backup",
    "compression": "gz",
    "conf_file": null,
    "level_seed": null,
    "mc_version": "1.8.1",
    "mem_format": "MB",
    "mem_max": "1024",
    "mem_min": "512",
    "port": "25565",
    "running": false,
    "screen_name": "SweetpotatoWorld",
    "server_dir": "/tmp/_sp_test_server",
    "webui_port": 8080,
    "world_name": "SweetpotatoWorld"
}"""


class SweetpotatoTests(unittest.TestCase):

    def setUp(self):
        self.config = sweetpotato.SweetpotatoConfig()
        self.config.backup_dir = TEST_BACKUP_DIR
        self.config.mem_format = TEST_MEM_FORMAT
        self.config.mem_max = TEST_MEM_MAX
        self.config.mem_min = TEST_MEM_MIN
        self.config.server_dir = TEST_SERVER_DIR

        # Write the test conf file
        with open(TEST_CONF_FILE, 'w') as c:
            for l in TEST_CONF.strip().splitlines():
                c.write(l)
                c.write('\n')
            c.close()

        # Install a server to test with
        sweetpotato.arg_parse([
            '--conf', '{}'.format(TEST_CONF_FILE),
            '--create',
            '--quiet'
        ])

    def test_as_conf_file(self):
        self.assertIn(TEST_SERVER_DIR, self.config.as_conf_file)

    def test_json(self):  # TODO: test if forge and if not forge
        self.assertEqual(self.config.as_json, JSON)

    def test_as_serverproperties(self):
        self.assertEqual(self.config.as_serverproperties, TEST_SERVER_PROPERTIES)

    def test_agree_to_eula(self):
        eula_txt = os.path.join(TEST_SERVER_DIR, 'eula.txt')
        with open(eula_txt, 'r') as et:
            eula_txt_text = et.readlines()
            et.close()
        agreed = 'eula=true' in eula_txt_text[0]
        self.assertTrue(agreed)

    def test_dependency_check(self):
        check = sweetpotato.dependency_check(('nothing', None))
        self.assertRaises(sweetpotato.MissingExeError, check)

    @unittest.expectedFailure
    def test_get_fake_exe_path(self):
        fake = sweetpotato.get_exe_path('FartBomb.EXE')
        self.assertTrue(fake)

    def test_get_real_exe_path(self):
        ls = sweetpotato.get_exe_path('ls')
        self.assertEqual(ls, '/bin/ls')

    def test_get_jar(self):
        jar = sweetpotato.get_jar(self.config)[0]
        self.assertEqual(jar, 'minecraft_server.{}.jar'.format(sweetpotato.__mcversion__))

    def test_minimal_install(self):
        sweetpotato_py_file = SWEETPOTATO_PY.split(os.path.sep)[-1]
        init = open('/tmp/__init__.py', 'a')
        init.write('\n')
        init.close()
        temp_sweetpotato_py_file = os.path.join('/tmp/', sweetpotato_py_file)
        try:
            copy(SWEETPOTATO_PY, temp_sweetpotato_py_file)
        except SameFileError:
            pass
        os.chdir('/tmp')

        command = './{0} -c {1} -q -W'.format(SCRIPT_NAME, TEST_CONF_FILE)

        self.assertRaises(
            SystemExit,
            p=subprocess.Popen(command.split())
        )

    def test_stop_when_stopped(self):
        self.assertRaises(
            SystemExit,
            sweetpotato.arg_parse, (
                '--conf', '{}'.format(TEST_CONF_FILE),
                '--quiet',
                '--stop'
            ))

    def test_uptime_when_server_not_running(self):
        self.assertRaises(
            SystemExit,
            sweetpotato.arg_parse, (
                '--conf', '{}'.format(TEST_CONF_FILE),
                '--quiet',
                '--uptime'
            ))


if __name__ == '__main__':
    unittest.main()
