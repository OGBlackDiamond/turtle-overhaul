import mcp
from mcp import Master_Control_Program
turtles = []

master_control_program = Master_Control_Program()

def add_turtle(turtle):
    global turtles
    turtles.append(turtle)
    master_control_program.set_turtles(turtles)

# returns 
def get_turtles():
    return turtles

# returns a turtle with the given id
def find_turtle(id):
    # loops through the list of turtles
    for turtle in turtles:
        # returns the turtle that matches the id
        if turtle.gameID == id:
            return turtle

    return None

def set_websocket(websocket, id):
    for i in range(0, len(turtles)):
        if turtles[i].gameID == id:
            turtles[i].turtle.websocket = websocket
            return turtles[i]

    return None