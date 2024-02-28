# sets the message that will indicate a disconnection 
DISCONNECT_MESSAGE = "END-OF-LINE"

"""
Turtle naming convention:
{type}-{number}-{revision}


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