from websockets.sync.server import ServerConnection
from mcp import Master_Control_Program
from turtle_stuff.turt_object import Turt_Object
turtles = []

master_control_program = Master_Control_Program()

def add_turtle(turtle: Turt_Object):
    global turtles
    turtles.append(turtle)
    master_control_program.set_turtles(turtles)

# returns the array of turtles
def get_turtles():
    return turtles

# returns a turtle with the given id
def find_turtle(id: int) -> Turt_Object:
    # loops through the list of turtles
    for turtle in turtles:
        # returns the turtle that matches the id
        if turtle.gameID == id:
            return turtle

    return None # type: ignore

def set_websocket(websocket: ServerConnection, id: int):
    for i in range(0, len(turtles)):
        if turtles[i].gameID == id:
            turtles[i].turtle.websocket = websocket
            return turtles[i]

    return None