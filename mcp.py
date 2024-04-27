from turtle_stuff.turtle import Turtle
from websockets.sync.server import ServerConnection

# this will handle all logic in the autonomous funciton of the turtle swarm
class Master_Control_Program:

    turtles: list[Turtle]

    starting_coords: list[int]

    world: dict

    # initializes with the origional coordinates that the turtle will spawn at
    def __init__(self, starting_coords: list):
        self.turtles = []
        self.world = {}
        self.starting_coords = starting_coords

    # for now, this just continues to generate the world around the turtles
    def main(self):
        for turtle in self.turtles:
            self.gen_world(turtle)

    # returns the block at the given x y z coordinates
    def get_block(self, x:int, y:int, z:int) -> str:
        try:
            return self.world[f"{x}"][f"{y}"][f"{z}"]
        except KeyError:
            print("[ERROR] Requested world block does not exist yet.")
            return "unknown"

    # sets the block's value at the given x y z coordinates
    def set_block(self, x: int, y: int, z: int, value: str):
        try:
            self.world[f"{x}"][f"{y}"][f"{z}"] = value
        except KeyError:
            print("[ERROR] World block does not exist yet.")

    def gen_world(self, turtle: Turtle):
        # loads new unknown block values in where the turtle could potentially detect and assign block values
        self.world[f"{turtle.x}"] = self.world.get(f"{turtle.x}", {f"{turtle.y}": {f"{turtle.z}": "computercraft:turtle_normal"}})

        self.world[f"{turtle.x - 1}"] = self.world.get(f"{turtle.x - 1}", {f"{turtle.y}": {f"{turtle.z}": "unknown"}})
        self.world[f"{turtle.x + 1}"] = self.world.get(f"{turtle.x + 1}", {f"{turtle.y}": {f"{turtle.z}": "unknown"}})

        self.world[f"{turtle.x}"][f"{turtle.y - 1}"] = self.world[f"{turtle.x}"].get(f"{turtle.y - 1}", {f"{turtle.z}": "unknown"})
        self.world[f"{turtle.x}"][f"{turtle.y + 1}"] = self.world[f"{turtle.x}"].get(f"{turtle.y + 1}", {f"{turtle.z}": "unknown"})

        self.world[f"{turtle.x - 1}"][f"{turtle.y - 1}"] = self.world[f"{turtle.x - 1}"].get(f"{turtle.y - 1}", {f"{turtle.z}": "unknown"})
        self.world[f"{turtle.x - 1}"][f"{turtle.y + 1}"] = self.world[f"{turtle.x - 1}"].get(f"{turtle.y + 1}", {f"{turtle.z}": "unknown"})
        self.world[f"{turtle.x + 1}"][f"{turtle.y - 1}"] = self.world[f"{turtle.x + 1}"].get(f"{turtle.y - 1}", {f"{turtle.z}": "unknown"})
        self.world[f"{turtle.x + 1}"][f"{turtle.y + 1}"] = self.world[f"{turtle.x + 1}"].get(f"{turtle.y + 1}", {f"{turtle.z}": "unknown"})

        self.world[f"{turtle.x}"][f"{turtle.y}"][f"{turtle.z - 1}"] = self.world[f"{turtle.x}"][f"{turtle.y}"].get(f"{turtle.z - 1}", "unknown")
        self.world[f"{turtle.x}"][f"{turtle.y}"][f"{turtle.z + 1}"] = self.world[f"{turtle.x}"][f"{turtle.y}"].get(f"{turtle.z + 1}", "unknown")

        self.world[f"{turtle.x + 1}"][f"{turtle.y + 1}"][f"{turtle.z - 1}"] = self.world[f"{turtle.x + 1}"][f"{turtle.y + 1}"].get(f"{turtle.z - 1}", "unknown")
        self.world[f"{turtle.x + 1}"][f"{turtle.y + 1}"][f"{turtle.z + 1}"] = self.world[f"{turtle.x + 1}"][f"{turtle.y + 1}"].get(f"{turtle.z + 1}", "unknown")
        self.world[f"{turtle.x - 1}"][f"{turtle.y + 1}"][f"{turtle.z - 1}"] = self.world[f"{turtle.x - 1}"][f"{turtle.y + 1}"].get(f"{turtle.z - 1}", "unknown")
        self.world[f"{turtle.x - 1}"][f"{turtle.y + 1}"][f"{turtle.z + 1}"] = self.world[f"{turtle.x - 1}"][f"{turtle.y + 1}"].get(f"{turtle.z + 1}", "unknown")

        self.world[f"{turtle.x + 1}"][f"{turtle.y - 1}"][f"{turtle.z - 1}"] = self.world[f"{turtle.x + 1}"][f"{turtle.y - 1}"].get(f"{turtle.z - 1}", "unknown")
        self.world[f"{turtle.x + 1}"][f"{turtle.y - 1}"][f"{turtle.z + 1}"] = self.world[f"{turtle.x + 1}"][f"{turtle.y - 1}"].get(f"{turtle.z + 1}", "unknown")
        self.world[f"{turtle.x - 1}"][f"{turtle.y - 1}"][f"{turtle.z - 1}"] = self.world[f"{turtle.x - 1}"][f"{turtle.y - 1}"].get(f"{turtle.z - 1}", "unknown")
        self.world[f"{turtle.x - 1}"][f"{turtle.y - 1}"][f"{turtle.z + 1}"] = self.world[f"{turtle.x - 1}"][f"{turtle.y - 1}"].get(f"{turtle.z + 1}", "unknown")

    # adds a turtle to the array
    def add_turtle(self, turtle: Turtle):
        self.turtles.append(turtle)

    # returns the array of turtles
    def get_turtles(self) -> list[Turtle]:
        return self.turtles

    # returns the world
    def get_world(self) -> dict:
        return self.world

    # returns a turtle with the given id
    def find_turtle(self, id: int) -> Turtle:
        # loops through the list of turtles
        for turtle in self.turtles:
            # returns the turtle that matches the id
            if turtle.gameID == id:
                return turtle

        return None # type: ignore

    # sets the websocket class to the turtle at the given id
    def set_websocket(self, websocket: ServerConnection, id: int) -> Turtle:
        for i in range(0, len(self.turtles)):
            if self.turtles[i].gameID == id:
                self.turtles[i].websocket = websocket
                return self.turtles[i]

        return None # type: ignore

    # returns the starting coords
    def get_start_coords(self) -> list[int]:
        return self.starting_coords

    # sets the starting coordinates for the master turtle
    def set_start_coords(self, coords: list[int]):
        self.starting_coords = coords

    # sets the world, this should only be used in construction.
    def set_world(self, world:dict):
        self.world = world