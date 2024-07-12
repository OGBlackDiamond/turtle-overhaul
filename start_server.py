from argparse import ArgumentParser

from server_control.mcp import Master_Control_Program
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

# allows the user to define the direction of the bounding box
parser.add_argument(
    "-b",
    "--box_direction",
    type=str,
    default='x',
    help="The direction along a coordinate plane (x/z) for which the bounding box will extend."
)

# parse arguments
args = parser.parse_args()

# creates a new server with json manager and mcp
server = Server(
    json_manager=Json_Manager(args.world), mcp=Master_Control_Program(args.coordinates, args.box_direction)
)

# start server
server.main()
