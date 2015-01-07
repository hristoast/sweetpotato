#!/usr/bin/env python3
# TODO: test start, stop, restart, webui, ????
# TODO: run when already running
# TODO: stop when already stopped
# TODO: webui when already webui-ing
import unittest
import sweetpotato


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


class SweetpotatoTests(unittest.TestCase):

    def setUp(self):
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
        config = sweetpotato.SweetpotatoConfig()
        config.backup_dir = TEST_BACKUP_DIR
        config.mem_format = TEST_MEM_FORMAT
        config.mem_max = TEST_MEM_MAX
        config.mem_min = TEST_MEM_MIN
        config.server_dir = TEST_SERVER_DIR
        self.assertIn(TEST_SERVER_DIR, config.as_conf_file)

    def test_as_serverproperties(self):
        config = sweetpotato.SweetpotatoConfig()
        config.backup_dir = TEST_BACKUP_DIR
        config.mem_format = TEST_MEM_FORMAT
        config.mem_max = TEST_MEM_MAX
        config.mem_min = TEST_MEM_MIN
        config.server_dir = TEST_SERVER_DIR
        server_properties = """generator-settings=
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
        self.assertEqual(config.as_serverproperties, server_properties)

    def test_json(self):  # TODO: test if forge and if not forge
        config = sweetpotato.SweetpotatoConfig()
        config.backup_dir = TEST_BACKUP_DIR
        config.mem_format = TEST_MEM_FORMAT
        config.mem_max = TEST_MEM_MAX
        config.mem_min = TEST_MEM_MIN
        config.server_dir = TEST_SERVER_DIR
        json = """{
    "backup_dir": "/tmp/_sp_test_backup",
    "compression": "gz",
    "conf_file": null,
    "forge": null,
    "level_seed": null,
    "mc_version": "1.8.1",
    "mem_format": "MB",
    "mem_max": "1024",
    "mem_min": "512",
    "permgen": null,
    "port": "25565",
    "running": false,
    "screen_name": "SweetpotatoWorld",
    "server_dir": "/tmp/_sp_test_server",
    "webui_port": 8080,
    "world_name": "SweetpotatoWorld"
}"""
        self.assertEqual(config.as_json, json)

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
