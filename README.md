# sweetpotato
-------------

![sweetpotato logo](http://static.blackholegate.net/i/cyark.jpeg)

## What is it?
----

`sweetpotato` is a tool for running a Minecraft server from inside a screen session on a GNU/Linux system. It is written in Python (for Python 3), but with no external Python dependencies (except for the optional WebUI function).

It was created as a way to simplify managing a Minecraft server by providing a simple wrapper for common tasks. It knows what your world is and where its files are via command-line options, values set in a configuration file, or a mixture of both!

## Installation

With `make` installed and `sudo` access:

 1. Download or `git clone https://github.com/hristoast/sweetpotato.git`
 1. Extract (if downloaded)
 1. `cd sweetpotato`
 1. `sudo make install`

## Uninstallation

With `sudo` access:

 1. `cd` into your git-cloned source directory
 1. `sudo make uninstall`

__OR__

 1. `sudo rm -fr /opt/sweetpotato /usr/bin/sweetpotato`

Which are essentially the same thing.

## Issues

I am sure there may be actual bugs and unintended problems in here, but this section is for known issues relating to design decisions. Things that happen, things `sweetpotato` can or can't do - things like that.

  * `sweetpotato` is very careful in may ways, but it will not keep your settings straight for you. Meaning, you must take care to ensure the directories you configure for backups, servers, and so forth are where you really want these things to be.

  * At present `sweetpotato` has no way of validating the screen you have chosen. This means that if you have two servers running on the same machine, and you give them both the same screen name, `sweetpotato` is not going to be able to do anything about it and unexpected things will happen!

  * The WebUI includes no extra security whatsoever. This is deliberate, any decent HTTP server has a way of providing SSL and authentication functions for you.

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
    webui_port: 8080
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
    $ sweetpotato -c myconf.conf --json
    {
        "backup_dir": "/srv/backups/minecraft",
        "compression": "gz",
        "conf_file": "/home/larry/myconf.conf",
        "forge": null,
        "level_seed": null,
        "mc_version": "1.8.1",
        "mem_format": "GB",
        "mem_max": "1",
        "mem_min": "1",
        "permgen": null,
        "port": "25565",
        "running": false,
        "screen_name": "SweetpotatoWorld",
        "server_dir": "/srv/minecraft/mc_server",
        "webui_port": "8080",
        "world_name": "SweetpotatoWorld"
    }

You can also make your settings the default (so you don't have to pass a conf file or command-line args) by writing them to the default conf file location, which is 
`$HOME/.config/sweetpotato/sweetpotato.conf`:

    $ sweetpotato -d /srv/backups/minecraft -s /srv/minecraft/mc_server -gb 1 1 --seed awesomeseed --genconf > $HOME/.config/sweetpotato/sweetpotato.conf
    $ sweetpotato --json
    {
        "backup_dir": "/srv/backups/minecraft",
        "compression": "gz",
        "conf_file": null,
        "forge": null,
        "level_seed": "awesomeseed",
        "mc_version": "1.8.1",
        "mem_format": "GB",
        "mem_max": "1",
        "mem_min": "1",
        "permgen": null,
        "port": "25565",
        "running": false,
        "screen_name": "SweetpotatoWorld",
        "server_dir": "/srv/minecraft/mc_server",
        "webui_port": "8080",
        "world_name": "SweetpotatoWorld"
    }

### Live Backup

Run a backup while the server is running. This sends a message to the in-game chat when the backup starts and finishes, then creates a backup of your configured world

    $ sweetpotato -d /srv/backups/minecraft -s /srv/minecraft/mc_server -gb 1 1 --backup
    [live-backup] Running live backup of "SweetpotatoWorld"  ... Done!

But the backup will not be ran if the file (named after today's date) already exists:

    $ sweetpotato -d /srv/backups/minecraft -s /srv/minecraft/mc_server -gb 1 1 --backup
    [live-backup] Running live backup of "SweetpotatoWorld"  ... FATAL: File "/srv/backups/minecraft/2014-10-20_SweetpotatoWorld.tar.gz" already exists!

### Offline Backup

Ensure that the server is shut down before backing up. Once completed (or errored out) the server will be restarted:

    $ sweetpotato --offline
    [offline-backup]  Stopping "SweetpotatoWorld" ... backing up ... starting "SweetpotatoWorld" ... Done!

As with the live backup, this will not be ran if the file (named after today's date) already exists:

    $ sweetpotato --offline
    [offline-backup]  Stopping "SweetpotatoWorld" ... backing up ... starting "SweetpotatoWorld" ... Done!
    FATAL: File "/srv/backups/minecraft/2014-10-20_SweetpotatoWorld.tar.gz" already exists!

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

### WebUI

A simple web-based interface for many of the functions offered by `sweetpotato`. By default it binds to port `8080`, but this can be changed with the `--web-port` option or a conf file setting.

    $ sweetpotato --web
    Bottle v0.12.7 server starting up (using WSGIRefServer())...
    Listening on http://127.0.0.1:3434/
    Hit Ctrl-C to quit.

### Forge

`sweetpotato` supports using Forge, and defaults to the latest Recommended 1.7.10 build. You can set a specific Forge version with the `-f` or `--forge` option. The extra `-P` or `--permgen` option is available for Forge, by default it is set to 256MB.

 * Both your Forge version and permgen setting can be stored in a conf file or passed in as arguments.
 * You can use the `-C` or `--create` option to download your Forge jar, just as you would with a vanilla server, however don't expect to be able to run it as you'll be missing external dependencies.

Here is an example conf file for a Forge server, taken from my server:

    ## Generated by sweetpotato at Mon Dec 15 22:29:49 2014
    [Settings]
    mc_version: 1.7.10
    webui_port: 34345
    mem_max: 4
    mem_format: GB
    backup_dir: /srv/ftb/backups
    screen_name: llx
    permgen: 256
    compression: gz
    server_dir: /srv/ftb/LLX
    mem_min: 3
    world_name: LarrylandX
    forge: 1.7.10-10.13.2.1230

## ETC

  * [http://hristoast.github.io/sweetpotato](http://hristoast.github.io/sweetpotato)
  * [https://github.com/hristoast/sweetpotato](https://github.com/hristoast/sweetpotato)
  
  _Thanks for reading!_
