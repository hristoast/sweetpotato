                % rebase('base.tpl', title='Backups')
                <div class="center">
                    <h1>Backups</h1>
                    % if todays_file in backup_dir_contents:
                    <h2>"{{world_name}}" has been backed up today. Great Job!</h2>
                    % else:
                    <button class="btn btn-lg btn-success">Backup Now Button Goes Here</button>
                    % end
                    % for backup in backup_dir_contents:
                    <p class="bold">{{backup}}</p>
                    % end
                </div>