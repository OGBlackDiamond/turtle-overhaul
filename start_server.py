from argparse import ArgumentParser

from mcp import Master_Control_Program
from server import Server
from worlds.json_manager import Json_Manager

# defines argument parser
parser = ArgumentParser(
    prog="Turtle Overhaul",
    description="A websocket controller for computercraft turtles",
)

# gets 3 coordinate points from the user
parser.add_argument(
    "-c",
    "--coordinates",
    type=int,
    nargs=3,
    default=[0, 0, 0],
    help="The 3 coordinate points the first turtle will start at.",
)

# allows the user to define a new world
parser.add_argument(
    "-w",
    "--world",
    type=str,
    default="world",
    help="The world name to create or load in.",
)

# parse arguments
args = parser.parse_args()

# creates a new server with json manager and mcp
server = Server(
    json_manager=Json_Manager(args.world), mcp=Master_Control_Program(args.coordinates)
)

# start server
server.main()
