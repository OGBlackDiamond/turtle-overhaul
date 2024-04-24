from server import Server
from argparse import ArgumentParser
from worlds.json_manager import Json_Manager
from mcp import Master_Control_Program

parser = ArgumentParser(
    prog="Turtle Overhaul",
    description="A websocket controller for computercraft turtles"
)

# gets 3 coordinate points from the user
parser.add_argument("-c", "--coordinates", type=int, nargs=3, default=[0, 0, 0])

# allows the user to define a new world
parser.add_argument("-w", "--world", type=str, default="world")

args = parser.parse_args()

server = Server(
    json_manager=Json_Manager(args.world),
    mcp=Master_Control_Program(args.coordinates)
)

server.main()
