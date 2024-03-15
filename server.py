import asyncio
import string
import aioconsole
import websockets.server
from websockets.sync.server import ServerConnection
from turtle_stuff.turtle import Turtle
from turtle_stuff.turt_object import Turt_Object
from turtle_stuff import json_manager
import server_utils


# identifies the port
PORT = 3000

# identifies the hostname
HOST = "rx-78-2"

# sets the trust message that essentially acts as a secondary handshake
TURTLE_MESSAGE = "shake-my-hand-bro"

# handles a new connection
async def handle_connect(websocket: ServerConnection):
    print(f"CONNECTION RECIEVED @ {websocket.remote_address[0]}")

    first_msg = await websocket.recv() # type: ignore

    if first_msg != TURTLE_MESSAGE:
        print("Connection Refused")
        await websocket.send("return print('Connection Refused')") # type: ignore
        await websocket.close() # type: ignore
    else:
        print("Connection Established")
        await websocket.send("return print('Connection Established')") # type: ignore

        turtle_id = await websocket.recv() # type: ignore
        parent_id = await websocket.recv() # type: ignore
        turtle:Turtle = None # type: ignore
        parent:Turt_Object = None # type: ignore

        # a parentID of -1 indicates that this turtle needs to reconnect, and a new turtle class should not be created
        if parent_id == "-1":
            ### HANDLES TURTLE RECONNECTION ###

            # attempt to recconnect the turtle ot it's websocket if it exists
            turtle_obj = server_utils.set_websocket(websocket, turtle_id)

            # if a turtle object doesn't exist, recover it from json
            if turtle_obj == None:
                turtles_json = json_manager.restore_turtles()

                turtle_json = turtles_json[f"turtle{turtle_id}"]

                neo_parent_id = turtle_json["parentID"]

                parent = server_utils.find_turtle(neo_parent_id)

                turtle = Turtle(websocket, parent, turtle_json, True)
                turtle_obj = Turt_Object(turtle, turtle_id, neo_parent_id)
                server_utils.add_turtle(turtle_obj)
            else:
                turtle = turtle_obj.turtle
        else:

            ### HANDLES INITIAL TURTLE CONNECTION ###

            parent_obj = server_utils.find_turtle(parent_id)

            if parent_obj != None:
                parent = parent_obj.turtle

            turtle = Turtle(websocket, parent)
            server_utils.add_turtle(Turt_Object(turtle, turtle_id, parent_id))
            await turtle.set_name()

        while turtle.connected:
            await turtle.main()

    print("CLOSING SOCKET")

# this will get user input asynchronously 
async def get_input():
    while True:
        line = await aioconsole.ainput('->')
        if line == "stop":
            json_manager.dump_turtles(server_utils.get_turtles())
            asyncio.get_event_loop().stop()
        elif line == "save":
            json_manager.dump_turtles(server_utils.get_turtles())
        elif line == "stats":
            print("SERVER STATISTICS")
            print(f"Connected Turtles: {len(server_utils.get_turtles())}")

def main():
    start_server = websockets.server.serve(handle_connect, HOST, PORT, ssl=None, compression=None) # type: ignore
    print("STARTING SERVER")
    asyncio.gather(
        start_server,
        get_input(),
    )

    asyncio.get_event_loop().run_forever()