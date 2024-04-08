from turtle_stuff.turtle import Turtle
import time

# this will handle all logic in the autonomous funciton of the turtle swarm
class Master_Control_Program:

    turtles: list[Turtle]

    world: dict

    def __init__(self):
        self.turtles = []
        self.world = {}

    def add_turtle(self, turtle):

        world_gen = False
        if (len(self.turtles) == 0):
            world_gen = True

        self.turtles.append(turtle)

        if world_gen:
            master = self.turtles[0]
            self.world[f"{master.x}"] = {}
            self.world[f"{master.x}"][f"{master.y}"] = {}
            self.world[f"{master.x}"][f"{master.y}"][f"{master.z}"] = "turtle"


    def main(self):
        if len(self.turtles) > 0:
            self.coaling()


    def coaling(self):
        master = self.turtles[0]

        if master.get_queue_length() == 0:

            if master.y > 56:
                self.dig(master, "down")
                self.move(master, "down", True)

            elif master.y < 56:
                self.dig(master, "up")
                self.move(master, "up", False)

            else:
                # start mining coal
                self.dig(master)
                self.move(master)


    def dig(self, turtle, direction=""):
        turtle.queue_instruction(f"turtle.dig{direction.capitalize()}()")

    def move(self, turtle, direction="forward", is_aware=False):

        if direction == "left":
            turtle.queue_instruction("turtle.turnLeft()")
        elif direction == "right":
            turtle.queue_instruction("turtle.turnRight()")
        else:
            turtle.queue_instruction(f"turtle.{direction}()")


        # loads new unknown block values in where the turtle could potentially detect and assign block values
        self.world[f"{turtle.x - 1}"] = self.world.get(f"{turtle.x - 1}", {f"{turtle.y}": {f"{turtle.z}": "unknown"}})
        self.world[f"{turtle.x + 1}"] = self.world.get(f"{turtle.x + 1}", {f"{turtle.y}": {f"{turtle.z}": "unknown"}})
        self.world[f"{turtle.x}"][f"{turtle.y - 1}"] = self.world[f"{turtle.x}"].get(f"{turtle.y - 1}", {f"{turtle.z}": "unknown"})
        self.world[f"{turtle.x}"][f"{turtle.y + 1}"] = self.world[f"{turtle.x}"].get(f"{turtle.y + 1}", {f"{turtle.z}": "unknown"})
        self.world[f"{turtle.x}"][f"{turtle.y}"][f"{turtle.z - 1}"] = self.world[f"{turtle.x}"][f"{turtle.y}"].get(f"{turtle.z - 1}", "unknown")
        self.world[f"{turtle.x}"][f"{turtle.y}"][f"{turtle.z + 1}"] = self.world[f"{turtle.x}"][f"{turtle.y}"].get(f"{turtle.z + 1}", "unknown")


        # if is_aware:
        #     self.scan(turtle)

    def scan(self, turtle, sides=False):
        # forward
        for i in range(3):

            for j in range(i):
                turtle.queue_instruction("turtle.turnRight()")

            turtle.queue_instruction("turtle.inspect()")
            self.wait()

            data = self.get_block_from_message()

            if turtle.heading == 0:
                self.world[turtle.x][turtle.y][turtle.z - 1] = data
            elif turtle.heading == 1:
                self.world[turtle.x + 1][turtle.y][turtle.z] = data
            elif turtle.heading == 2:
                self.world[turtle.x][turtle.y][turtle.z + 1] = data
            elif turtle.heading == 3:
                self.world[turtle.x - 1][turtle.y][turtle.z] = data

        turtle.queue_instruction("turtle.turnRight()")

        turtle.queue_instruction("turtle.inspectUp()")
        self.wait()
        self.world[turtle.x][turtle.y + 1][turtle.z] = self.get_block_from_message()

        turtle.queue_instruction("turtle.inspectDown()")
        self.wait()
        self.world[turtle.x][turtle.y - 1][turtle.z] = self.get_block_from_message()

    def get_block_from_message(self, turtle, index=0):
        msg = turtle.get_message(index)
        if msg.status:
            data = msg.data
        else:
            data = "minecraft:air"

        return data

    def wait(self):
        pass
        #time.sleep(0.5)