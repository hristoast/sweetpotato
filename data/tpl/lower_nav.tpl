                <ul class="nav nav-pills pull-right">
                    % if path == '/':
                    <li class="active bold"><a href="/"><span class="fa fa-home"></span> Home</a></li>
                    <li><a href="/backup"><span class="fa fa-file-archive-o"></span> Backup</a></li>
                    <li><a href="/server"><span class="fa fa-spin fa-cog"></span> Server Control</a></li>
                    <li><a href="/readme"><span class="fa fa-info-circle"></span> README</a></li>
                    % elif path == '/backup':
                    <li><a href="/"><span class="fa fa-home"></span> Home</a></li>
                    <li class="active bold"><a href="/backup"><span class="fa fa-file-archive-o"></span> Backup</a></li>
                    <li><a href="/server"><span class="fa fa-spin fa-cog"></span> Server Control</a></li>
                    <li><a href="/readme"><span class="fa fa-info-circle"></span> README</a></li>
                    % elif path == '/readme':
                    <li><a href="/"><span class="fa fa-home"></span> Home</a></li>
                    <li><a href="/backup"><span class="fa fa-file-archive-o"></span> Backup</a></li>
                    <li><a href="/server"><span class="fa fa-spin fa-cog"></span> Server Control</a></li>
                    <li class="active bold"><a href="/readme"><span class="fa fa-info-circle"></span> README</a></li>
                    % elif path == '/server':
                    <li><a href="/"><span class="fa fa-home"></span> Home</a></li>
                    <li><a href="/backup"><span class="fa fa-file-archive-o"></span> Backup</a></li>
                    <li class="active bold"><a href="/server"><span class="fa fa-spin fa-cog"></span> Server Control</a></li>
                    <li><a href="/readme"><span class="fa fa-info-circle"></span> README</a></li>
                    % else:
                    <li><a href="/"><span class="fa fa-home"></span> Home</a></li>
                    <li><a href="/backup"><span class="fa fa-file-archive-o"></span> Backup</a></li>
                    <li><a href="/server"><span class="fa fa-spin fa-cog"></span> Server Control</a></li>
                    <li><a href="/readme"><span class="fa fa-info-circle"></span> README</a></li>
                    % end
                </ul>
                <h3 class="text-muted">sweetpotato WebUI v{{__version__}}</h3>
