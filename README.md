# turtle-overhaul

## About
This is a websocket controller script for computercraft turtles. Once the first turtle connects, it will autonomously mine for resources, reproduce, harvest more resources, etc. The websocket can save all data from a session, and reuse it, should it crash or need to be turned off. Turtles can also recconnect and resume autonomous function no matter where it is, as long as the server is online. 

## Usage
Install all dependencies by running `pip install -r requirements.txt`.

This server can save multiple worlds. You would use this if you are running this on multiple minecraft worlds. You can specify what world should be created or used for the particular instance of the server with the `-w` (`--world`) arguemnt. If your input already exists as a world, it will use the data from that world for turtles to reconnect. If it doesn't exist it will create a new instance.

In order for the turtle to be able to accuratley mine for resources, it has to know its coorect x y and z coordinates within the minecraft world. This only needs to be defined for initial startup of a fresh world. After the first turtle connects, all turtles after it will know where they are, based on the first turtle's location. This can be defined with the `-c` (`--coordinates`) argument. This will take 3 integers, 1 for x y and z respectively in that order. 

Examples:
* `python3 start_server.py -w example` -  A world called "example" doesn't exist yet. This will create a new world file with new data called "example". The starting coordinates haven't been specified so it defaults to (x, y, z) = (0, 0, 0).
* `python3 start_server.py -w example1 -c 130 23 54` - A world called "example1 doesn't exist yet. This will create a new world file with data called "example1", and the first turtle that connects will think that it is at (x, y, z) = (130, 23, 54).
* `python3 start_server.py` - This will load (or create) a world called "world" (if no `-w` argument, "world" is passed as default) and the first turtle that connects (if at all) will think it's at (x, y, z) = (0, 0, 0).
