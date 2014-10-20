# sweetpotato
-------------

![sweetpotato logo](http://static.blackholegate.net/i/cyark.jpeg)

## What is it?
----

`sweetpotato` is a tool for running a Minecraft server from inside a screen session on a GNU/Linux system. It is written in Python, specifically Python 3, but with no external Python dependencies, except for the optional WebUI function.

It was created as a way to simplify managing a Minecraft server by providing a simple wrapper for common tasks. It knows what your world is and where its files are via command-line options, values set in a configuration file, or a mixture of both!

## Usage
----

### Live Backup

Run a backup while the server is running. This sends a message to the in-game chat when the backup starts and finishes, then creates a backup of your configured world

    $ sweetpotato -mb 1024 2048 -z xz -s /srv/mc_server -S minecraft -w Larryland -d /srv/backups/minecraft -v 1.8 --backup
    [live-backup] Running live backup of "Larryland"  ... Done!

But the backup will not be ran if the file (named after today's date) already exists:

    $ sweetpotato --backup
    [live-backup] Running live backup of "Larryland"  ... FATAL: File "/srv/backups/minecraft/2014-10-19_Larryland.tar.gz" already exists!

### Create Server

Create the configured server_dir, download the server jar for the configured mc_version, then generate a `server.properties` and agreed-to `eula.txt` file.

    $ sweetpotato -mb 1024 2048 -z xz -s /srv/mc_server -S minecraft -w Larryland -d /srv/backups/minecraft -v 1.8 --create
    [create] Creating "Larryland" ...
    [create] Creating /srv/mc_server ... Done!
    [create] Downloading minecraft_server.1.8.jar ... Done!
    [create] Agreeing to the eula ... Done!
    [create] Generating server.properties ... Done!
    [create] World "Larryland" has been created!

### Generate Conf File

Prints a conf file based on passed-in settings to the stdout.

    $ sweetpotato -mb 1024 2048 -z xz -s /srv/mc_server -S minecraft -w Larryland -d /srv/backups/minecraft -v 1.8 --genconf
    # Generated by sweetpotato at Sun Oct 19 22:12:01 2014
    [Settings]
    backup_dir: /srv/backups/minecraft
    screen_name: minecraft
    z: xz
    server_dir: /srv/mc_server
    mc_version: 1.8
    mem_max: 2048
    mem_format: MB
    mem_min: 1024
    world_name: Larryland
    port: 25565

You can create your own file like this:

    $ sweetpotato -mb 1024 2048 -z xz -s /srv/mc_server -S minecraft -w Larryland -d /srv/backups/minecraft -v 1.8 --genconf > myserver.conf
    $ sweetpotato --conf myserver.conf --json
    {
        "backup_dir": "/srv/backups/minecraft",
        "conf_file": "myserver.conf",
        "force": false,
        "forge": null,
        "level_seed": null,
        "mc_version": "1.8",
        "mem_format": "MB",
        "mem_max": "2048",
        "mem_min": "1024",
        "port": "25565",
        "screen_name": "minecraft",
        "server_dir": "/srv/mc_server",
        "world_name": "Larryland",
        "z": "xz"
    }

Or set the default configuration file, which allows you to run `sweetpotato` without any settings arguments at all:

    $ sweetpotato -gb 1 2 -z gz -s /srv/mc_server -w Larryland -d /srv/backups/minecraft -v 1.8 --genconf > $HOME/.config/sweetpotato/sweetpotato.conf
    $ sweetpotato --json
    {
        "backup_dir": "/srv/backups/minecraft",
        "conf_file": null,
        "force": false,
        "forge": null,
        "level_seed": null,
        "mc_version": "1.8",
        "mem_format": "GB",
        "mem_max": "2",
        "mem_min": "1",
        "port": "25565",
        "screen_name": "sweetpotato_mc",
        "server_dir": "/srv/mc_server",
        "world_name": "Larryland",
        "z": "gz"
    }

### Offline Backup

Ensure that the server is shut down before backing up. Once completed (or errored out) the server will be restarted:

    $ sweetpotato --offline
    [offline-backup]  Backing up "Larryland" ... starting "Larryland" ... Done!

As with the live backup, this will not be ran if the file (named after today's date) already exists:

    sweetpotato --offline
    [offline-backup]  Stopping "Larryland" ... backing up ... starting "Larryland" ... Done!
    FATAL: File "/srv/backups/minecraft/2014-10-19_Larryland.tar.gz" already exists!

### WebUI

At this time, the WebUI is just a stub, but you can fire it up if you have a valid configuration and have bottle.py installed.

    $ sweetpotato --web
    Bottle v0.12.7 server starting up (using WSGIRefServer())...
    Listening on http://127.0.0.1:8080/
    Hit Ctrl-C to quit.

As the output says, after launching you can then fire up the WebUI in your favorite browser at http://127.0.0.1:8080/.

## Mod (Forge) support
----

TODO

## Installation
----

TODO
