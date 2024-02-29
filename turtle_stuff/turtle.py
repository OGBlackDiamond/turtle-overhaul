# sets the message that will indicate a disconnection 
DISCONNECT_MESSAGE = "END-OF-LINE"

"""
Turtle naming convention:
{type}.{pyramid position}-{number}-{revision}

Type:
    They type of turtle:
    - M: Master - the first turtle, acts like an overlord
    - O: Overlord - controls a subset of other turtles and largley handles incoming resources from the underlings
    - U: Underling - standard worker drone, the first underling a turtle creates should be equipped with the nessecary to clone

    An underling gets promoted to an overlord when it has 3 underlings that have cloned from it
    Only 1 master turtle can exist for any given websocket.
    
Pyramid position:
    The position of the turtle on the pyramid. 
    Example: Master turtle is level 0, because it is the tip. 
    An underling that master creates would be 1, and underling that it creates is 2, and so on.
    
Number:
    A count of how many underlings exist under a particular turtle.
    Example: The first underling a turtle creates will be named "U.X-1-X" The second one it creates would be "U.X-2-X" and so on.
    
Revision:
    This number represents the version of 'startup.lua' that a particular turtle is running.
    
    For example, the Master turtle will proabably be running ver 1.0, while a newly created underling might be running version 2.3


Example names w/ description

"M.0-7-1.0" - The master turtle, with 7 underlings, running version 1.0 of the turtle code.

"O.2-3-1.3" - An overlord turtle, which has 3 turtles above it, 3 underlings, running version 1.3 of the turtle code.

"U.5-1-2.4" - An underling turtle, which has 6 turtles above it, 1 underling, running verision 2.4 of the turtle code.
"""

class Turtle:
    
    def __init__(self, websocket):
        self.websocket = websocket


    def main(self):
        msg = self.recv()
        print(msg)
        if msg == DISCONNECT_MESSAGE:
            return False
        self.send("return turtle.turnRight()")
        return True

    async def send(self, message):
        await self.websocket.send(message)

    async def recv(self):
        return await self.websocket.recv()