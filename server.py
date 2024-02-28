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
    print(f"CONNECTION RECIEVED @ {websocket.remote_address[0]}")
    turtleIndex = len(turtles)
    turtles.append(f"Turtle {len(turtles)}")

    print(turtles[turtleIndex])

    first_msg = await websocket.recv()
    await websocket.send("return print('Connection Refused')")
    print(first_msg)
    # if first_msg != TURTLE_MESSAGE:
    #     print("Connection Refused")
    #     await websocket.send("return print('Connection Refused')")
    #     await websocket.close()
    # else:
    #     print("Connection Established")
    #     await websocket.send("return print('Connection Established')")

    while True:
        msg = await websocket.recv()
        if msg == DISCONNECT_MESSAGE:
            break
        await websocket.send("return turtle.turnRight()")

    print("CLOSING SOCKET")

async def main():
    async with websockets.serve(handle_connect, HOST, PORT):
        await asyncio.Future()

print("STARTING SERVER")
asyncio.run(main())