                % rebase('base.tpl', title='Home')
                <div class="center">
                    <h1>Welcome to the <span class="text-muted">sweetpotato WebUI</span>!</h1>
                    % if server_running:
                    <h2>World "{{settings.world_name}}" is running with PID {{pid}}</h2>
                    % else:
                    <h2>World "{{settings.world_name}}" is not presently running.</h2>
                    % end
                </div>