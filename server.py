import asyncio
import websockets


# identifies the port
PORT = "3000"

# identifies the hostname
HOST = ""

# sets the trust message that essentially acts as a secondary handshake
TURTLE_MESSAGE = "Shake my hand bro"

# sets the message that will indicate a disconnection 
DISCONNECT_MESSAGE = "END-OF-LINE"

turtles = []

# handles a new connection
async def handle_connect(websocket, path):
    print(f"CONNECTION RECIEVED @ {path}")
    turtleIndex = len(turtles)
    turtles.append(f"Turtle {len(turtles)}")

    print(turtles[turtleIndex])


    connected = True

    first_msg = await websocket.recv()
    if False:
        print("Connection Refused")
        await websocket.send("return print('Connection Refused')")
        await websocket.close()
    else:
        print("Connection Established")
        await websocket.send("return print('Connection Established')")

    while connected:
        msg = await websocket.recv()
        if msg == DISCONNECT_MESSAGE:
            break
        print(websocket.is_client)
        await websocket.send("return turtle.turnRight()")

    print("CLOSING SOCKET")

async def main():
    async with websockets.serve(handle_connect, HOST, PORT):
        await asyncio.Future()

print("STARTING SERVER")
asyncio.run(main())