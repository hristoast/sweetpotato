                % rebase('base.tpl', title='Backup')
<div class="center">
                    <h1><span class="fa fa-file-archive-o"></span> Backup</h1>
                    % if request_method == 'POST':
                    <h1>Backup Started!</h1>
                    % else:
                    % if todays_file in backup_dir_contents:
                    <h2>"{{world_name}}" has been backed up today. Great Job!</h2>
                    % else:
                    <form action="/backup" method="post">
                        <button class="btn btn-lg btn-primary srvctl">Online Backup {{world_name}} now</button>
                    </form>
                    <form action="/backup" method="post">
                        <button class="btn btn-lg btn-warning srvctl">Offline Backup {{world_name}} now</button>
                    </form>
                    % end
                    % if backup_dir_contents:
                    <h3>Click any of the below filenames to download them</h3>
                    <ul>
                    % end
                    % for backup in backup_dir_contents:
                    <li class="bold"><a class="bakfile" href="/backups/{{backup}}">{{backup}}</a></li>
                    % end
                    % end
                    </ul>
                </div>