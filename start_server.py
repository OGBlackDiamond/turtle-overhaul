import server
from argparse import ArgumentParser

parser = ArgumentParser(
    prog="Turtle Overhaul",
    description="A websocket controller for computercraft turtles"
)

# gets 3 coordinate points from the user
parser.add_argument("-c", "--coordinates", type=int, nargs=3, default=[0, 0, 0])

args = parser.parse_args()

server.mcp.set_start_coords(args.coordinates)


server.main()
