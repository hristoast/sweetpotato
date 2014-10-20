                <ul class="nav nav-pills pull-right">
                    % if path == '/':
                    <li class="active"><a href="/">Home</a></li>
                    <li><a href="/backup">Backup</a></li>
                    <li><a href="/json">JSON</a></li>
                    <li><a href="/readme">README</a></li>
                    <li><a href="/server">Server Control</a></li>
                    % elif path == '/backup':
                    <li><a href="/">Home</a></li>
                    <li class="active"><a href="/backup">Backup</a></li>
                    <li><a href="/json">JSON</a></li>
                    <li><a href="/readme">README</a></li>
                    <li><a href="/server">Server Control</a></li>
                    % elif path == '/readme':
                    <li><a href="/">Home</a></li>
                    <li><a href="/backup">Backup</a></li>
                    <li><a href="/json">JSON</a></li>
                    <li class="active"><a href="/readme">README</a></li>
                    <li><a href="/server">Server Control</a></li>
                    % elif path == '/server':
                    <li><a href="/">Home</a></li>
                    <li><a href="/backup">Backup</a></li>
                    <li><a href="/json">JSON</a></li>
                    <li><a href="/readme">README</a></li>
                    <li class="active"><a href="/server">Server Control</a></li>
                    % else:
                    <li><a href="/">Home</a></li>
                    <li><a href="/readme">README</a></li>
                    <li><a href="/backup">Backup</a></li>
                    <li><a href="/json">JSON</a></li>
                    <li><a href="/server">Server Control</a></li>
                    % end
                </ul>
                <h3 class="text-muted">sweetpotato WebUI</h3>