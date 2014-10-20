<h1>sweetpotato</h1><hr /><p><img alt="sweetpotato logo" src="http://static.blackholegate.net/i/cyark.jpeg" /></p><h2>What is it?</h2><hr /><p><code>sweetpotato</code> is a tool for running a Minecraft server from inside a screen session on a GNU/Linux system. It is written in Python, specifically Python 3, but with no external Python dependencies, except for the optional WebUI function.</p><p>It was created as a way to simplify managing a Minecraft server by providing a simple wrapper for common tasks. It knows what your world is and where its files are via command-line options, values set in a configuration file, or a mixture of both!</p><h2>Usage</h2><hr /><h3>Live Backup</h3><p>Run a backup while the server is running. This sends a message to the in-game chat when the backup starts and finishes, then creates a backup of your configured world</p><pre><code>$ sweetpotato -mb 1024 2048 -z xz -s /srv/mc_server -S minecraft -w Larryland -d /srv/backups/minecraft -v 1.8 --backup
</code></pre><pre><code>[live-backup] Running live backup of "Larryland"  ... Done!
</code></pre><p>But the backup will not be ran if the file (named after today's date) already exists:</p><pre><code>$ sweetpotato --backup
</code></pre><pre><code>[live-backup] Running live backup of "Larryland"  ... FATAL: File "/srv/backups/minecraft/2014-10-19_Larryland.tar.gz" already exists!
</code></pre><h3>Create Server</h3><p>Create the configured server_dir, download the server jar for the configured mc_version, then generate a <code>server.properties</code> and agreed-to <code>eula.txt</code> file.</p><pre><code>$ sweetpotato -mb 1024 2048 -z xz -s /srv/mc_server -S minecraft -w Larryland -d /srv/backups/minecraft -v 1.8 --create
</code></pre><pre><code>[create] Creating "Larryland" ...
</code></pre><pre><code>[create] Creating /srv/mc_server ... Done!
</code></pre><pre><code>[create] Downloading minecraft_server.1.8.jar ... Done!
</code></pre><pre><code>[create] Agreeing to the eula ... Done!
</code></pre><pre><code>[create] Generating server.properties ... Done!
</code></pre><pre><code>[create] World "Larryland" has been created!
</code></pre><h3>Generate Conf File</h3><p>Prints a conf file based on passed-in settings to the stdout.</p><pre><code>$ sweetpotato -mb 1024 2048 -z xz -s /srv/mc_server -S minecraft -w Larryland -d /srv/backups/minecraft -v 1.8 --genconf
</code></pre><pre><code># Generated by sweetpotato at Sun Oct 19 22:12:01 2014
</code></pre><pre><code>[Settings]
</code></pre><pre><code>backup_dir: /srv/backups/minecraft
</code></pre><pre><code>screen_name: minecraft
</code></pre><pre><code>z: xz
</code></pre><pre><code>server_dir: /srv/mc_server
</code></pre><pre><code>mc_version: 1.8
</code></pre><pre><code>mem_max: 2048
</code></pre><pre><code>mem_format: MB
</code></pre><pre><code>mem_min: 1024
</code></pre><pre><code>world_name: Larryland
</code></pre><pre><code>port: 25565
</code></pre><p>You can create your own file like this:</p><pre><code>$ sweetpotato -mb 1024 2048 -z xz -s /srv/mc_server -S minecraft -w Larryland -d /srv/backups/minecraft -v 1.8 --genconf &gt; myserver.conf
</code></pre><pre><code>$ sweetpotato --conf myserver.conf --json
</code></pre><pre><code>{
</code></pre><pre><code>    "backup_dir": "/srv/backups/minecraft",
</code></pre><pre><code>    "conf_file": "myserver.conf",
</code></pre><pre><code>    "force": false,
</code></pre><pre><code>    "forge": null,
</code></pre><pre><code>    "level_seed": null,
</code></pre><pre><code>    "mc_version": "1.8",
</code></pre><pre><code>    "mem_format": "MB",
</code></pre><pre><code>    "mem_max": "2048",
</code></pre><pre><code>    "mem_min": "1024",
</code></pre><pre><code>    "running": "false",
</code></pre><pre><code>    "port": "25565",
</code></pre><pre><code>    "screen_name": "minecraft",
</code></pre><pre><code>    "server_dir": "/srv/mc_server",
</code></pre><pre><code>    "world_name": "Larryland",
</code></pre><pre><code>    "z": "xz"
</code></pre><pre><code>}
</code></pre><p>Or set the default configuration file, which allows you to run <code>sweetpotato</code> without any settings arguments at all:</p><pre><code>$ sweetpotato -gb 1 2 -z gz -s /srv/mc_server -w Larryland -d /srv/backups/minecraft -v 1.8 --genconf &gt; $HOME/.config/sweetpotato/sweetpotato.conf
</code></pre><pre><code>$ sweetpotato --json
</code></pre><pre><code>{
</code></pre><pre><code>    "backup_dir": "/srv/backups/minecraft",
</code></pre><pre><code>    "conf_file": null,
</code></pre><pre><code>    "force": false,
</code></pre><pre><code>    "forge": null,
</code></pre><pre><code>    "level_seed": null,
</code></pre><pre><code>    "mc_version": "1.8",
</code></pre><pre><code>    "mem_format": "GB",
</code></pre><pre><code>    "mem_max": "2",
</code></pre><pre><code>    "mem_min": "1",
</code></pre><pre><code>    "port": "25565",
</code></pre><pre><code>    "running": [
</code></pre><pre><code>        "/srv/mc_server",
</code></pre><pre><code>        "/usr/bin/java",
</code></pre><pre><code>        "7341"
</code></pre><pre><code>    ],
</code></pre><pre><code>    "screen_name": "sweetpotato_mc",
</code></pre><pre><code>    "server_dir": "/srv/mc_server",
</code></pre><pre><code>    "world_name": "Larryland",
</code></pre><pre><code>    "z": "gz"
</code></pre><pre><code>}
</code></pre><h3>Offline Backup</h3><p>Ensure that the server is shut down before backing up. Once completed (or errored out) the server will be restarted:</p><pre><code>$ sweetpotato --offline
</code></pre><pre><code>[offline-backup]  Backing up "Larryland" ... starting "Larryland" ... Done!
</code></pre><p>As with the live backup, this will not be ran if the file (named after today's date) already exists:</p><pre><code>sweetpotato --offline
</code></pre><pre><code>[offline-backup]  Stopping "Larryland" ... backing up ... starting "Larryland" ... Done!
</code></pre><pre><code>FATAL: File "/srv/backups/minecraft/2014-10-19_Larryland.tar.gz" already exists!
</code></pre><h3>WebUI</h3><p>At this time, the WebUI is just a stub, but you can fire it up if you have a valid configuration and have bottle.py installed.</p><pre><code>$ sweetpotato --web
</code></pre><pre><code>Bottle v0.12.7 server starting up (using WSGIRefServer())...
</code></pre><pre><code>Listening on http://127.0.0.1:8080/
</code></pre><pre><code>Hit Ctrl-C to quit.
</code></pre><p>As the output says, after launching you can then fire up the WebUI in your favorite browser at http://127.0.0.1:8080/.</p><h2>Mod (Forge) support</h2><hr /><p>TODO</p><h2>Installation</h2><hr /><p>TODO</p>
% include('readme_padding.tpl')
% rebase('base.tpl', title='README.md')