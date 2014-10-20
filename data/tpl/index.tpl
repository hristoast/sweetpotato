                % rebase('base.tpl', title='Home')
                <div class="center">
                    <h1>Welcome to the <span class="text-muted">sweetpotato WebUI</span>!</h1>
                    % if server_running:
                    <h2>World "{{settings.world_name}}" is running with PID {{pid}}</h2>
                    % else:
                    <h2>World "{{settings.world_name}}" is not presently running.</h2>
                    % end
                    <h2>Loaded Settings</h2>
                    <div style="font-size: 1.2em;">
                        % for k, v in settings.__dict__.items():
                        % if v is not None:
                        % if v is not False:
                        % if k is not 'running':
                        <p>{{k}}: {{v}}</p>
                        % end
                        % end
                        % end
                        % end
                    </div>
                </div>