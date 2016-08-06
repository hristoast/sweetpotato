                % rebase('base.tpl', title='Backup')
<div class="center">
                    <h1><span class="fa fa-file-archive-o"></span> Backup</h1>
                    % if request_method == 'POST':
                        % if not todays_file in backup_dir_contents or force:
                    <h1><span class="fa fa-spin fa-spinner"></span> Running a backup on "{{world_name}}" now!</h1>
                            % if world_only:
                    <h4>A 'world-only' backup is being performed ...</h4>
                            % end
                            % if force:
                    <h4>A forced backup is being performed ...</h4>
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
                        <div>
                            <button class="btn btn-lg btn-primary srvctl" type="submit"><span class="fa fa-upload"></span> Backup {{world_name}} now</button>
                        </div>
                        <div class="container" style="max-width: 900px;">
                            <div class="row">
                                <div class="col-sm-4"></div>
                                <div class="col-sm-1" style="padding-left: 25px;">
                                    <h3>Force?</h3>
                        % if force:
                                    <input name="force" id="force" type="checkbox" checked="checked">
                        % else:
                                    <input name="force" id="force" type="checkbox">
                        % end
                                </div>
                                <div class="col-sm-3" style="padding-left: 40px;">
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
