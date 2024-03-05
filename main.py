import server

turtles = []

async def set_turtles(_turtles):
    global turtles
    turtles = _turtles
    

async def main():
    if len(turtles) > 0:
        turtles[0].queue("turtle.turnRight()")
        turtles[0].queue("turtle.turnLeft()")