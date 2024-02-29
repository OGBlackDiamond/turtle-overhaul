import server

turtles = []

async def setTurtles(_turtles):
    global turtles
    turtles = _turtles

    
    
async def say():
    await turtles[0].turtle.send("return print('ea sports its in the game')")