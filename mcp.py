# this is the master contol program
# it will handle all logic in the autonomous funciton of the turtle swarm
class Master_Control_Program:

    def __init__(self):
        self.turtles = []

    def set_turtles(self, turtles):
        self.turtles = turtles

    def main(self):
        while len(self.turtles) > 0:
            pass