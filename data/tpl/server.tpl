                % rebase('base.tpl', title='Server Control')
<div class="center">
                    <h1><span class="fa fa-cog"></span> Server Control</h1>
                % if request_method == 'POST':
                % if restart is not None:
                    <h3>"{{world_name}}" has been restarted!</h3>
                % elif start is not None:
                    <h3>"{{world_name}}" has been started!</h3>
                % elif stop is not None:
                    <h3>"{{world_name}}" has been stopped!</h3>
                % end
                % else:
                % if not server_running:
                    <form action="/server" method="post">
                        <button class="btn btn-lg btn-success srvctl" name="start" type="submit"><span class="fa fa-level-up"></span> Start {{world_name}}</button>
                    </form>
                % else:
                    <form action="/server" method="post">
                        <button class="btn btn-lg btn-danger srvctl" name="stop" type="submit"><span class="fa fa-power-off"></span> Stop {{world_name}}</button>
                    </form>
                    <form action="/server" method="post">
                        <button class="btn btn-lg btn-warning srvctl" name="restart" type="submit"><span class="fa fa-refresh"></span> Restart {{world_name}}</button>
                    </form>
                % end
                % end
                </div>