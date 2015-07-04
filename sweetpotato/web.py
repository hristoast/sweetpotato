try:
    import bottle
except ImportError:
    bottle = None
import os
import sys

from collections import OrderedDict
from datetime import datetime
try:
    from markdown import markdown
except ImportError:
    markdown = None
from threading import Thread
from .common import PROGNAME, README_MD, WEB_STATIC, WEB_TPL, VERSION, Colors
from .core import reread_settings, run_server_backup
from .error import ServerNotRunningError
from .server import (get_uptime, get_uptime_raw, get_uptime_string,
                     is_server_running, list_players, list_players_as_list,
                     restart_server, start_server, stop_server)
from .system import die_silently, error_and_die


def run_webui(settings, quiet):
    """
    Run the WebUI or print a message about why not.

    @param settings:
    @return:
    """
    # TODO: decorator for DRY view context
    # TODO: POST routes for control functions
    if bottle:
        app = bottle.app()

        bottle.debug(True)
        bottle.TEMPLATE_PATH.insert(0, WEB_TPL)

        if markdown:
            def readme_md_to_html(md_file):
                """
                Runs markdown() on a markdown-formatted README.md file to
                generate html.

                @param md_file:
                @return:
                """
                html = "% rebase('base.tpl', title='README.md')\n"
                m = open(md_file, 'r')
                for l in m.readlines():
                    html += markdown(l)
                m.close()
                return html

            @bottle.route('/readme')
            def readme():
                path = bottle.request.path
                html = readme_md_to_html(README_MD)
                return bottle.template(
                    html,
                    path=path,
                    __version__=VERSION)
        else:
            @bottle.route('/readme')
            @bottle.view('readme_no_md')
            def readme():
                path = bottle.request.path
                return {'path': path, '__version__': VERSION}

        @bottle.get('/backup')
        @bottle.post('/backup')
        @bottle.view('backup')
        def backups():
            s = reread_settings(settings)
            offline = None
            is_running = is_server_running(s.server_dir)
            path = bottle.request.path
            request_method = bottle.request.method
            todays_file = '{0}_{1}.tar.{2}'.format(
                datetime.now().strftime('%Y-%m-%d'),
                s.world_name,
                s.compression)
            if s.world_only:
                world_only = True
            else:
                world_only = None

            backup_dir_contents = os.listdir(s.backup_dir)
            unsorted_backup_file_list = []
            for backup_file in backup_dir_contents:
                full_path_to_backup_file = os.path.join(s.backup_dir,
                                                        backup_file)
                raw_backup_file_size = os.path.getsize(
                    full_path_to_backup_file)
                if os.path.isfile(full_path_to_backup_file):
                    backup_file_size = raw_backup_file_size / 1000000
                    dc = len(str(backup_file_size).split('.')[-1])
                    dc_diff = dc - 2
                    try:
                        trimmed_size = float(str(backup_file_size)[0:-dc_diff])
                    except ValueError:
                        trimmed_size = backup_file_size
                    unsorted_backup_file_list.append({
                        'bit': 'MB',
                        'file': backup_file,
                        'size': trimmed_size})
            backup_file_list = sorted(unsorted_backup_file_list,
                                      key=lambda k: k['size'], reverse=True)

            if bottle.request.method == 'POST':
                postdata = bottle.request.POST
                force = 'force' in postdata or 'force-offline' in postdata
                offline = 'offline' in postdata or 'force-offline' in postdata
                world_only = postdata['world-only'] == 'on' or world_only
                t = Thread(
                    target=run_server_backup,
                    args=('', s, True, is_running, world_only),
                    kwargs={'offline': offline,
                            'force': force})
                t.daemon = True
                t.start()

            return {
                'backup_dir_contents': backup_dir_contents,
                'backup_file_list': backup_file_list,
                'offline': offline,
                'path': path,
                'request_method': request_method,
                'server_running': is_running,
                'todays_file': todays_file,
                'world_name': s.world_name,
                'world_only': world_only,
                '__version__': VERSION}

        @bottle.route('/')
        @bottle.view('index')
        def index():
            s = reread_settings(settings)
            is_running = is_server_running(s.server_dir)
            path = bottle.request.path
            pid = None
            players = None
            if s.world_only:
                world_only = True
            else:
                world_only = False
            try:
                raw = get_uptime_raw(s.server_dir, s.world_name, False)
                u = get_uptime(raw)
                uptime = get_uptime_string(u)
                if is_running:
                    pid = is_running.get('pid')
                    players = list_players_as_list(list_players(s))
            except ServerNotRunningError:
                uptime = None
            try:
                # we don't care about these daemon details
                s.__dict__.pop('pidfile_path')
                s.__dict__.pop('pidfile_timeout')
                s.__dict__.pop('stderr_path')
                s.__dict__.pop('stdin_path')
                s.__dict__.pop('stdout_path')
            except KeyError:
                pass
            sorted_settings = OrderedDict(sorted(s.__dict__.items()))

            return {
                'path': path,
                'pid': pid,
                'players': players,
                'server_running': is_running,
                'sorted_settings': sorted_settings,
                'uptime': uptime,
                'world_name': s.world_name,
                'world_only': world_only,
                '__version__': VERSION}

        @bottle.route('/json')
        def as_json():
            bottle.response.content_type = 'application/json'
            s = reread_settings(settings)
            s.running = is_server_running(s.server_dir)
            return s.as_json

        @bottle.get('/server')
        @bottle.post('/server')
        @bottle.view('server')
        def server():
            s = reread_settings(settings)
            is_running = is_server_running(s.server_dir)
            path = bottle.request.path
            request_method = bottle.request.method
            restart = None
            start = None
            stop = None
            if bottle.request.method == 'POST':
                postdata = bottle.request.POST
                restart = postdata.get('restart')
                start = postdata.get('start')
                stop = postdata.get('stop')
                if restart is not None:
                    t = Thread(target=restart_server, args=('', s, True))
                    t.daemon = True
                    t.start()
                elif start is not None:
                    t = Thread(target=start_server, args=('', s, True))
                    t.daemon = True
                    t.start()
                elif stop is not None:
                    t = Thread(target=stop_server,
                               args=('', s.screen_name,
                                     s.server_dir, s.world_name, True))
                    t.daemon = True
                    t.start()
            return {
                'path': path,
                'request_method': request_method,
                'restart': restart,
                'start': start,
                'stop': stop,
                'server_running': is_running,
                'world_name': s.world_name,
                '__version__': VERSION}

        @bottle.route('/backups/<file_path:path>')
        def serve_backup(file_path):
            s = reread_settings(settings)
            return bottle.static_file(file_path, root=s.backup_dir)

        @bottle.route('/static/<file_path:path>')
        def serve_static(file_path):
            return bottle.static_file(file_path, root=WEB_STATIC)

        @bottle.error(404)
        @bottle.view('404')
        def error404(error):
            path = bottle.request.path
            return {
                'error': error,
                'path': path,
                '__version__': VERSION}

        @bottle.error(500)
        @bottle.view('500')
        def error500(error):
            path = bottle.request.path
            return {
                'error': error,
                'path': path,
                '__version__': VERSION}
        try:
            if not quiet:
                print(Colors.green + '{0} {1} - launching WebUI now!'.format(
                    PROGNAME, VERSION))
                sys.stdout.flush()
            bottle.run(app=app, port=settings.webui_port, quiet=quiet)
        except OSError:
            if not quiet:
                error_and_die(
                    'Port {} is already in use! Exiting ...\n'.format(
                        settings.webui_port))
            else:
                die_silently()
    elif not quiet:
        error_and_die('The web component requires both bottle.py to function, '
                      'with Python-Markdown as an optional dependency.')
    else:
        die_silently()
