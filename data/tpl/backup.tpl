                % rebase('base.tpl', title='Backup')
                <div class="center">
                    <h1>Backup</h1>
                    % if request_method == 'POST':
                    <h1>Backup Started!</h1>
                    % else:
                    % if todays_file in backup_dir_contents:
                    <h2>"{{world_name}}" has been backed up today. Great Job!</h2>
                    % else:
                    <form action="/backup" method="post">
                        <button class="btn btn-lg btn-success">Backup {{world_name}} now</button>
                    </form>
                    % end
                    % if backup_dir_contents:
                    <h3>Click any of the below filenames to download them</h3>
                    % end
                    % for backup in backup_dir_contents:
                    <p class="bold"><a href="/backups/{{backup}}">{{backup}}</a></p>
                    % end
                    % end
                </div>