                % rebase('base.tpl', title='Home')
<div class="center">
                    <h1>Welcome to the <span class="text-muted">sweetpotato WebUI</span>!</h1>
                    % if server_running:
                    <h2>World "{{settings.world_name}}" is running with PID {{pid}}</h2>
                    % else:
                    <h2>World "{{settings.world_name}}" is not presently running.</h2>
                    % end
                    <div id="server_stats" class="well">
                    <h2 class="center">Loaded Settings</h2>
                        <div class="divider"></div>
                        % for k, v in settings.__dict__.items():
                        % if v is not None:
                        % if v is not False:
                        % if k is not 'running':
                        <p class="bold setting_values"><span style="float:left;">{{k}}</span>: <span style="float: right">{{v}}</span></p>
                        <div class="divider"></div>
                        % end
                        % end
                        % end
                        % end
                    </div>
                </div>