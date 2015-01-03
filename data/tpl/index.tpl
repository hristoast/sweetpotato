                % rebase('base.tpl', title=settings.world_name)
<div class="center">
                    <h1>Welcome to the <span class="text-muted">sweetpotato WebUI</span>!</h1>
                    % if server_running:
                    <h2>World "{{settings.world_name}}" is running with PID {{pid}}</h2>
                    % else:
                    <h2>World "{{settings.world_name}}" is not presently running.</h2>
                    % end
                    <div id="server_stats" class="well">
                    <h2 class="center"><span class="fa fa-cogs"></span> Loaded Settings</h2>
                        <div class="divider"></div>
                            <dl class="dl-horizontal">
                                % for k, v in settings.__dict__.items():
                                % if v is not None:
                                % if v is not False:
                                % if k is not 'running':
                                <dt>{{k}}:</dt>
                                <dd>{{v}}</dd>
                                % end
                                % end
                                % end
                                % end
                            </dl>
                    </div>
                </div>