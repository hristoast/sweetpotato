# sweetpotato
-------------

![sweetpotato logo](http://static.blackholegate.net/i/cyark.jpeg)

## What is it?
----

`su - mcuser`

`screen -x mcserver`

`stop`

`java -Xms1G -Xmx2G -jar forge-1.7.10-10.13.4.1558-1.7.10-universal.jar nogui`

The above might be pretty close to the normal commands you'd use to restart a Minecraft server 'by hand'.

But what if you could do it with just one command, like this: `sweetpotato -r`

`sweetpotato` is a tool for running a Minecraft server from inside a screen session on a GNU/Linux system. It is written in Python (for Python 3), but with no external Python dependencies.

It was created as a way to simplify managing a Minecraft server by providing a simple wrapper for common tasks. It knows what your world is and where its files are via command-line options, values set in a configuration file, or a mixture of both!

Oh yeah - you need **Python 3**!

## Installation

With `make` installed and `sudo` access:

 1. [Download](https://github.com/hristoast/sweetpotato/tarball/dev) or `git clone https://github.com/hristoast/sweetpotato.git`
 1. Extract (if downloaded)
 1. `cd sweetpotato`
 1. `make install` (use `sudo` as needed)

## Re-installation

Simply do the installation process again.

## Getting Started
----

Let's set up a server at `/home/hristos/minecraft` and configure it to back up to `/home/hristos/backups`. We'll also set a custom port and level seed too.

    $ sweetpotato --server-dir /home/hristos/minecraft --backup-dir /home/hristos/backups --port 25566 --level-seed AwesomeSeedYo -GB 1 2 --json
    FATAL: The configured directory "/home/hristos/backups" does not exist. Do you need to run --create?

Not to worry, as the message suggests we will run the create command:

    $ sweetpotato --server-dir /home/hristos/minecraft --backup-dir /home/hristos/backups --port 25566 --level-seed AwesomeSeedYo -GB 1 2 --create
    [create] Creating "SweetpotatoWorld" ...
    [create] Creating /home/hristos/backups ... Done!
    [create] Creating /home/hristos/minecraft ... Done!
    [create] Downloading minecraft_server.1.8.1.jar ... Done!
    [create] Agreeing to the eula ... Done!
    [create] Generating server.properties ... Done!
    [create] World "SweetpotatoWorld" has been created!

Now we've got a server that we can use, but it is a little annoying to pass all of these options each time. Let's capture our configuration in a file that we can read from:

    $ sweetpotato --server-dir /home/hristos/minecraft --backup-dir /home/hristos/backups --port 25566 --level-seed AwesomeSeedYo -GB 1 2 --genconf > sweetpotato.conf

Just use the `-c` or `--conf` option to configure `sweetpotato`:

    $ sweetpotato --conf sweetpotato.conf --json --fancy
    {
        "backup_dir": "/home/hristos/backups",
        "compression": "gz",
        "conf_file": "/home/hristos/sweetpotato.conf",
        "forge": null,
        "level_seed": "AwesomeSeedYo",
        "mc_version": "1.8.1",
        "mem_format": "GB",
        "mem_max": "2",
        "mem_min": "1",
        "port": "25566",
        "running": false,
        "screen_name": "SweetpotatoWorld",
        "server_dir": "/home/hristos/minecraft",
        "world_name": "SweetpotatoWorld"
    }

That's better, but we could save even more keystrokes if we wanted to by putting our conf file into the default location as expected by `sweetpotato`, which is `$HOME/.config/sweetpotato/sweetpotato.conf`:

    $ mv sweetpotato.conf ~/.config/sweetpotato/
    $ sweetpotato --start
    [start] Starting "SweetpotatoWorld" ... Done!

Success! Using explicit conf files makes managing multiple servers under one user much easier, but if you are only running one server using the default conf file makes the most sense.

Keep in mind that with the above configuration, the world and screen names are generated from default values.

Or, you can set up a cron job to run a live backup every day at a set time (or other fun things):

    $ crontab -l
    # m h  dom mon dow   command
    @reboot (sleep 30s && sweetpotato --start)
    45 23 * * * sweetpotato --backup
    00 12 * * * sweetpotato --say "`ddate`"

## Usage
----

### Create Server

Create the configured server_dir, download the server jar for the configured mc_version, then generate a `server.properties` and agreed-to `eula.txt` file.

    $ sweetpotato -d /srv/backups/minecraft -s /srv/minecraft/mc_server -gb 1 1 --create
    [create] Creating "SweetpotatoWorld" ...
    [create] Creating /srv/backups/minecraft ... Done!
    [create] Creating /srv/minecraft/mc_server ... Done!
    [create] Downloading minecraft_server.1.8.jar ... Done!
    [create] Agreeing to the eula ... Done!
    [create] Generating server.properties ... Done!
    [create] World "SweetpotatoWorld" has been created!

If you change a setting, like port number, the necessary files are regenerated

    $ sweetpotato -d /srv/backups/minecraft -s /srv/minecraft/mc_server -gb 1 1 --port 25569 --create
    [create] Creating "SweetpotatoWorld" ...
    [create] Found /srv/backups/minecraft!
    [create] Found /srv/minecraft/mc_server!
    [create] Found minecraft_server.1.8.jar!
    [create] Eula agreed to!
    [create] Generating server.properties ... Done!
    [create] World "SweetpotatoWorld" has been created!

Beware when changing values! You can end up with a lost screen name, world name, or some other lost thing that I haven't yet ran into or conceived.

Such a scenario will produce unexpected results - you have been warned to keep track of your configs!

### Generating A Conf File

It is possible to print a conf file based on passed-in settings to the stdout:

    $ sweetpotato -d /srv/backups/minecraft -s /srv/minecraft/mc_server -gb 1 1 --genconf
    ## Generated by sweetpotato at Mon Dec 15 22:32:39 2014
    [Settings]
    mem_max: 1
    mem_format: GB
    mc_version: 1.8.1
    mem_min: 1
    backup_dir: /srv/backups/minecraft
    compression: gz
    world_name: SweetpotatoWorld
    screen_name: SweetpotatoWorld
    port: 25565
    server_dir: /srv/minecraft/mc_server

You can create your own file like this:

    $ sweetpotato -d /srv/backups/minecraft -s /srv/minecraft/mc_server -gb 1 1 --genconf > myconf.conf
    $ sweetpotato -c myconf.conf -j -x
    {
        "backup_dir": "/srv/backups/minecraft",
        "compression": "gz",
        "conf_file": "/home/larry/myconf.conf",
        "level_seed": null,
        "mc_version": "1.8.1",
        "mem_format": "GB",
        "mem_max": "1",
        "mem_min": "1",
        "port": "25565",
        "running": false,
        "screen_name": "SweetpotatoWorld",
        "server_dir": "/srv/minecraft/mc_server",
        "world_name": "SweetpotatoWorld"
    }

You can also make your settings the default (so you don't have to pass a conf file or command-line args) by writing them to the default conf file location, which is 
`$HOME/.config/sweetpotato/sweetpotato.conf`:

    $ sweetpotato -d /srv/backups/minecraft -s /srv/minecraft/mc_server -gb 1 1 --seed awesomeseed --genconf > $HOME/.config/sweetpotato/sweetpotato.conf
    $ sweetpotato -j
    {"screen_name": "SweetpotatoWorld", "compression": "gz", "conf_file": "/home/larry/.config/sweetpotato/sweetpotato.conf", "mem_min": "1", "server_dir": "/srv/minecraft/mc_server", "world_name": "SweetpotatoWorld", "mem_format": "GB", "level_seed": "awesomeseed", "mc_version": "1.8.1", "port": "25565", "backup_dir": "/srv/backups/minecraft", "running": false, "mem_max": "2"}

### List players

Show the console output  of `list` if any players are logged in:

    [list] [13:00:28] [Server thread/INFO]: There are 1/20 players online:
    [list] [13:00:28] [Server thread/INFO]: georgedubya


### Live Backup

Run a backup while the server is running. This sends a message to the in-game chat when the backup starts and finishes, then creates a backup of your configured world

    $ sweetpotato -d /srv/backups/minecraft -s /srv/minecraft/mc_server -gb 1 1 -b
    [live-backup] Running live backup of "SweetpotatoWorld"  ... Done!

But the backup will not be ran if the file (named after today's date) already exists:

    $ sweetpotato -d /srv/backups/minecraft -s /srv/minecraft/mc_server -gb 1 1 -b
    [live-backup] Running live backup of "SweetpotatoWorld"  ... FATAL: File "/srv/backups/minecraft/2014-10-20_SweetpotatoWorld.tar.gz" already exists!

Use the `--force` option to override that.

### Restart

    $ sweetpotato --restart
    [restart] Restarting SweetpotatoWorld ... Done!

If the configured world is not running, is is started.

    $ sweetpotato --restart
    [restart] Starting SweetpotatoWorld ... Done!

### Start

    $ sweetpotato --start
    [start] Starting "SweetpotatoWorld" ... Done!

Fails if the configured world is already running.

    $ sweetpotato --start
    FATAL: World "SweetpotatoWorld" already running with PID 30320

### Stop

    $ sweetpotato --stop
    [stop] Stopping "SweetpotatoWorld" ... Done!

Fails if the configured world is not running.

    $ sweetpotato --stop
    FATAL: Cannot stop "SweetpotatoWorld" - it is not running!
    
### Uptime

See your server's uptime if it's running:

    $ sweetpotato --uptime
    LarrylandX has been up for 0 days, 5 hours, 23 minutes, and 40 seconds

### Forge

`sweetpotato` supports using Forge. You can set a specific Forge version with the `-f` or `--forge` option.

 * Your Forge version can be stored in a conf file or passed in as arguments.
 * You can use the `-C` or `--create` option to download your Forge jar, just as you would with a vanilla server, however don't expect to be able to run it as you'll be missing external dependencies.

Here is an example conf file for a Forge server, taken from my server:

    ## Generated by sweetpotato at Mon Dec 15 22:29:49 2014
    [Settings]
    mc_version: 1.7.10
    mem_max: 4
    mem_format: GB
    backup_dir: /srv/ftb/backups
    screen_name: llx
    compression: gz
    server_dir: /srv/ftb/LLX
    mem_min: 3
    world_name: LarrylandX
    forge: 1.7.10-10.13.4.1558-1.7.10

## ETC

  * [http://hristoast.github.io/sweetpotato](http://hristoast.github.io/sweetpotato)
  * [https://github.com/hristoast/sweetpotato](https://github.com/hristoast/sweetpotato)
  
  _Thanks for reading!_
