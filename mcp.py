from turtle_stuff.turtle import Turtle

# this will handle all logic in the autonomous funciton of the turtle swarm
class Master_Control_Program:

    turtles: list[Turtle]

    def __init__(self):
        self.turtles = []

    def set_turtles(self, turtles):
        self.turtles = turtles

    def main(self):
        while len(self.turtles) > 0:
            pass