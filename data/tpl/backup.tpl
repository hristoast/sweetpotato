                % rebase('base.tpl', title='Backup')
<div class="center">
                    <h1><span class="fa fa-file-archive-o"></span> Backup</h1>
                    % if request_method == 'POST':
                        % if not todays_file in backup_dir_contents or force:
                            % if offline:
                                % if server_running:
                    <h1><span class="fa fa-spin fa-spinner"></span> "{{world_name}}" is going down for an offline backup now!</h1>
                    <h2>It will be restarted when the backup is complete.</h2>
                                % else:
                    <h1><span class="fa fa-spin fa-spinner"></span> "{{world_name}}" is backing up now!</h1>
                                % end
                            % else:
                    <h1><span class="fa fa-spin fa-spinner"></span> Running a live backup on "{{world_name}}" now!</h1>
                            % end
                            % if world_only:
                    <h4>A 'world-only' backup is being performed ...</h4>
                            % end
                        % else:
                    <h2>You've already made a backup today. Great Job!</h2>
                    <h4>Please use the 'force' option if you really want to overwrite it.</h4>
                        % end
                    % else:
                        % if todays_file in backup_dir_contents:
                    <h2>"{{world_name}}" has been backed up today. Great Job!</h2>
                        % end
                    <form action="/backup" method="post">
                        % if server_running:
                        <div>
                            <button class="btn btn-lg btn-primary srvctl" type="submit"><span class="fa fa-upload"></span> Online Backup {{world_name}} now</button>
                        </div>
                        % end
                        <div>
                            <button class="btn btn-lg btn-warning srvctl" name="offline" type="submit"><span class="fa fa-download"></span> Offline Backup {{world_name}} now</button>
                        </div>
                        <div class="container">
                            <div class=" row">
                                <div class="col-sm-3"></div>
                                <div class="col-sm-2" style="padding-left: 65px;">
                                    <h3 class="center">Force?</h3>
                        % if force:
                                    <input name="force" id="force" type="checkbox" checked="checked">
                        % else:
                                    <input name="force" id="force" type="checkbox">
                        % end
                                </div>
                                <div class="col-sm-3">
                                    <h3>World Only?</h3>
                        % if world_only:
                                    <input name="world-only" id="world-only" type="checkbox" checked="checked">
                        % else:
                                    <input name="world-only" id="world-only" type="checkbox">
                        % end
                                </div>
                            </div>
                        </div>
                    </form>
                        % if backup_dir_contents:
                    <h3>Click any of the below filenames to download them</h3>
                    <div id="backup_files" class="well">
                        <dl class="dl-horizontal">
                            % for file_dict in backup_file_list:
                                % file_bit = file_dict['bit']
                                % file_name = file_dict['file']
                                % file_size = file_dict['size']
                            <dt><a href="/backups/{{file_name}}" title="{{file_name}}">{{file_name}}</a></dt>
                            <dd>Size: <span class="bold">{{file_size}} {{file_bit}}</span></dd>
                            % end
                        </dl>
                    </div>
                        % else:
                    <h3>No backups yet!</h3>
                        % end
                    % end
                </div>
