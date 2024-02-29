import asyncio
import websockets
from turtle_stuff.turtle import Turtle
from turtle_stuff.turt_object import Turt_Object


# identifies the port
PORT = "3000"

# identifies the hostname
HOST = "rx-78-2"

# sets the trust message that essentially acts as a secondary handshake
TURTLE_MESSAGE = "Shake my hand bro"

turtles = []
turtle_counter = 0


# handles a new connection
async def handle_connect(websocket, path):
    global turtles, turtle_counter
    print(f"CONNECTION RECIEVED @ {websocket.remote_address[0]}")

    first_msg = await websocket.recv()

    if first_msg != TURTLE_MESSAGE:
        print("Connection Refused")
        await websocket.send("return print('Connection Refused')")
        await websocket.close()
    else:
        print("Connection Established")

        turtle_index = 0
        turtles.append(Turt_Object(Turtle(websocket), turtle_index))
        await websocket.send("return print('Connection Established')")

    while True:
        pass

    turtles.remove(turtle_index)
    print("CLOSING SOCKET")


def main():
    start_server = websockets.serve(handle_connect, HOST, PORT, ssl=None, compression=None)
    print("STARTING SERVER")
    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()
