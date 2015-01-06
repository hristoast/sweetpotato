#!/usr/bin/env python3
# TODO: test start, stop, restart, webui, ????
# TODO: run when already running
# TODO: stop when already stopped
# TODO: webui when already webui-ing
import unittest
import sweetpotato


TEST_SERVER_DIR = '/tmp/_sp_test_server'
TEST_SERVER_DIR2 = '/tmp/_sp_test_server2'
TEST_WORLD_NAME = 'TestWorld'
TEST_WORLD_NAME2 = 'TestWorld2'
TEST_CONF = """
[Settings]
world_name: {0}
mem_max: 1024
mem_min: 512
backup_dir: /tmp/_sp_test_backup
mem_format: MB
server_dir: {1}
""".format(TEST_WORLD_NAME, TEST_SERVER_DIR)
TEST_CONF_FILE = '/tmp/_sp_test.conf'
TEST_CONF_FILE2 = '/tmp/_sp_test.conf2'


class SweetpotatoTests(unittest.TestCase):

    def setUp(self):
        with open(TEST_CONF_FILE, 'w') as c:
            for l in TEST_CONF.strip().splitlines():
                c.write(l)
                c.write('\n')
            c.close()

        sweetpotato.arg_parse([
            '--conf', '{}'.format(TEST_CONF_FILE),
            '--create',
            '--quiet'
        ])

    def test_stop_when_server_not_running(self):
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
