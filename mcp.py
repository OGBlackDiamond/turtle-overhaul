from turtle_stuff.turtle import Turtle
import time

# this will handle all logic in the autonomous funciton of the turtle swarm
class Master_Control_Program:

    turtles: list[Turtle]

    world: dict

    def __init__(self):
        self.turtles = []
        self.world = {}

    def main(self):
        for turtle in self.turtles:
            self.gen_world(turtle)

    def get_block(self, x, y, z):
        try:
            return self.world[f"{x}"][f"{y}"][f"{z}"]
        except KeyError:
            print("[ERROR] Requested world block does not exist yet.")
            return "unknown"


    def gen_world(self, turtle):
        # loads new unknown block values in where the turtle could potentially detect and assign block values
        self.world[f"{turtle.x - 1}"] = self.world.get(f"{turtle.x - 1}", {f"{turtle.y}": {f"{turtle.z}": "unknown"}})
        self.world[f"{turtle.x + 1}"] = self.world.get(f"{turtle.x + 1}", {f"{turtle.y}": {f"{turtle.z}": "unknown"}})
        self.world[f"{turtle.x}"][f"{turtle.y - 1}"] = self.world[f"{turtle.x}"].get(f"{turtle.y - 1}", {f"{turtle.z}": "unknown"})
        self.world[f"{turtle.x}"][f"{turtle.y + 1}"] = self.world[f"{turtle.x}"].get(f"{turtle.y + 1}", {f"{turtle.z}": "unknown"})
        self.world[f"{turtle.x}"][f"{turtle.y}"][f"{turtle.z - 1}"] = self.world[f"{turtle.x}"][f"{turtle.y}"].get(f"{turtle.z - 1}", "unknown")
        self.world[f"{turtle.x}"][f"{turtle.y}"][f"{turtle.z + 1}"] = self.world[f"{turtle.x}"][f"{turtle.y}"].get(f"{turtle.z + 1}", "unknown")

    def add_turtle(self, turtle):
        self.turtles.append(turtle)
