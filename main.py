import server

turtles = []

async def setTurtles(_turtles):
    turtles = _turtles
    
    await turtles[0].turtle.send("return print('ea sports its in the game')")