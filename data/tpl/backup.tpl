                % rebase('base.tpl', title='Backup')
<div class="center">
                    <h1><span class="fa fa-file-archive-o"></span> Backup</h1>
                    % if request_method == 'POST':
                    % if offline:
                    % if server_running:
                    <h1><span class="fa fa-spin fa-spinner"></span> "{{world_name}}" is going down for an offline backup now!</h1>
                    <h2>It will be restarted when the backup is complete.</h2>
                    % else:
                    <h1><span class="fa fa-spin fa-spinner"></span> "{{world_name}}" is backup up now!</h1>
                    <h2>It will be started when the backup is complete.</h2>
                    % end
                    % else:
                    <h1><span class="fa fa-spin fa-spinner"></span> Running a live backup on "{{world_name}}" now!</h1>
                    % end
                    % else:
                    % if todays_file in backup_dir_contents:
                    <h2>"{{world_name}}" has been backed up today. Great Job!</h2>
                    % else:
                    % if server_running:
                    <form action="/backup" method="post">
                        <button class="btn btn-lg btn-primary srvctl"><span class="fa fa-upload"></span> Online Backup {{world_name}} now</button>
                    </form>
                    % end
                    <form action="/backup" method="post">
                        <button class="btn btn-lg btn-warning srvctl" name="offline" type="submit"><span class="fa fa-download"></span> Offline Backup {{world_name}} now</button>
                    </form>
                    % end
                    % if backup_dir_contents:
                    <h3>Click any of the below filenames to download them</h3>
                    % end
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
                    % end
                </div>