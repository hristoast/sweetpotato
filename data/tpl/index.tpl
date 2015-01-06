                % rebase('base.tpl', title=world_name)
<div class="center">
                    <h1>Welcome to the <span class="text-muted">sweetpotato WebUI</span>!</h1>
                    % if server_running:
                    <h2>World "{{world_name}}" is running with PID {{pid}}</h2>
                    <h3>Uptime: <span class="bold">{{uptime}}</span></h3>
                    % else:
                    <h2>World "{{world_name}}" is not presently running.</h2>
                    % end
                    <div id="server_stats" class="well">
                        <h2 class="center"><span class="fa fa-cogs"></span> Loaded Settings</h2>
                        <div class="divider"></div>
                        <dl class="dl-horizontal">
                            % for k, v in sorted_settings.items():
                            % if v is not None:
                            % if v is not False:
                            % if k is not 'running':
                            % if k is 'backup_dir':
                            <dt>Backup Directory:</dt>
                            % elif k is 'compression':
                            <dt>Compression Type:</dt>
                            % elif k is 'conf_file':
                            <dt>Conf File:</dt>
                            % elif k is 'forge':
                            <dt>Forge Version:</dt>
                            % elif k is 'mc_version':
                            <dt>Minecraft Version:</dt>
                            % elif k is 'mem_format':
                            <dt>Memory Format:</dt>
                            % elif k is 'mem_max':
                            <dt>Max Server Memory:</dt>
                            % elif k is 'mem_min':
                            <dt>Min Server Memory:</dt>
                            % elif k is 'permgen':
                            <dt>Permgen:</dt>
                            % elif k is 'port':
                            <dt>Server Port:</dt>
                            % elif k is 'screen_name':
                            <dt>Screen Session Name:</dt>
                            % elif k is 'server_dir':
                            <dt>Server Directory:</dt>
                            % elif k is 'webui_port':
                            <dt>WebUI Port:</dt>
                            % elif k is 'world_name':
                            <dt>World Name:</dt>
                            % else:
                            <dt>{{k}}:</dt>
                            % end
                            <dd>{{v}}</dd>
                            % end
                            % end
                            % end
                            % end
                        </dl>
                    </div>
                </div>