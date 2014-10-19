# sweetpotato
-------------

![sweetpotato logo](http://static.blackholegate.net/i/cyark.jpeg)

## What is it?
--------------

`sweetpotato` is a tool for running a Minecraft server from inside a screen session on a GNU/Linux system. It is written in Python, specifically Python 3.

It was created as a way to simplify managing a Minecraft server by providing a simple wrapper for common tasks.

* Create a compressed tar backup of your server files
    * Online: while the server is running
    * Offline: stop, back up, then restart the server
* Start the server
* Restart it
* And stop it

It knows what your world is and where its files are via command-line options, values set in a configuration file, or a mixture of both!

`sweetpotato` is also able to take your passed-in command line arguments and output them into `.conf` file or `json` format for your convenience.

### What works?

As of right now, `sweetpotato` is still in beta and does not yet fully function.

_Features that do __(should)__ work:_

  * All configuration parsing
    1. Default conf file
    1. Passed-in conf file
    1. CLI arguments
  * Server creation, including
    * Creation of configured server directory
    * Downloading of the server jar for the configured mc version
    * Generation of `server.properties` based on desired configurations

## Configuration file
----

TODO

### Generating a conf file

TODO

## Mod (Forge) support
----

TODO

## Web UI
----

TODO

## Installation
----

TODO
