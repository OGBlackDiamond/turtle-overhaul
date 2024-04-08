from websockets.sync.server import ServerConnection
from turtle_stuff.turtle import Turtle
turtles = []

# adds a turtle to the array
def add_turtle(turtle: Turtle):
    global turtles
    turtles.append(turtle)

# returns the array of turtles
def get_turtles() -> list[Turtle]:
    return turtles

# returns a turtle with the given id
def find_turtle(id: int) -> Turtle:
    # loops through the list of turtles
    for turtle in turtles:
        # returns the turtle that matches the id
        if turtle.gameID == id:
            return turtle

    return None # type: ignore

def set_websocket(websocket: ServerConnection, id: int) -> Turtle:
    for i in range(0, len(turtles)):
        if turtles[i].gameID == id:
            turtles[i].websocket = websocket
            return turtles[i]

    return None # type: ignore